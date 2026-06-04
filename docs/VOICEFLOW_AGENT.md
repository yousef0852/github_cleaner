# Phase 1.5 — Voiceflow agent (run + connect)

This is the **documented way** to run the backend and connect a **Voiceflow** (or similar) agent. Prefer **`POST /scan/voiceflow`** for a **flat** JSON (no nested `summary` / `repos` / arrays) — see **[AGENT_INTEGRATION.md](AGENT_INTEGRATION.md)**. Use **`POST /scan`** when you need the full payload.

### Production (Render + published Voiceflow)

| Item | Example |
| ---- | -------- |
| **Deployed API** | `https://github-cleaner-api.onrender.com` (your Render service URL) |
| **Voiceflow API block URL** | `https://github-cleaner-api.onrender.com/scan/voiceflow` |
| **Headers** | `Content-Type: application/json` only — **do not** send `ngrok-skip-browser-warning` (ngrok only). |
| **Token** | Set **`GITHUB_TOKEN`** in the Render service **Environment** (not in git). |
| **Publish** | In Voiceflow, **Publish** Development → Production when the prototype works. |

Full deploy steps: **[DEPLOY_RENDER.md](DEPLOY_RENDER.md)**.

---

## Prerequisites

- Project installed: `pip install -e .` or `uv pip install -e .` from the repo root.
- **`.env`** at the project root with a valid GitHub token (recommended to avoid rate limits and `401 Bad credentials`):

  ```bash
  cp .env.example .env
  # Edit .env: GITHUB_TOKEN=ghp_your_real_token
  ```

  See the main [README](../README.md) — the app loads `.env` on startup via `python-dotenv`.

---

## 1. Run the API (local)

From the **project root** (`github_cleaner/`):

```bash
source .venv/bin/activate
PYTHONPATH=src uvicorn api.main:app --reload
```

Default URL: **`http://127.0.0.1:8000`**. Health check: `GET http://localhost:8000/health` → `{"status":"ok"}`.

---

## 2. Expose localhost for cloud agents (ngrok)

Voiceflow runs in the cloud; it cannot call `http://localhost:8000` on your machine unless you tunnel.

1. Install [ngrok](https://ngrok.com/) and add your [authtoken](https://dashboard.ngrok.com/get-started/your-authtoken) once: `ngrok config add-authtoken …`
2. **Use the same port as uvicorn** (default **8000**):

   ```bash
   ngrok http 8000
   ```

3. Copy the **Forwarding** HTTPS URL from the ngrok terminal (e.g. `https://rex-thatchy-ciliately.ngrok-free.dev`). Free tier may use **`.ngrok-free.dev`** — use the exact host ngrok prints.

4. Leave **both** terminals open: one for uvicorn, one for ngrok.

**Verify the tunnel** (optional):

```bash
curl -H "ngrok-skip-browser-warning: true" https://YOUR_NGROK_HOST/health
```

Or run `./scripts/check-ngrok.sh` while uvicorn and ngrok are up — it prints the live public URL and checks `/health`.

---

## 3. Configure Voiceflow (API block)

**Where in Voiceflow:** open your agent project → find the **canvas** (the diagram with blocks) → click the block that **calls your backend** (often labeled **API**, **Integrations**, or shows `POST` + a URL). Settings for that block open on the **right** — that’s where you paste the URL and body.

### Option A — Flat JSON (easiest for Voiceflow): `POST /scan/voiceflow`

| Setting | Value |
|--------|--------|
| **Method** | `POST` |
| **URL (production)** | `https://<your-render-host>/scan/voiceflow` e.g. `https://github-cleaner-api.onrender.com/scan/voiceflow` |
| **URL (local + ngrok)** | `https://<your-ngrok-host>/scan/voiceflow` |
| **Headers** | `Content-Type: application/json` |
| **Extra header (ngrok only)** | `ngrok-skip-browser-warning: true` — **omit on Render** |

**Body (JSON),** e.g. (replace the username part with your Voiceflow variable if the editor uses `{{variable}}` or another syntax):

```json
{
  "github_username": "octocat",
  "review_mode": "portfolio",
  "scan_scope": "public"
}
```

**Capture response (map to variables):** the JSON has **no** nested `summary` — use top-level keys only, e.g. `total_repos`, `showcase_ready`, `needs_cleanup`, `archive_candidates`, `top_issue_1`, `top_issue_2`, `top_issue_3`, `recommended_next_step`, `archive_repo_1`, `archive_repo_2`, `cleanup_repo_1`, `cleanup_repo_2`, `showcase_repo_1`, `showcase_repo_2` (highest-scoring showcase repos). See **[AGENT_INTEGRATION.md](AGENT_INTEGRATION.md)** for the full list and error codes (**400 / 404 / 502**).

**Remove** any old mappings like `summary.total_repos` or `top_issues.0` — those only match **`/scan`**, not **`/scan/voiceflow`**.

**Example speak / text block** (variable names must match what you saved in Capture):

```text
GitHub scan results

You have {total_repos} public repositories.

- Showcase-ready: {showcase_ready}
- Need cleanup: {needs_cleanup}
- Archive candidates: {archive_candidates}

Most common issues:
1. {top_issue_1}
2. {top_issue_2}
3. {top_issue_3}

Pin these on your profile if you can: {showcase_repo_1}, {showcase_repo_2}

Repos to prioritize for cleanup: {cleanup_repo_1}, {cleanup_repo_2}
Repos to consider archiving: {archive_repo_1}, {archive_repo_2}

Recommended next step: {recommended_next_step}
```

### Option B — Full JSON: `POST /scan`

Same as above but URL ends with **`/scan`**. Map nested paths, e.g. `summary.total_repos`, `top_issues[0]`, `repos`, etc.

---

## 4. Production polish — API timeout & failure paths (Voiceflow)

The canvas lives in Voiceflow; labels (**Timeout**, **Failure path**, **Catch errors**) may vary slightly by product version. Goal: **long timeout** + **separate messages** for “user not found” vs “GitHub/server problem”.

### 4.1 Increase timeout

Scans can take **15–60+ seconds** (many repos + GitHub + structure checks). On **Render free tier**, the **first** request after sleep can add **30–90 seconds** (cold start).

| Where | Suggested value |
| ----- | ---------------- |
| API / Integration block → **Timeout** (or **Advanced**) | **90 seconds** minimum; **120 seconds** if the UI allows it |

If Voiceflow only offers a preset, pick the **largest** available for this block.

### 4.2 Turn on the failure branch

1. Open the same **API** block that calls `/scan/voiceflow`.
2. Find **Failure path**, **On error**, **Catch errors**, or a **second output port** from the API block (not the success path).
3. **Enable** it so failed HTTP responses and timeouts go to a **separate** path on the canvas — do **not** send the user to the “scan results” text block on that path.

### 4.3 Map error `detail` (optional)

On error, FastAPI returns JSON such as:

```json
{"detail": "GitHub user not found"}
```

If Voiceflow lets you **capture variables from the error response**, map **`detail`** → e.g. `api_error_detail`. Then use conditions below. If you cannot map it, use a **single** generic error message (section 4.5).

### 4.4 Branch on status code (if available)

Some builders expose **HTTP status** (e.g. `status_code`, `response_code`). Use:

| Status | Meaning | Next step on canvas |
| ------ | -------- | --------------------- |
| **404** | Username not found on GitHub | Message block: “user not found” (copy below) |
| **400** | Bad request / `scan_scope: all` without server token | Explain public-only or contact admin |
| **422** | Bad body (e.g. empty username) | Ask user to enter a valid username |
| **502** | GitHub or server error | “Temporary problem” message + retry |
| **Timeout / no status** | Render cold start or overload | Same as 502 — ask user to **retry once** after ~1 minute |

### 4.5 Copy-paste messages (English)

Use these in **Text / Speak** blocks on the **failure** path.

**404 — user not found**

```text
I couldn't find a GitHub user with that username. Check the spelling (case doesn't matter) and try again.
```

**502 / timeout / generic server**

```text
Something went wrong while talking to GitHub, or the scan took too long. If this is the first try in a while, wait a minute and try again — the server may be waking up. Otherwise try again in a few minutes.
```

**400 — private scan without token**

```text
Scanning private repositories isn't available on this deployment. Try again with public repositories only, or ask the admin to configure the server token.
```

**422 — validation**

```text
That input wasn't accepted. Please enter a non-empty GitHub username and try again.
```

### 4.6 نصوص جاهزة (عربي) — اختياري

**404**

```text
ما لقيت مستخدم GitHub بهذا الاسم. تأكد من الإملاء وحاول مرة ثانية.
```

**502 / انتهاء الوقت**

```text
صار خطأ أثناء الاتصال بـ GitHub أو طال وقت الاستجابة. إذا كانت أول محاولة من زمان، انتظر دقيقة وحاول مرة ثانية (السيرفر قد يكون يستيقظ). وإلا حاول بعد شوي.
```

---

## 5. Troubleshooting (short)

| Symptom | Likely cause |
|--------|----------------|
| ngrok “offline” / ERR_NGROK_3200 | ngrok not running, or wrong hostname (e.g. `.app` vs `.dev`). |
| ERR_NGROK_8012 upstream `localhost:8001` | ngrok points to **8001** but API is on **8000** — run `ngrok http 8000`. |
| `502` + GitHub “Bad credentials” | Invalid `GITHUB_TOKEN` in `.env` or placeholder left in place. |
| `502` + rate limit | Set a real token in `.env`, or wait and retry. |
| Voiceflow “API tool failed”, curl works | Increase API block timeout; scan can take many seconds for large profiles. |
| First request slow on Render free tier | **Cold start** — wait and retry, or raise Voiceflow timeout / use a paid Render instance. |

---

## 6. Related docs

- **[AGENT_INTEGRATION.md](AGENT_INTEGRATION.md)** — `POST /scan` request/response JSON, errors, agent behavior.
- **[PHASE_1.5_AGENT_PLAN.md](PHASE_1.5_AGENT_PLAN.md)** — Phase 1.5 goals and checklist.
- **[SETUP_UV.md](SETUP_UV.md)** — uv / ngrok notes.

---

## Phase 1.5 success (this setup + polish)

**Production:** API on **Render** (or similar) + Voiceflow calling `POST https://<your-host>/scan/voiceflow` with flat capture + **Publish** to Production.

**Local dev:** uvicorn + **ngrok** to **8000** + same `/scan/voiceflow` path + `ngrok-skip-browser-warning` header.
