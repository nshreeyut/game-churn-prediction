# Implementation Workflow

Track progress here. Check off each step as it's done. Add notes on blockers or decisions inline.

**Legend:** `[ ]` not started · `[x]` done · `[-]` blocked/skipped

---

## Pre-flight — Verify ML Artifacts

> The entire backend reads these files. Do this first.

```bash
make train
```

- [ ] `data/03_features/player_features.parquet` exists
- [ ] `models/ensemble.joblib` exists
- [ ] `models/scaler.joblib` exists
- [ ] `models/shap_values.joblib` exists
- [ ] Confirm real player IDs in the parquet: `python -c "import polars as pl; print(pl.read_parquet('data/03_features/player_features.parquet')[['player_id','platform']].head(5))"`

---

## Phase 1 — Backend Services

> Work bottom-up. Each service can be tested in a Python shell before touching any router.

### Step 1 · `api/services/data_service.py`

- [ ] `load_features()` — reads parquet, raises clear error if missing
- [ ] `get_player()` — filters by player_id + platform, returns dict or None
- [ ] `list_players()` — filters + selects key columns + limit
- [ ] `get_dataset_summary()` — total players, churn rate, avg scores, platform list

**Verify:**
```python
from api.services.data_service import load_features, get_player, get_dataset_summary
df = load_features()
print(df.shape)                          # expect (2000, ~20)
print(get_player("player_0", "chess_com"))
print(get_dataset_summary())
```

Notes:

---

### Step 2 · `api/services/model_service.py`

- [ ] Cross-check `FEATURE_COLUMNS` list against actual parquet columns
- [ ] `load_scaler()` — loads `models/scaler.joblib`
- [ ] `load_model()` — loads requested model by registry ID
- [ ] `predict_churn()` — arranges features → scale → predict_proba → risk label

**Verify:**
```python
from api.services.data_service import get_player
from api.services.model_service import predict_churn
player = get_player("player_0", "chess_com")
print(predict_churn(player))             # expect: { churn_probability, risk_level, ... }
```

Notes:

---

### Step 3 · `api/services/shap_service.py`

- [ ] Inspect `models/shap_values.joblib` structure before implementing:
  ```python
  import joblib; d = joblib.load("models/shap_values.joblib"); print(type(d), d.keys() if isinstance(d, dict) else "")
  ```
- [ ] `load_shap_values()` — loads the file
- [ ] `get_player_shap()` — finds player row, pairs with feature names, sorts by abs value

**Verify:**
```python
from api.services.shap_service import get_player_shap
print(get_player_shap("player_0", "chess_com"))
```

Notes:

---

## Phase 2 — Backend Routers

> Start the server after each step and test in `/docs`.

```bash
uvicorn api.main:app --reload --port 8000
# then open http://localhost:8000/docs
```

### Step 4 · `api/routers/players.py`

- [ ] `get_games()` — returns `get_supported_games()` (1 line)
- [ ] `get_models()` — returns `list_models()` (1 line)
- [ ] `search_players()` — calls `list_players()`, handles missing file with 503
- [ ] `get_player_analytics()` — validate platform → get player → predict → shap → combined response

**Test each endpoint in `/docs` before moving on.**

Notes:

---

### Step 5 · `api/agents/churn_analyst.py`

Implement tools first, agent last.

- [ ] `get_dataset_context` tool — calls `get_dataset_summary()`
- [ ] `get_player_data` tool — calls `get_player()` + `predict_churn()`
- [ ] `explain_prediction` tool — calls `get_player_shap()`, formats as readable string
- [ ] `suggest_retention_strategy` tool — maps top SHAP factors to interventions
- [ ] `get_agent()` — LLM + tools + prompt + AgentExecutor

**Verify tools before wiring the agent:**
```python
from api.agents.churn_analyst import get_player_data, explain_prediction
print(get_player_data.invoke({"player_id": "player_0", "platform": "chess_com"}))
print(explain_prediction.invoke({"player_id": "player_0", "platform": "chess_com"}))
```

Notes:

---

### Step 6 · `api/routers/chat.py`

- [ ] Non-streaming first — `agent.invoke()`, return `{"response": result["output"]}`
- [ ] Test in `/docs`: ask "What is the overall churn rate?"
- [ ] Upgrade to streaming — `agent.astream_events()` + `StreamingResponse`

Notes:

---

## Phase 3 — Frontend

> Keep the API server running the whole time. Build one piece, see it render, move on.

```bash
cd frontend
npm install
npm run dev    # http://localhost:5173
```

### Step 7 · `src/api/players.js`

- [ ] `fetchSupportedGames()`
- [ ] `fetchModels()`
- [ ] `fetchPlayerAnalytics(platform, playerId, modelId)`
- [ ] `fetchPlayers(platform, limit)`

**Verify in browser console:**
```js
import('/src/api/players.js').then(m => m.fetchSupportedGames().then(console.log))
```

Notes:

---

### Step 8 · `src/hooks/usePlayer.js`

- [ ] `useState` for player, loading, error
- [ ] `fetchPlayer` async function with try/catch/finally
- [ ] `useEffect` — fetch when platform or playerId changes, skip if either is null
- [ ] Return `{ player, loading, error, refetch }`

Notes:

---

### Step 9 · `PlayerSearch` component

- [ ] Fetch games on mount → populate dropdown
- [ ] Update input placeholder when platform changes
- [ ] Call `onSearch(platform, playerId)` on submit
- [ ] Basic validation (no empty fields)

Notes:

---

### Step 10 · `AnalyticsPanel` + `ShapChart`

- [ ] Loading state (skeleton or spinner)
- [ ] Error state (clear message card)
- [ ] Player header — ID, platform, risk level badge (color coded)
- [ ] Churn probability display
- [ ] Key stats grid — engagement score, days since last game, games_7d, win_rate_7d
- [ ] Pass `shap_values` to `ShapChart`
- [ ] `ShapChart` — Recharts horizontal bar chart, red/green bars, reference line at 0

Notes:

---

### Step 11 · `src/api/chat.js` + `src/hooks/useChat.js`

- [ ] `chat.js` — non-streaming version first (fetch + `await res.json()`)
- [ ] `useChat.js` — messages state, streamingMessage, sendMessage function
- [ ] `chat.js` — upgrade to streaming (ReadableStream + reader loop)
- [ ] `useChat.js` — handle streaming chunks with `streamRef`

Notes:

---

### Step 12 · `ChatPanel`

- [ ] Render message history (user vs assistant styling)
- [ ] Streaming bubble (live typing effect)
- [ ] Suggested questions — shown when chat is empty, clickable
- [ ] Auto-scroll to bottom on new messages (`useRef` + `scrollIntoView`)
- [ ] Input bar — disabled while loading, submit on Enter or button click

Notes:

---

## Phase 4 — Deployment

### Step 13 · Backend → Render

- [ ] Push repo to GitHub
- [ ] Create Render Web Service, connect repo, confirm `render.yaml` is detected
- [ ] Set `OPENAI_API_KEY` in Render environment variables
- [ ] Confirm `/health` returns `{"status": "ok"}`
- [ ] Confirm `/docs` loads
- [ ] Add Render URL to `cors_origins` in `api/config.py`

Notes:

---

### Step 14 · Frontend → Vercel

- [ ] Connect GitHub repo to Vercel, set root directory to `frontend/`
- [ ] Set `VITE_API_URL` to Render URL in Vercel environment variables
- [ ] Confirm player lookup works end to end on the deployed URL
- [ ] Confirm chat works end to end on the deployed URL

Notes:

---

## Blockers / Decisions Log

> Record anything unexpected here so you don't lose context between sessions.

| Date | Issue | Resolution |
|------|-------|-----------|
| | | |
