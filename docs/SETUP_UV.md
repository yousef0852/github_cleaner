# Setup with uv

Use **uv** instead of venv + pip. One-time setup, then how to run.

---

## 1. Install uv (if you don’t have it)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then restart your terminal (or run `source $HOME/.local/bin/env` if the installer added it). Check:

```bash
uv --version
```

---

## 2. One-time project setup

From the **project root** (`github_cleaner/`):

**Create the environment:**

```bash
uv venv
```

**Install the project in editable mode:**

```bash
uv pip install -e .
```

That’s the setup. No code changes needed.

---

## 3. Run the API

From the **project root** (`github_cleaner/`), activate the venv then start uvicorn **with `PYTHONPATH=src` in the same command** (required so Python finds the `api` package under `src/`):

```bash
source .venv/bin/activate
PYTHONPATH=src uvicorn api.main:app --reload
```

Or without activating (uv uses the project venv):

```bash
PYTHONPATH=src uv run uvicorn api.main:app --reload
```

Then open **http://localhost:8000/health** and **POST http://localhost:8000/scan** with the JSON body (see README or AGENT_INTEGRATION.md).

**If you see `ModuleNotFoundError: No module named 'api'`:** you ran uvicorn without `src` on the path. Use one of the commands above from the project root; do not run uvicorn from inside `src` unless you `cd src` first and then run `uvicorn api.main:app --reload` (then the current directory is on the path).

---

## Optional: GitHub token

Only needed for higher rate limits or `scan_scope: "all"`:

```bash
export GITHUB_TOKEN=ghp_your_token_here
```

Set this in the same terminal before running `uvicorn`, or add it to your shell profile.

---

## When using the agent (Phase 1.5) with a cloud agent (e.g. Voiceflow)

The agent runs in the cloud and must call your API. Your API is on `localhost`, so the agent cannot reach it unless you expose it.

**Use ngrok** (or similar) to get a public URL for your local server:

1. Start your API: `source .venv/bin/activate` then `PYTHONPATH=src uvicorn api.main:app --reload` (from project root).
2. In **another terminal**: `ngrok http 8000`. Leave it running.
3. Use the **exact** URL ngrok prints (e.g. `https://rex-thatchy-ciliately.ngrok-free.dev`). Note: free tier often uses **`.ngrok-free.dev`** — not `.app`.
4. In Voiceflow, set **BASE_URL** to that URL. Call `POST {BASE_URL}/scan` with header `ngrok-skip-browser-warning: true` if the agent gets HTML instead of JSON.

**Verify everything:** From the project root run `./scripts/check-ngrok.sh` while both the API and ngrok are running. It will print the correct BASE_URL and confirm `/health` works.

Without ngrok, the agent will get connection errors when it tries to hit `localhost`.
