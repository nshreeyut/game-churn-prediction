# Architecture

Multi-platform player churn prediction platform. Game studios connect their data sources, and a multi-agent AI pipeline scores players, explains predictions, and surfaces insights through a dashboard and conversational agent.

---

## System Overview

```
Data Sources                 Agent Pipeline                  Product
────────────                 ──────────────                  ───────
OpenDota API  ──┐
Steam API     ──┤──→ Schema Agent ──→ Behavioral Features ──┐
               │                                             │
RAWG / Steam  ──┤──→ NLP Agent    ──→ Sentiment Features  ──┤──→ ML Models ──→ Churn Scores
Reviews        │                                             │       │
               │                                             │     SHAP
Studio push  ──┘                                             │   Explainer
(any JSON)                                                   │
                                                             ↓
                                                       Dashboard + Chat Agent
                                                       (FastAPI + React)
```

---

## Layer 1 — Data Ingestion

**Active collectors** (`src/game_churn/collectors/`):
- `opendota.py` — Dota 2 match history, MMR, peer graph (no key required)
- `steam.py` — playtime, recently played, friend list, reviews
- `rawg.py` — game metadata + user review text (feeds NLP only)
- `base.py` — shared HTTP client with retry logic (tenacity)

**Standardization** (`src/game_churn/features/standardize.py`):
Each collector's raw JSON → unified `PlayerActivity` records → same feature engineering regardless of source.

**Studio ingestion** (`api/routers/ingest.py`):
Studios POST any JSON to `/api/v1/ingest/events`. The Schema Agent infers field mapping on first connect; subsequent events are auto-normalized.

---

## Layer 2 — Agent Pipeline

Five agents, each with one job:

| Agent | File | When it runs |
|---|---|---|
| **Schema Agent** | `api/agents/schema_agent.py` | Once at studio onboarding — infers field mapping from sample data |
| **NLP Agent** | `api/agents/nlp_agent.py` | On every review ingest — RoBERTa sentiment + GPT summary |
| **Churn Analyst** | `api/agents/churn_analyst.py` | The conversational agent users talk to — has all other outputs as tools |

Background analysis (churn scoring, SHAP) runs as services, not agents — agents call services as tools.

---

## Layer 3 — ML Engine

`src/game_churn/models/train.py` — trains per-studio models:
- XGBoost, LightGBM, CatBoost, Logistic Regression
- Soft-voting ensemble (default)
- StandardScaler + SHAP values saved alongside models

**Feature set** (18 behavioral signals):
- Recency: `days_since_last_game`
- Frequency: `games_7d / 14d / 30d`, `avg_daily_sessions_*`
- Duration: `playtime_hours_7d / 14d / 30d`
- Trends: `games_trend_7d_vs_14d`, `playtime_trend_*`
- Performance: `win_rate_7d / 30d`, `current_rating`, `rating_change_30d`
- Social: `unique_peers_30d`, `games_with_peers_30d`
- Composite: `engagement_score`, `max_gap_days_30d`

Sentiment features from the NLP agent merge into this table as additional columns.

**Artifacts per studio:**
```
models/{studio_id}/
  ensemble.joblib
  scaler.joblib
  shap_values.joblib
```

---

## Layer 4 — FastAPI Backend

```
api/
  main.py               ← app, CORS, router registration
  config.py             ← all settings + get_llm() factory (Groq / OpenAI switchable)
  middleware/
    auth.py             ← API key → studio_id on every request
  models/
    studio.py           ← Pydantic schemas (Studio, FieldMap)
  routers/
    studios.py          ← register studio, get API key
    ingest.py           ← POST events, POST reviews
    players.py          ← player lookup + analytics
    chat.py             ← streaming chat endpoint
  services/
    studio_service.py   ← studio CRUD
    ingest_service.py   ← normalize any JSON → PlayerActivity
    mapping_service.py  ← apply saved field_map config
    nlp_service.py      ← run NLP pipeline, store sentiment output
    training_service.py ← trigger per-studio feature eng + model train
    data_service.py     ← load studio parquet, query players
    model_service.py    ← load studio model, predict churn
    shap_service.py     ← load studio SHAP, explain player
  agents/
    schema_agent.py     ← onboarding: infer field mapping from sample
    nlp_agent.py        ← sentiment + keyword extraction on review text
    churn_analyst.py    ← conversational agent with tool access to all services
  registry/
    game_registry.py    ← active platforms (OpenDota, Steam)
    model_registry.py   ← registered ML models
```

**LLM configuration** — swap provider via env var, no code changes:
```
LLM_PROVIDER=groq          # or "openai"
LLM_MODEL=llama-3.3-70b-versatile
GROQ_API_KEY=...
```

---

## Layer 5 — React Frontend

```
frontend/src/
  api/
    client.js       ← configured axios instance
    players.js      ← player lookup calls
    chat.js         ← streaming fetch for chat
    studios.js      ← studio registration calls
  hooks/
    usePlayer.js    ← player fetch state
    useChat.js      ← conversation + streaming state
  components/
    PlayerSearch/   ← platform dropdown + ID input
    AnalyticsPanel/ ← churn score, risk badge, key stats
    ShapChart/      ← Recharts horizontal bar (red/green by impact)
    SentimentPanel/ ← review sentiment trend + top complaints
    CohortView/     ← high/medium/low risk segment breakdown
    ChatPanel/      ← streaming conversational agent UI
  pages/
    Home.jsx        ← main dashboard layout
    Onboarding.jsx  ← studio registration + field mapping review
```

---

## Data Paths

```
data/
  01_raw/
    opendota/       ← raw match JSON from OpenDota
    steam/          ← raw player + game JSON from Steam
  studios/
    {studio_id}/
      01_raw/
        events/     ← raw events as received
        reviews/    ← raw review text
      03_features/
        player_features.parquet
        sentiment_features.parquet
      04_predictions/

models/
  {studio_id}/      ← per-studio model artifacts
  *.joblib          ← demo models (synthetic data)
```

---

## Demo Mode

A completely separate layer for sharing with investors and studios before real data is connected.

```
yourapp.vercel.app/demo
        │
        ▼
React loads /demo route → DemoBanner shown (amber, unmissable)
        │
        ▼
All API calls → /api/v1/demo/* (never touches real studio data)
        │
        ▼
demo_service.py → 50 synthetic players, scored by real models, SHAP computed
                  cached in memory after first request
```

| File | Role |
|---|---|
| `api/routers/demo.py` | Endpoints: summary, player list, player detail, streaming chat |
| `api/services/demo_service.py` | Generates + scores + SHAP synthetic players; `lru_cache` |
| `frontend/src/api/demo.js` | All demo fetch calls + streaming chat |
| `frontend/src/components/DemoBanner/` | Amber banner — always visible in demo mode |

**Auth note:** The auth middleware (Phase 2) must explicitly exclude `/api/v1/demo/*`. Demo requires no API key — anyone with the link can access it.

**`train.py` note:** The silent synthetic fallback has been removed. Running `make train` without real data now raises a clear error. Synthetic data is only available through the explicit demo mode, not as a hidden pipeline fallback.

---

## Key Design Decisions

**Groq over OpenAI by default** — free tier, fast inference, reliable tool-calling with `llama-3.3-70b-versatile`. Switch to OpenAI for production by changing `LLM_PROVIDER=openai`.

**Push-based ingestion** — studios POST events to our API rather than us polling theirs. More reliable, no connector maintenance, works for any backend.

**RAWG as review-only source** — RAWG doesn't have player behavioral data, only game metadata and reviews. It feeds the NLP agent exclusively and doesn't appear in the player search flow.

**Services over agents for background work** — churn scoring and SHAP run as cached Python services. Agents only activate when reasoning or LLM judgment is needed (schema inference, NLP summarization, conversation).
