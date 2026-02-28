"""Model training pipeline with MLflow tracking.

Usage: python -m game_churn.models.train
"""

from __future__ import annotations

import logging

import joblib
import mlflow
import numpy as np
import polars as pl
from sklearn.ensemble import VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

from game_churn.models.synthetic import generate_synthetic_data
from game_churn.utils.config import FEATURES_DIR, MLFLOW_DIR, MODELS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

FEATURE_COLS = [
    "games_7d",
    "games_14d",
    "games_30d",
    "playtime_7d_hours",
    "playtime_14d_hours",
    "playtime_30d_hours",
    "avg_daily_sessions_7d",
    "avg_daily_sessions_14d",
    "avg_daily_sessions_30d",
    "max_gap_days_30d",
    "games_trend_7d_vs_14d",
    "playtime_trend_7d_vs_14d",
    "win_rate_7d",
    "win_rate_30d",
    "rating_change_30d",
    "unique_peers_30d",
    "peer_games_30d",
    "engagement_score",
    "days_since_last_game",
]

TARGET_COL = "churned"


def load_features() -> pl.DataFrame:
    """Load feature data from parquet or generate synthetic data."""
    parquet_path = FEATURES_DIR / "player_features.parquet"
    if parquet_path.exists():
        log.info("Loading features from %s", parquet_path)
        return pl.read_parquet(parquet_path)

    log.info("No feature data found, generating synthetic dataset for training...")
    return generate_synthetic_data()


def prepare_data(
    df: pl.DataFrame,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, list[str]]:
    """Prepare train/test splits from feature DataFrame."""
    # Ensure all feature columns exist
    available_cols = [c for c in FEATURE_COLS if c in df.columns]
    log.info("Using %d/%d feature columns", len(available_cols), len(FEATURE_COLS))

    X = df.select(available_cols).fill_null(0).to_numpy()
    y = df[TARGET_COL].cast(pl.Int32).to_numpy()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Scale features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Save scaler
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(scaler, MODELS_DIR / "scaler.joblib")

    return X_train, X_test, y_train, y_test, available_cols


def build_models() -> dict:
    """Build all model instances."""
    from catboost import CatBoostClassifier
    from lightgbm import LGBMClassifier
    from xgboost import XGBClassifier

    models = {
        "logistic_regression": LogisticRegression(
            max_iter=1000, random_state=42, class_weight="balanced"
        ),
        "xgboost": XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            eval_metric="logloss",
            use_label_encoder=False,
        ),
        "lightgbm": LGBMClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            verbose=-1,
        ),
        "catboost": CatBoostClassifier(
            iterations=200,
            depth=6,
            learning_rate=0.1,
            random_seed=42,
            verbose=0,
            train_dir=str(MLFLOW_DIR / "catboost_info"),
        ),
    }
    return models


def evaluate_model(
    model_name: str,
    model: object,
    X_test: np.ndarray,
    y_test: np.ndarray,
) -> dict[str, float]:
    """Evaluate a trained model and return metrics."""
    y_pred = model.predict(X_test)  # type: ignore[union-attr]
    y_proba = model.predict_proba(X_test)[:, 1]  # type: ignore[union-attr]

    metrics = {
        "auc": roc_auc_score(y_test, y_proba),
        "f1": f1_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
    }

    log.info(
        "%s — AUC: %.4f | F1: %.4f | Precision: %.4f | Recall: %.4f",
        model_name,
        metrics["auc"],
        metrics["f1"],
        metrics["precision"],
        metrics["recall"],
    )

    cm = confusion_matrix(y_test, y_pred)
    log.info("%s confusion matrix:\n%s", model_name, cm)
    log.info("%s classification report:\n%s", model_name, classification_report(y_test, y_pred))

    return metrics


def train_and_log(
    models: dict,
    X_train: np.ndarray,
    X_test: np.ndarray,
    y_train: np.ndarray,
    y_test: np.ndarray,
    feature_names: list[str],
) -> dict[str, float]:
    """Train all models with MLflow tracking."""
    MLFLOW_DIR.mkdir(parents=True, exist_ok=True)
    mlflow.set_tracking_uri(f"sqlite:///{MLFLOW_DIR / 'mlflow.db'}")
    mlflow.set_experiment("game-churn-prediction")
    best_auc = 0.0
    best_model_name = ""
    all_metrics: dict[str, float] = {}

    for name, model in models.items():
        with mlflow.start_run(run_name=name):
            log.info("Training %s...", name)
            model.fit(X_train, y_train)

            metrics = evaluate_model(name, model, X_test, y_test)
            all_metrics[name] = metrics["auc"]

            # Log to MLflow
            mlflow.log_params({"model": name, "n_features": len(feature_names)})
            mlflow.log_metrics(metrics)
            mlflow.sklearn.log_model(model, artifact_path="model")

            # Save locally
            model_path = MODELS_DIR / f"{name}.joblib"
            joblib.dump(model, model_path)
            log.info("Saved %s to %s", name, model_path)

            if metrics["auc"] > best_auc:
                best_auc = metrics["auc"]
                best_model_name = name

    # Build soft-voting ensemble from the trained models
    log.info("Building soft-voting ensemble...")
    with mlflow.start_run(run_name="ensemble"):
        ensemble = VotingClassifier(
            estimators=list(models.items()),
            voting="soft",
        )
        # VotingClassifier needs to be fit, but we already have trained estimators
        # Set them directly to avoid retraining
        ensemble.estimators_ = list(models.values())
        le = LabelEncoder()
        le.classes_ = np.array([0, 1])
        ensemble.le_ = le  # type: ignore[attr-defined]
        ensemble.classes_ = np.array([0, 1])

        metrics = evaluate_model("ensemble", ensemble, X_test, y_test)
        all_metrics["ensemble"] = metrics["auc"]
        mlflow.log_params({"model": "ensemble", "n_models": len(models)})
        mlflow.log_metrics(metrics)

        joblib.dump(ensemble, MODELS_DIR / "ensemble.joblib")

        if metrics["auc"] > best_auc:
            best_auc = metrics["auc"]
            best_model_name = "ensemble"

    log.info("Best model: %s (AUC=%.4f)", best_model_name, best_auc)
    return all_metrics


def generate_shap_plots(
    model_name: str,
    X_test: np.ndarray,
    feature_names: list[str],
) -> None:
    """Generate SHAP explainability plots."""
    import shap

    log.info("Generating SHAP plots for %s...", model_name)

    model = joblib.load(MODELS_DIR / f"{model_name}.joblib")

    # Use TreeExplainer for tree models, KernelExplainer for others
    tree_models = {"xgboost", "lightgbm", "catboost"}
    if model_name in tree_models:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_test[:200])
    else:
        explainer = shap.KernelExplainer(model.predict_proba, X_test[:50])  # type: ignore[union-attr]
        shap_values = explainer.shap_values(X_test[:200])

    # Save SHAP values for dashboard
    shap_output = MODELS_DIR / "shap_values.joblib"
    joblib.dump(
        {
            "shap_values": shap_values,
            "feature_names": feature_names,
            "X_sample": X_test[:200],
        },
        shap_output,
    )
    log.info("SHAP values saved to %s", shap_output)


def main() -> None:
    """Run full training pipeline."""
    df = load_features()
    log.info("Dataset: %d rows, %d columns", len(df), len(df.columns))

    X_train, X_test, y_train, y_test, feature_names = prepare_data(df)
    log.info("Train: %d, Test: %d", len(X_train), len(X_test))

    models = build_models()
    train_and_log(models, X_train, X_test, y_train, y_test, feature_names)

    # Generate SHAP for best tree model
    generate_shap_plots("xgboost", X_test, feature_names)

    log.info("Training pipeline complete!")


if __name__ == "__main__":
    main()
