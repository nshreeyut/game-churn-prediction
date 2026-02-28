# Game Churn Prediction

Multi-platform video game player churn prediction using free gaming APIs, modern ML models, a FastAPI backend, and a React frontend with an AI analyst chatbot powered by LangChain.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     React Frontend (Vercel)                      │
│                                                                  │
│   PlayerSearch → AnalyticsPanel + ShapChart │ ChatPanel (AI)    │
│                                                                  │
│   src/api/          src/hooks/         src/components/          │
│   (HTTP layer)      (state logic)      (rendering only)         │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTP / streaming
┌──────────────────────────────▼──────────────────────────────────┐
│                     FastAPI Backend (Render)                     │
│                                                                  │
│   registry/          services/              agents/             │
│   game_registry  →   data_service      →   churn_analyst        │
│   model_registry →   model_service         (LangChain + tools)  │
│                  →   shap_service                               │
└──────────────────────────────┬──────────────────────────────────┘
                               │ reads files
┌──────────────────────────────▼──────────────────────────────────┐
│                      ML Layer (unchanged)                        │
│                                                                  │
│   src/game_churn/collectors/    →  data/01_raw/                 │
│   src/game_churn/features/      →  data/03_features/*.parquet   │
│   src/game_churn/models/        →  models/*.joblib              │
└─────────────────────────────────────────────────────────────────┘
```

## Features

- **Multi-platform data collection** from Chess.com, OpenDota, and Riot Games APIs
- **Engineered features**: time-window activity, engagement trends, social graph, win rates
- **4 ML models + ensemble**: Logistic Regression, XGBoost, LightGBM, CatBoost
- **MLflow experiment tracking** with metric logging and model artifacts
- **SHAP explainability** for model interpretability
- **FastAPI backend** with auto-generated docs, registry-based extensibility
- **React frontend**: Player Lookup with SHAP chart + AI Analyst chatbot
- **LangChain agent** with tools that call real models and real data
- **Extensible by design**: add a new game or model by editing one registry file

## Quick Start

### ML Pipeline (train models first)

```bash
# Install dependencies (requires uv)
make install

# Run the full training pipeline (uses synthetic data if no API data)
make train

# View MLflow experiment results
make mlflow-ui
```

### Backend (FastAPI)

```bash
# Start the API server (visit http://localhost:8000/docs for interactive docs)
uvicorn api.main:app --reload --port 8000
```

### Frontend (React)

```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

## Setup

### Prerequisites

- Python 3.12+ with [uv](https://docs.astral.sh/uv/)
- Node.js 18+

### Installation

```bash
git clone https://github.com/yourusername/game-churn-prediction.git
cd game-churn-prediction
make install       # Python deps
cd frontend && npm install  # JS deps
```

### Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your-openai-key        # required for the AI chatbot
GAME_CHURN_RIOT_API_KEY=your-key      # optional: enables Riot data collection
GAME_CHURN_RAWG_API_KEY=your-key      # optional: enables game metadata
```

For the frontend, create `frontend/.env`:

```env
# Leave empty in development (Vite proxy handles routing)
# Set to your Render URL in production
VITE_API_URL=https://your-api.onrender.com
```

## Usage

### Data Collection

```bash
make collect    # Collect from all configured APIs
make features   # Build feature table from raw data
make train      # Train all models + compute SHAP values
```

### Development

```bash
# Terminal 1 — FastAPI backend
uvicorn api.main:app --reload --port 8000

# Terminal 2 — React frontend
cd frontend && npm run dev
```

### Code Quality

```bash
make lint       # Ruff linter
make format     # Auto-format
make typecheck  # mypy
make test       # pytest
```

## Project Structure

```
game-churn-prediction/
│
├── api/                         ← FastAPI backend
│   ├── main.py                  ← app entry, CORS, router registration
│   ├── config.py                ← settings (paths, API keys, CORS origins)
│   ├── registry/
│   │   ├── game_registry.py     ← add new game platforms here
│   │   └── model_registry.py    ← add new ML models here
│   ├── services/
│   │   ├── data_service.py      ← loads parquet, queries players
│   │   ├── model_service.py     ← loads joblib, runs predictions
│   │   └── shap_service.py      ← loads + formats SHAP values
│   ├── routers/
│   │   ├── players.py           ← GET /players endpoints
│   │   └── chat.py              ← POST /chat (streaming)
│   └── agents/
│       └── churn_analyst.py     ← LangChain agent + 4 tools
│
├── frontend/                    ← Vite + React (plain JS)
│   ├── src/
│   │   ├── api/
│   │   │   ├── client.js        ← configured axios instance
│   │   │   ├── players.js       ← player API functions
│   │   │   └── chat.js          ← streaming chat function
│   │   ├── hooks/
│   │   │   ├── usePlayer.js     ← player fetch + state management
│   │   │   └── useChat.js       ← chat state + streaming
│   │   ├── components/
│   │   │   ├── PlayerSearch/    ← platform dropdown + player ID form
│   │   │   ├── AnalyticsPanel/  ← churn probability, stats, SHAP chart
│   │   │   ├── ShapChart/       ← Recharts horizontal bar chart
│   │   │   └── ChatPanel/       ← chat UI with streaming
│   │   └── pages/
│   │       └── Home.jsx         ← layout, lifted state
│   └── vite.config.js           ← dev proxy → localhost:8000
│
├── src/game_churn/              ← ML library (unchanged)
│   ├── collectors/              ← Chess.com, OpenDota, Riot, RAWG
│   ├── features/                ← standardize, engineer, build
│   ├── models/                  ← train, synthetic data
│   ├── pipelines/               ← Prefect flow
│   └── utils/                   ← config, paths
│
├── data/                        ← DVC-tracked data
│   ├── 01_raw/                  ← raw API responses (JSON)
│   └── 03_features/             ← player_features.parquet
│
├── models/                      ← trained model artifacts
│   ├── ensemble.joblib
│   ├── xgboost.joblib
│   ├── lightgbm.joblib
│   ├── catboost.joblib
│   ├── logistic_regression.joblib
│   ├── scaler.joblib
│   └── shap_values.joblib
│
├── render.yaml                  ← Render deployment config (backend)
├── frontend/vercel.json         ← Vercel SPA routing (frontend)
└── tests/                       ← pytest test suite
```

## Tech Stack

| Category | Tools |
|----------|-------|
| Package Management | uv |
| Data Processing | Polars |
| ML Models | scikit-learn, XGBoost, LightGBM, CatBoost |
| Experiment Tracking | MLflow |
| Explainability | SHAP |
| Backend | FastAPI, uvicorn |
| AI / LLM | LangChain, OpenAI (GPT-4o-mini) |
| Frontend | React, Vite, Recharts, Axios |
| Validation | Pydantic, pydantic-settings |
| Orchestration | Prefect |
| Data Versioning | DVC |
| Code Quality | Ruff, mypy, pytest |
| CI/CD | GitHub Actions |
| Deployment | Vercel (frontend), Render (backend) |

## Extensibility

### Add a new game platform

1. Create `src/game_churn/collectors/your_game.py` (inherit `BaseCollector`)
2. Add a standardizer in `src/game_churn/features/standardize.py`
3. Add one entry to `api/registry/game_registry.py`

The API and frontend update automatically — no other changes needed.

### Add a new ML model

1. Train your model and save: `joblib.dump(model, "models/your_model.joblib")`
2. Add one entry to `api/registry/model_registry.py`

Users can select it from the model picker immediately.

## Deployment

**Backend → Render**
- `render.yaml` configures the build and start commands automatically
- Set `OPENAI_API_KEY` in Render's environment variables dashboard

**Frontend → Vercel**
- Connect your GitHub repo to Vercel, set root directory to `frontend/`
- Set `VITE_API_URL` to your Render service URL in Vercel's environment variables

## License

MIT
