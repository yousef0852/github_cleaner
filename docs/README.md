# Docs index — how everything fits

Use this page to see **which file to open** and how phases relate.

---

## Big picture (phases)

| Phase             | What it is                                             | In this repo?                                               |
| ----------------- | ------------------------------------------------------ | ----------------------------------------------------------- |
| **Phase 1 (MVP)** | Backend: GitHub scan, scoring, `POST /scan`, tests     | **Yes** — implemented                                       |
| **Phase 1.5**     | Agent talks to user, calls `POST /scan`, explains JSON | **Partly** — API + docs here; **Voiceflow UI** in Voiceflow |
| **Later**         | DB, writes, guided cleanup, Phase 4 ideas              | **Not** built yet                                           |

---

## File guide

| File                                                               | Read when you want to…                                                                                                   |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| **[README.md](README.md)** (this file)                             | Orientation and doc map                                                                                                  |
| **[START_HERE.md](START_HERE.md)**                                 | Understand the **code** path: `main.py` → `scan.py` → data → scoring                                                     |
| **[MODULES.md](MODULES.md)**                                       | Module boundaries                                                                                                        |
| **[AGENT_INTEGRATION.md](AGENT_INTEGRATION.md)**                   | **JSON contract** for `POST /scan`                                                                                       |
| **[PHASE_1.5_AGENT_PLAN.md](PHASE_1.5_AGENT_PLAN.md)**             | Phase 1.5 spec, checklist, success criteria                                                                              |
| **[VOICEFLOW_AGENT.md](VOICEFLOW_AGENT.md)**                       | Run API, ngrok, Voiceflow; **§4** = timeout + failure paths + error copy (EN/AR)                                          |
| **[DEPLOY_RENDER.md](DEPLOY_RENDER.md)**                           | **Deploy API on Render** → stable URL for Voiceflow (no ngrok)                                                           |
| **Streamlit** (`streamlit_app.py` at repo root)                    | Free local UI: `pip install -e ".[demo]"` then `streamlit run streamlit_app.py` — see main **README.md**                  |
| **[SETUP_UV.md](SETUP_UV.md)**                                     | uv / optional tooling                                                                                                    |
| **[BUILD_SUMMARY.md](BUILD_SUMMARY.md)**                           | **What we’ve built** (files + documented Voiceflow path)                                                                 |
| **[PROJECT_WORK_PLAN.md](PROJECT_WORK_PLAN.md)**                   | **North-star work plan** — full vision (phases 1–7, safety, extensions) vs current repo                                  |
| **[EVALUATION_AND_NEXT_STEPS.md](EVALUATION_AND_NEXT_STEPS.md)**   | **What to do now** — phase status vs plan, gaps, prioritized next steps (English)                                        |
| **[TASKS.md](TASKS.md)**                                           | Phase 2 inspector checklist (mostly done)                                                                                |
| **[TASKS_STRUCTURE_TO_SCORING.md](TASKS_STRUCTURE_TO_SCORING.md)** | **Next tasks** — plain English + steps: use `structure_report` in issues → suggestions → score, then breakdown / plans   |
| **[TASKS_SCORE_BREAKDOWN.md](TASKS_SCORE_BREAKDOWN.md)**           | **Priority 2 checklist** — `ScoreBreakdown`, `score_evidence`, `scorer` refactor, aggregator, tests, `AGENT_INTEGRATION` |
| **[TASKS_REMEDIATION.md](TASKS_REMEDIATION.md)**                     | Remediation plan — pointers to `remediation.py`, contracts, tests (implemented)                                         |
| **[TASKS_PHASE2.md](TASKS_PHASE2.md)**                             | **Phase 2 (your work)** — README depth; stub modules in `src/phase2/` with per-file task counts                          |

**Suggested order:** new to code → `START_HERE.md` · wiring an agent → `AGENT_INTEGRATION.md` → `VOICEFLOW_AGENT.md` · inventory → `BUILD_SUMMARY.md`.
