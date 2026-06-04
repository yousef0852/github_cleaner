# GitHub Cleaner AI Agent

Production-grade AI system that analyzes GitHub profiles, evaluates repository quality, and provides structured recommendations to improve portfolio quality.

## Architecture

- **Layer 1 — Agent**: Conversation, tool calls (Voiceflow / LLM).
- **Layer 2 — Backend API**: FastAPI; orchestration and response shaping.
- **Layer 3 — Scoring Engine**: Deterministic scoring and classification.
- **Layer 4 — Data**: GitHub API client (read-only in MVP).

See [ARCHITECTURE.md](ARCHITECTURE.md) and [docs/MODULES.md](docs/MODULES.md). **Full project work plan (vision & phases 1–7):** [docs/PROJECT_WORK_PLAN.md](docs/PROJECT_WORK_PLAN.md). **Docs map:** [docs/README.md](docs/README.md).

**Phase 1.5 — Voiceflow agent:** connect Voiceflow to **`POST /scan/voiceflow`** (flat JSON) or **`POST /scan`** (full JSON) — **[docs/VOICEFLOW_AGENT.md](docs/VOICEFLOW_AGENT.md)** · contract **[docs/AGENT_INTEGRATION.md](docs/AGENT_INTEGRATION.md)** · **deploy API (e.g. Render):** **[docs/DEPLOY_RENDER.md](docs/DEPLOY_RENDER.md)**.

**Production example:** API at `https://github-cleaner-api.onrender.com` — Voiceflow uses `https://github-cleaner-api.onrender.com/scan/voiceflow`. Set **`GITHUB_TOKEN`** in Render’s environment.

## MVP (Phase 1)

- Read-only GitHub scan
- Repository scoring (0–100)
- Classification: showcase / cleanup / archive
- Issue detection and suggestions
- No write actions

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .
```

**GitHub token (recommended):** Copy `.env.example` to `.env`, put your real token in `GITHUB_TOKEN=...`, and restart the API. The app loads `.env` automatically. Never commit `.env` (it is in `.gitignore`).

## Run API

From project root (after `pip install -e .`):

```bash
PYTHONPATH=src uvicorn api.main:app --reload
```

Or run from `src`: `uvicorn api.main:app --reload`

POST **`/scan`** (full response) or **`/scan/voiceflow`** (flat fields for no-code tools) with JSON:

```json
{
  "github_username": "octocat",
  "review_mode": "portfolio",
  "scan_scope": "public"
}
```

- **`GET /`** — small JSON index (links to docs, health, scan paths).  
- **`GET /docs`** — Swagger UI.

## Streamlit demo (free UI, no Voiceflow)

Calls the same **`POST /scan/voiceflow`** as the hosted API (default: Render). Runs on your machine; uses **httpx** server-side (no CORS issues).

```bash
source .venv/bin/activate
pip install -e ".[demo]"
streamlit run streamlit_app.py
```

Then open the URL Streamlit prints (usually `http://localhost:8501`). Set **API base URL** in the sidebar if your API is not on Render.

## Deploy (Render)

See **[docs/DEPLOY_RENDER.md](docs/DEPLOY_RENDER.md)**. After deploy, use **`https://<your-service>.onrender.com/scan/voiceflow`** in Voiceflow (not ngrok).

## Save scan result to JSON

From project root, with the API running:

```bash
chmod +x scripts/scan-and-save.sh
./scripts/scan-and-save.sh Mjeedbakr
```

Result is saved to **`output/scan_Mjeedbakr.json`**. Use any username:

```bash
./scripts/scan-and-save.sh octocat    # → output/scan_octocat.json
./scripts/scan-and-save.sh YOUR_USER  # → output/scan_YOUR_USER.json
```

Or with curl only (saves formatted JSON):

```bash
curl -s -X POST http://localhost:8000/scan \
  -H "Content-Type: application/json" \
  -d '{"github_username":"Mjeedbakr","review_mode":"portfolio","scan_scope":"public"}' \
  | python3 -c "import sys,json; json.dump(json.load(sys.stdin), open('output/scan_Mjeedbakr.json','w'), indent=2)"
```

## Project Layout

```
src/
  api/          # FastAPI app and routes
  contracts/    # Pydantic input/output and DTOs
  data/         # GitHub API client
  scoring/      # Scoring, classification, issues, suggestions
docs/           # Architecture and module docs
tests/          # Tests
```

## License

MIT
