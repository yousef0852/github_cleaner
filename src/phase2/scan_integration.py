"""
scan_integration — how Phase 2 plugs into the existing scan pipeline.

Total tasks for YOU to implement: **7**

-------------------------------------------------------------------------------
Task 1 — Read current data flow
-------------------------------------------------------------------------------
What:
  - Trace: `api/routes/scan.py` → `fetch_repos_for_user` → `inspect_repo` →
    `build_scan_result` → `RepoResult`.

How to search:
  - Read files: `src/api/routes/scan.py`, `src/scoring/aggregator.py`,
    `src/contracts/repo_dto.py`, `src/contracts/scan_response.py`

-------------------------------------------------------------------------------
Task 2 — Extend RepoDTO (optional fields)
-------------------------------------------------------------------------------
What:
  - Add optional fields e.g. readme_excerpt: str | None, readme_signals: dict |
    None — or a nested model. Keep backward compatible for JSON clients.

How to search:
  - "pydantic optional field default None"

-------------------------------------------------------------------------------
Task 3 — Call readme fetch during scan loop
-------------------------------------------------------------------------------
What:
  - In the same loop where you set `structure_report`, call your readme_client
    for allowed indices only (rate cap).

How to search:
  - Copy pattern from `inspect_repo` try/except in `scan.py`.

-------------------------------------------------------------------------------
Task 4 — Run readme_signals on excerpt
-------------------------------------------------------------------------------
What:
  - Produce extra issues or attach to repo before `detect_issues` / or merge
    inside `detect_issues` by passing excerpt.

How to search:
  - Read `src/scoring/issues.py` — decide extend vs separate function.

-------------------------------------------------------------------------------
Task 5 — Scoring impact (optional in Phase 2)
-------------------------------------------------------------------------------
What:
  - Either add `score_evidence` lines only, or small penalty in `scorer.py`.
    Document the rule in `docs/TASKS_SCORE_BREAKDOWN.md` style.

How to search:
  - Read `src/scoring/scorer.py` and `build_score_evidence`.

-------------------------------------------------------------------------------
Task 6 — Voiceflow flat payload (optional)
-------------------------------------------------------------------------------
What:
  - If you want one line for the whole account, extend `VoiceflowScanResponse`
    in `voiceflow_scan_response.py` (new keys) and document in AGENT_INTEGRATION.

How to search:
  - Read `src/contracts/voiceflow_scan_response.py`

-------------------------------------------------------------------------------
Task 7 — Streamlit (optional)
-------------------------------------------------------------------------------
What:
  - Show excerpt expander per repo or skip until Phase 4.

How to search:
  - `streamlit_app.py` patterns you already have.

-------------------------------------------------------------------------------
This module is documentation-only until you add real imports and wiring.
-------------------------------------------------------------------------------
"""
