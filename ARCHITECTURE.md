# Game Churn Prediction — Architecture Guide

This document covers the full system: what each layer does, how data flows end to end, how the ML pipeline connects to the API, how the frontend is structured, and how to extend the project.

---

## Table of Contents

1. [The Big Picture](#1-the-big-picture)
2. [ML Layer — The Foundation](#2-ml-layer--the-foundation)
3. [FastAPI Backend](#3-fastapi-backend)
4. [React Frontend](#4-react-frontend)
5. [End-to-End Request Walkthrough](#5-end-to-end-request-walkthrough)
6. [Extensibility Patterns](#6-extensibility-patterns)
7. [Deployment](#7-deployment)
8. [What Data We Pull from Each API](#8-what-data-we-pull-from-each-api)
9. [Tool Choices](#9-tool-choices)

---

## 1. The Big Picture

The project answers one question: **"Is this player about to stop playing?"**

```
[Collect]          [Engineer]          [Train]           [Serve]          [Display]
Gaming APIs   →    Features       →    ML Models    →    FastAPI     →    React App
(Chess.com,        (parquet)           (joblib)          + LangChain      + AI Chat
 OpenDota,
 Riot LoL)
```

The ML pipeline (collect → engineer → train) runs offline and produces artifacts.
The API reads those artifacts to serve predictions.
The React frontend calls the API and presents the results.
The LangChain agent wraps everything in a conversational interface.

---

## 2. ML Layer — The Foundation

This layer is the original project, completely unchanged. It produces the files everything else depends on.

### Pipeline stages

```
src/game_churn/collectors/    →    data/01_raw/             (raw JSON from APIs)
src/game_churn/features/      →    data/03_features/        (player_features.parquet)
src/game_churn/models/        →    models/                  (*.joblib files)
```

Run with: `make collect` → `make features` → `make train`

### Output artifacts

| File | What it contains |
|------|-----------------|
| `data/03_features/player_features.parquet` | One row per player — all engineered features + churn label |
| `models/ensemble.joblib` | Soft-voting ensemble (XGBoost + LightGBM + CatBoost + LogReg) |
| `models/xgboost.joblib` | XGBoost classifier |
| `models/lightgbm.joblib` | LightGBM classifier |
| `models/catboost.joblib` | CatBoost classifier |
| `models/logistic_regression.joblib` | Logistic Regression baseline |
| `models/scaler.joblib` | StandardScaler fitted on training data |
| `models/shap_values.joblib` | Pre-computed SHAP explanations for test-set players |

The API never retrains. It only reads these files.

### Feature engineering summary

For each player, `engineer.py` computes:

| Feature | What it captures |
|---------|-----------------|
| `games_7d / 14d / 30d` | Recent activity volume |
| `playtime_hours_*` | Time investment per window |
| `avg_daily_sessions_*` | Playing frequency |
| `max_gap_days_30d` | Longest break — a key churn signal |
| `games_trend_7d_vs_14d` | Is activity increasing or declining? |
| `win_rate_7d / 30d` | Losing streaks predict churn |
| `rating_change_30d` | Skill progression or frustration |
| `unique_peers_30d` | Social connections — social players churn less |
| `engagement_score` | 0–100 composite of all signals |
| `days_since_last_game` | Most predictive single feature |
| `churned` | **Target variable** — True if inactive 14+ days |

---

## 3. FastAPI Backend

Lives in `api/`. Entry point: `api/main.py`.

### Internal layers

```
api/
├── main.py               ← app creation, CORS middleware, router registration
├── config.py             ← all settings loaded from environment variables
├── registry/             ← extensibility layer (edit to add games/models)
│   ├── game_registry.py
│   └── model_registry.py
├── services/             ← business logic (no HTTP knowledge)
│   ├── data_service.py   ← queries the parquet file
│   ├── model_service.py  ← loads joblib, runs predict_proba()
│   └── shap_service.py   ← loads + formats SHAP values per player
├── routers/              ← HTTP layer (no business logic)
│   ├── players.py        ← GET endpoints
│   └── chat.py           ← POST /chat with streaming
└── agents/
    └── churn_analyst.py  ← LangChain agent with 4 tools
```

### Registry pattern

The two registry files are the **only** files you edit to extend the system.

`game_registry.py` — one dict entry per supported platform:
```python
GAME_REGISTRY = {
    "chess_com": { "display_name": "Chess.com", "requires_api_key": False, ... },
    "opendota":  { ... },
    "riot_lol":  { ... },
    # Add "steam": { ... } here to support Steam
}
```

`model_registry.py` — one dict entry per trained model:
```python
MODEL_REGISTRY = {
    "ensemble":            { "path": "models/ensemble.joblib", ... },
    "xgboost":             { "path": "models/xgboost.joblib",  ... },
    # Add "my_new_model": { "path": "models/my_model.joblib" } here
}
```

Everything downstream (routers, frontend, agent) reads from these dicts. No other files need to change.

### Service layer

Services are pure Python functions — no HTTP, no request/response objects.
This means they can be called from both routers AND the LangChain agent tools without duplication.

```
data_service.get_player(player_id, platform)    → dict | None
model_service.predict_churn(features, model_id) → { churn_probability, risk_level, ... }
shap_service.get_player_shap(player_id, platform) → list[dict] | None
```

Each service uses `@lru_cache` so files are only read from disk once — subsequent calls return the in-memory cached object.

### Endpoints

| Method | Path | What it does |
|--------|------|-------------|
| GET | `/health` | Health check for Render |
| GET | `/api/v1/players/games` | List supported platforms (from game_registry) |
| GET | `/api/v1/players/models` | List registered models (from model_registry) |
| GET | `/api/v1/players` | Browse/search players in the dataset |
| GET | `/api/v1/players/{platform}/{player_id}` | Full analytics for one player |
| POST | `/api/v1/chat` | LangChain agent response (streaming) |

Visit `http://localhost:8000/docs` for interactive documentation (auto-generated by FastAPI).

### LangChain Agent

`agents/churn_analyst.py` defines an agent with four tools:

| Tool | When the LLM calls it | What it does |
|------|-----------------------|-------------|
| `get_player_data` | "What's Player X's risk score?" | Calls `get_player()` + `predict_churn()` |
| `explain_prediction` | "Why is Player X at risk?" | Calls `get_player_shap()`, formats SHAP values as text |
| `get_dataset_context` | "What's the overall churn rate?" | Calls `get_dataset_summary()` |
| `suggest_retention_strategy` | "How do we retain Player X?" | Reads top SHAP risk factors, maps to interventions |

The LLM (GPT-4o-mini) decides which tool to call based on the user's question. Each tool calls the existing service layer — no logic is duplicated.

---

## 4. React Frontend

Lives in `frontend/`. Deployed on Vercel. Built with Vite + React (plain JavaScript).

### Internal layers

```
frontend/src/
├── api/              ← HTTP layer — all fetch/axios calls live here
│   ├── client.js     ← configured axios instance (base URL, interceptors)
│   ├── players.js    ← functions calling /players endpoints
│   └── chat.js       ← streaming function for /chat (uses native fetch)
├── hooks/            ← data/state logic, decoupled from rendering
│   ├── usePlayer.js  ← manages fetch state for a player lookup
│   └── useChat.js    ← manages conversation state + streaming
├── components/       ← rendering only, receive data via props
│   ├── PlayerSearch/ ← platform dropdown + player ID form
│   ├── AnalyticsPanel/ ← churn score, stats, hosts ShapChart
│   ├── ShapChart/    ← Recharts horizontal bar chart
│   └── ChatPanel/    ← message list, streaming bubble, input bar
└── pages/
    └── Home.jsx      ← layout, lifts shared player state
```

### Component hierarchy

```
App.jsx
└── Home.jsx                          (owns selectedPlatform, selectedPlayerId)
    ├── PlayerSearch                  (calls onSearch → updates Home state)
    ├── AnalyticsPanel                (receives player, loading, error as props)
    │   └── ShapChart                 (receives shap_values array)
    └── ChatPanel                     (receives playerContext for LLM context)
```

### Why state lives in Home.jsx

Both `AnalyticsPanel` and `ChatPanel` need the player data.
`AnalyticsPanel` renders it. `ChatPanel` passes it to the LLM as context.
Since they're siblings, their shared state is "lifted up" to their parent (`Home.jsx`) and passed down as props. This is a core React pattern.

### Dev proxy

In development, Vite proxies `/api/*` to `localhost:8000`:

```
Browser → localhost:5173/api/v1/players/chess_com/hikaru
Vite proxy → localhost:8000/api/v1/players/chess_com/hikaru
```

No CORS issues in development. In production, the browser calls Render directly using the `VITE_API_URL` environment variable.

### Streaming chat

The chat endpoint streams responses token by token. Because axios doesn't support streaming, `chat.js` uses the native Fetch API with `ReadableStream`:

```
fetch POST /api/v1/chat
  → response.body (ReadableStream)
  → reader.read() in a loop
  → decode each chunk (TextDecoder)
  → onChunk(text) → setStreamingMessage(prev => prev + text)
  → when done: move to messages history, clear streaming state
```

---

## 5. End-to-End Request Walkthrough

### Player lookup

```
1.  User selects "Chess.com", types "hikaru", clicks submit
2.  PlayerSearch calls onSearch("chess_com", "hikaru")
3.  Home.jsx sets state → usePlayer hook triggers
4.  usePlayer calls fetchPlayerAnalytics("chess_com", "hikaru")
5.  players.js: GET /api/v1/players/chess_com/hikaru
6.  FastAPI router validates platform via game_registry
7.  data_service: loads parquet (cached), filters row for hikaru
8.  model_service: loads ensemble.joblib (cached), runs predict_proba()
9.  shap_service: loads shap_values.joblib (cached), finds hikaru's row
10. Router returns: { player_id, platform, features, prediction, shap_values }
11. usePlayer sets player state
12. AnalyticsPanel re-renders with data
13. ShapChart renders SHAP bar chart
14. ChatPanel now has playerContext loaded
```

### Chat message

```
15. User types "Why is hikaru at risk?" and clicks Send
16. ChatPanel calls sendMessage(text)
17. useChat adds user message to history, sets loading=true
18. chat.js: POST /api/v1/chat { message, player_context, conversation_history }
19. FastAPI router calls get_agent()
20. LangChain agent receives message + player context
21. LLM decides to call explain_prediction("hikaru", "chess_com")
22. Tool calls shap_service.get_player_shap() → formats top SHAP factors as text
23. LLM receives tool output
24. LLM generates a plain-English explanation
25. Response streams back chunk by chunk
26. onChunk fires → streamingMessage grows in real-time
27. ChatPanel re-renders each chunk → live typing effect
28. onDone fires → message added to history, streaming cleared
```

---

## 6. Extensibility Patterns

### Add a new game platform (e.g., Steam)

Touch exactly 4 files:

```
New:      src/game_churn/collectors/steam.py       (inherit BaseCollector, implement collect())
Modified: src/game_churn/collectors/run_all.py     (register sample player IDs)
Modified: src/game_churn/features/standardize.py   (add standardize_steam() function)
Modified: api/registry/game_registry.py            (add one dict entry)
```

The API's `/games` endpoint returns the new platform automatically.
The React dropdown updates without any frontend changes.
The LangChain agent can now call tools for Steam players.

### Add a new ML model

Touch exactly 2 files:

```
Modified: src/game_churn/models/train.py         (add training code)
Modified: api/registry/model_registry.py         (add one dict entry with path)
```

The API's `/models` endpoint lists it immediately.
Users can pass `?model_id=my_new_model` to the player endpoint.

---

## 7. Deployment

### Backend → Render

`render.yaml` at the project root configures the deployment:
- **Build**: `pip install -e . && pip install -r api/requirements.txt`
- **Start**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- Set `OPENAI_API_KEY` in Render's environment variables dashboard (never in code)

**Free tier note**: Render's free tier spins down after 15 minutes of inactivity. First request after spin-down takes ~30 seconds. Fine for demos.

### Frontend → Vercel

- Connect GitHub repo to Vercel
- Set root directory to `frontend/`
- Set environment variable: `VITE_API_URL=https://your-api.onrender.com`
- `frontend/vercel.json` handles SPA routing (all URLs → `index.html`)

### CORS

`api/config.py` defines `cors_origins`. Before deploying, add your Vercel URL:
```python
cors_origins: list[str] = [
    "http://localhost:5173",
    "https://your-app.vercel.app",   # add this
]
```

---

## 8. What Data We Pull from Each API

### Chess.com (no API key)

| Endpoint | Data | Churn signal |
|----------|------|-------------|
| `/pub/player/{username}` | Profile, last online | Recency |
| `/pub/player/{username}/stats` | Ratings per time control | Rating drops |
| Monthly archives | Individual games: timestamp, result, rating | Activity frequency, win rate |

### OpenDota / Dota 2 (no API key, 60 calls/min)

| Endpoint | Data | Churn signal |
|----------|------|-------------|
| `/players/{id}/matches?limit=200` | Match history, timestamps, win/loss | Activity + session length |
| `/players/{id}/peers` | Top 50 teammates | Social graph — social players churn less |
| `/players/{id}/ratings` | MMR over time | Rating decline = frustration |

### Riot / League of Legends (API key required)

| Endpoint | Data | Churn signal |
|----------|------|-------------|
| `/lol/match/v5/matches` | Last 100 match IDs | Recent activity |
| Per-match detail | Duration, champion, win, KDA | Performance trends |
| `/lol/league/v4/entries` | Rank, LP, win/loss | Competitive engagement |

---

## 9. Tool Choices

### Backend

| Tool | Why |
|------|-----|
| **FastAPI** | Auto-generates `/docs`, async support, Pydantic validation built in |
| **Pydantic-settings** | Reads `.env` and validates types — same as ML pipeline config |
| **Polars** | 5–10× faster than Pandas for the parquet queries |
| **joblib** | Standard Python ML serialization — used by scikit-learn internally |
| **LangChain** | Abstracts tool calling, memory, and streaming across different LLM providers |
| **@lru_cache** | Prevents reloading 50MB model files on every request |

### Frontend

| Tool | Why |
|------|-----|
| **Vite** | 10–100× faster builds than CRA, native ESM, HMR out of the box |
| **React Router** | Client-side routing — no page reloads on navigation |
| **Axios** | Cleaner API than fetch for standard requests, good interceptor support |
| **Recharts** | Most React-native chart library — JSX-based, no imperative D3 |
| **Native fetch** | Streaming requires ReadableStream — axios buffers the full response |

### ML Layer (existing)

| Tool | Why |
|------|-----|
| **XGBoost / LightGBM / CatBoost** | Best-in-class for tabular churn data |
| **Soft-voting ensemble** | Different models make different mistakes — averaging reduces overall error |
| **SHAP** | Game-theory-based feature attribution — explains individual predictions |
| **MLflow** | Tracks every training run's params + metrics for reproducibility |
| **Prefect** | Orchestrates collect → features → train with retries and scheduling |
| **DVC** | Versions large data files alongside code in Git |
