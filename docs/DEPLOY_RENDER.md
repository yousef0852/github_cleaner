# Deploy GitHub Cleaner API on Render

Use this so Voiceflow can call **`https://your-service.onrender.com/scan/voiceflow`** without ngrok.

---

## Before you start

1. Push this repo to **GitHub** (Render pulls from GitHub).
2. Have a **GitHub personal access token** ready (for rate limits and optional `scan_scope: "all"`).

---

## 1. Create a Web Service on Render

1. Go to [render.com](https://render.com) → sign in → **Dashboard**.
2. **New +** → **Web Service**.
3. Connect your **GitHub** account if asked → choose the **`github_cleaner`** repository.
4. Configure:

| Field | Value |
| ----- | ----- |
| **Name** | e.g. `github-cleaner-api` (becomes part of your URL) |
| **Region** | Closest to you |
| **Branch** | `main` (or your default branch) |
| **Root directory** | Leave empty if the FastAPI app is at the repo root |
| **Runtime** | **Python 3** |
| **Build command** | `pip install .` |
| **Start command** | `uvicorn api.main:app --host 0.0.0.0 --port $PORT` |

5. Click **Advanced** → **Add environment variable**:

   | Key | Value |
   | --- | ----- |
   | `GITHUB_TOKEN` | Your token (e.g. `ghp_...`) — mark **Secret** if Render offers it |

6. **Create Web Service** and wait for the first deploy (a few minutes).

---

## 2. Check that it works

Your service URL will look like:

`https://github-cleaner-api.onrender.com`  
(exact name depends on what you chose.)

- **`GET /`** — short JSON with links to `docs`, `health`, and scan paths (not an error).
- **`GET /docs`** — Swagger UI.
- **`GET /health`** → `{"status":"ok"}`.

**Voiceflow** must call **`POST https://YOUR-SERVICE.onrender.com/scan/voiceflow`** (not `/` alone — that is not the scan endpoint).

**Note (free tier):** The service **sleeps** after idle time. The **first** request after sleep can take **30–60+ seconds** (cold start). Voiceflow may time out unless you increase the API step timeout or use a paid plan that stays awake.

---

## 3. Point Voiceflow at Render

1. Open your **API** block in Voiceflow.
2. Set **URL** to:

   ```text
   https://YOUR-SERVICE.onrender.com/scan/voiceflow
   ```

   Replace `YOUR-SERVICE.onrender.com` with your real host.

3. **Method:** `POST`  
4. **Headers:** keep **`Content-Type: application/json`**.  
   You can **remove** `ngrok-skip-browser-warning` — that header is only for ngrok.
5. **Body** and **Capture** — same as local (flat keys: `total_repos`, `top_issue_1`, …).
6. **Run** in Voiceflow and test with a real username.

---

## 4. Publish Voiceflow

When tests look good → **Publish** in Voiceflow. End users hit Voiceflow; Voiceflow calls **Render**, not your laptop.

---

## Troubleshooting

| Problem | What to try |
| -------- | ------------ |
| Build fails | Check Render logs; ensure **Build command** is `pip install .` and Python ≥ 3.10. |
| Crashes on start | **Start command** must include `--host 0.0.0.0` and `--port $PORT`. |
| 502 from GitHub | Set or fix **`GITHUB_TOKEN`** in Render environment. |
| Voiceflow timeout | Cold start on free tier — retry once, increase API timeout in Voiceflow, or upgrade Render. |

---

## Optional: repo on Render without `pip install .`

If `pip install .` fails in build, add a **`requirements.txt`** at the repo root with:

```text
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0
httpx>=0.26.0
python-dotenv>=1.0.0
```

Then set **Build command** to: `pip install -r requirements.txt` and keep the same **Start command** (packages under `src` still need to be importable — `pip install .` is preferred because it installs the package layout correctly).

If Render still cannot import `api`, set **Start command** to:

```bash
PYTHONPATH=src uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

and use **Build command** `pip install -r requirements.txt` (with the file above).
