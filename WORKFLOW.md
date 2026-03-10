# Implementation Workflow

Track progress here. Check off each step as it's done.

**Legend:** `[ ]` not started · `[x]` done · `[-]` blocked/skipped

---

## What's Already Built

- [x] OpenDota collector (`collectors/opendota.py`)
- [x] RAWG collector with review fetching (`collectors/rawg.py`)
- [x] Feature engineering (`features/engineer.py`, `standardize.py`, `build.py`)
- [x] ML model training — XGBoost, LightGBM, CatBoost, Ensemble, SHAP (`models/train.py`)
- [x] Synthetic data generation (`models/synthetic.py`)
- [x] Model artifacts (`models/*.joblib`)
- [x] NLP notebook (`notebooks/01_review_text_analysis.ipynb`) — RoBERTa + GPT summaries
- [x] FastAPI app structure (`api/main.py`, `api/config.py`)
- [x] Registries (`api/registry/game_registry.py`, `model_registry.py`)
- [x] Router signatures (`api/routers/players.py`, `chat.py`)
- [x] Service stubs (`api/services/data_service.py`, `model_service.py`, `shap_service.py`)
- [x] Agent stub (`api/agents/churn_analyst.py`)
- [x] Frontend structure (`frontend/src/` — all components/hooks/api stubs)
- [x] `get_llm()` factory in `api/config.py` — Groq/OpenAI switchable via env var
- [x] `langchain-groq` installed
- [x] Demo mode — explicit synthetic data mode, separate from real pipeline
  - [x] Silent fallback removed from `train.py` (raises clear error instead)
  - [x] `api/services/demo_service.py` — generates/scores/SHAP 50 synthetic players, cached
  - [x] `api/routers/demo.py` — `/api/v1/demo/*` endpoints (summary, players, player, chat)
  - [x] `api/main.py` — demo router registered
  - [x] `frontend/src/api/demo.js` — demo API calls + streaming chat
  - [x] `frontend/src/components/DemoBanner/` — orange banner with "Exit Demo" button

---

## Phase 1 — Steam Collector ✓

> Unblocks real behavioral data from the most recognizable gaming platform.

- [x] `src/game_churn/collectors/steam.py`
  - [x] `get_player_summary(steam_id)` — profile, last_logoff
  - [x] `get_owned_games(steam_id)` — all games with playtime_forever
  - [x] `get_recently_played(steam_id)` — games played in last 2 weeks + playtime_2weeks
  - [x] `get_friend_list(steam_id)` — social graph (handles private profiles gracefully)
  - [x] `get_game_reviews(app_id)` — cursor-paginated reviews for NLP agent
  - [x] `collect(steam_id)` — saves 4 files to `data/01_raw/steam/`
- [x] `game_registry.py` — Steam entry active
- [x] `run_all.py` — Steam sample players wired in
- [x] 4/4 collector tests passing

---

## Phase 2 — Multi-tenant Foundation

> Studios need isolated data and API keys before anything else can be studio-scoped.

- [ ] `api/models/studio.py` — Pydantic schemas: `Studio`, `FieldMap`, `StudioCreate`
- [ ] `api/services/studio_service.py` — create studio, validate API key, load config (SQLite via stdlib)
- [ ] `api/middleware/auth.py` — `X-Studio-API-Key` header → `studio_id` on every request
- [ ] `api/routers/studios.py` — `POST /api/v1/studios` (register), `GET /api/v1/studios/me`
- [ ] `api/main.py` — register new routers, add auth middleware
- [ ] Verify: register a studio, get back an API key, use it in a subsequent request

---

## Phase 3 — Event Ingestion + Schema Agent

> Studios can POST any JSON. Schema agent normalizes it.

- [ ] `api/services/mapping_service.py` — apply saved `field_map` config to raw event dict
- [ ] `api/services/ingest_service.py` — validate, normalize raw event → `PlayerActivity`, append to studio's raw store
- [ ] `api/agents/schema_agent.py` — analyze sample payload, propose field mapping using `get_llm()`
- [ ] `api/routers/ingest.py`
  - [ ] `POST /api/v1/ingest/events` — single or batch event ingestion
  - [ ] `POST /api/v1/ingest/sample` — studio sends 50–100 rows, schema agent infers mapping
  - [ ] `POST /api/v1/ingest/trigger-training` — kick off feature engineering + model train
- [ ] Verify: POST a Dota 2 player event, confirm it normalizes and saves correctly

---

## Phase 4 — NLP Pipeline + NLP Agent

> Review text → sentiment features that enrich ML predictions.

- [ ] `src/game_churn/features/text_features.py` — productionize NLP notebook into callable functions
  - [ ] `clean_text(raw: str) -> str` — strip HTML, normalize
  - [ ] `score_sentiment(texts: list[str]) -> list[dict]` — RoBERTa batch inference
  - [ ] `extract_keywords(texts: list[str]) -> list[str]` — top complaint topics
  - [ ] `summarize_reviews(texts: list[str], game_name: str) -> str` — GPT summary via `get_llm()`
  - [ ] `build_sentiment_features(reviews: list[dict]) -> pl.DataFrame` — aggregate per player/game
- [ ] `api/services/nlp_service.py` — wrap `text_features.py`, save sentiment parquet to studio data dir
- [ ] `api/agents/nlp_agent.py` — orchestrate NLP pipeline on incoming review batches
- [ ] `api/routers/ingest.py` — `POST /api/v1/ingest/reviews` triggers NLP agent
- [ ] Merge sentiment features into `features/build.py` so they flow into ML training
- [ ] Verify: POST reviews → sentiment parquet exists → feature build includes sentiment columns

---

## Phase 5 — Core Backend Services + Training

> Implement the stubs. Everything downstream depends on these.

- [ ] `api/services/data_service.py` — implement (studio-scoped parquet load, player query, dataset summary)
- [ ] `api/services/model_service.py` — implement (studio-scoped model load, predict_proba, risk label)
- [ ] `api/services/shap_service.py` — implement (studio-scoped SHAP load, per-player explanation)
- [ ] `api/services/training_service.py` — trigger `build.py` → `train.py` for a given studio, save to `models/{studio_id}/`
- [ ] `api/routers/players.py` — implement all 4 endpoints using the services
- [ ] Verify via `/docs`:
  - [ ] `GET /api/v1/players/games` returns OpenDota + Steam
  - [ ] `GET /api/v1/players/opendota/87278757` returns prediction + SHAP

---

## Phase 6 — Chat Agent

> The conversational layer that makes this usable for non-technical studio staff.

- [ ] `api/agents/churn_analyst.py` — implement all tools using `get_llm()`:
  - [ ] `get_player_data(player_id, platform)` — fetch features + churn prediction
  - [ ] `explain_prediction(player_id, platform)` — SHAP → plain English
  - [ ] `get_dataset_context()` — fleet-level stats (churn rate, platform breakdown)
  - [ ] `suggest_retention_strategy(player_id, platform)` — top risk factors → actions
  - [ ] `get_at_risk_players(limit)` — ranked list of highest-risk players
  - [ ] `get_agent()` — assemble LangChain agent with all tools + studio-aware system prompt
- [ ] `api/routers/chat.py` — implement streaming endpoint (`astream_events` + `StreamingResponse`)
- [ ] Verify: ask "Who are our most at-risk players?" and get a real streamed answer

---

## Phase 7 — Frontend

> Make the product usable through a browser.

- [ ] `frontend/src/api/players.js` — implement fetch functions
- [ ] `frontend/src/api/chat.js` — implement streaming fetch
- [ ] `frontend/src/api/studios.js` — studio registration + config
- [ ] `frontend/src/hooks/usePlayer.js` — player fetch state
- [ ] `frontend/src/hooks/useChat.js` — conversation + streaming state
- [ ] `frontend/src/components/PlayerSearch/` — platform dropdown + ID input
- [ ] `frontend/src/components/AnalyticsPanel/` — churn score, risk badge, key stats
- [ ] `frontend/src/components/ShapChart/` — Recharts horizontal bar (red/green)
- [ ] `frontend/src/components/SentimentPanel/` — review sentiment trend + top complaints
- [ ] `frontend/src/components/CohortView/` — high/medium/low risk segment breakdown
- [ ] `frontend/src/components/ChatPanel/` — streaming agent UI with suggested questions
- [ ] `frontend/src/pages/Home.jsx` — main dashboard layout
- [ ] `frontend/src/pages/Onboarding.jsx` — studio registration + field mapping review UI

---

## Phase 8 — Deployment

- [ ] Backend → Render (`render.yaml` already configured)
  - [ ] Set `GROQ_API_KEY`, `STEAM_API_KEY`, `GAME_CHURN_RAWG_API_KEY` in Render env vars
  - [ ] Confirm `/health` returns `{"status": "ok"}`
  - [ ] Add Render URL to `cors_origins` in `api/config.py`
- [ ] Frontend → Vercel
  - [ ] Set `VITE_API_URL` to Render URL
  - [ ] Confirm player lookup + chat work end-to-end

---

## Blockers / Decisions Log

| Date | Issue | Resolution |
|------|-------|-----------|
| 2026-03-09 | Dropped Chess.com + Riot — too niche / requires key for demo | Replaced with Steam (more relevant, better data) |
| 2026-03-09 | Prefect removed — over-engineered for agentic pipeline | Training triggered by `training_service.py` via API |
| 2026-03-09 | Default LLM switched to Groq | Free tier, fast, reliable tool-calling. Switch to OpenAI via `LLM_PROVIDER=openai` |
