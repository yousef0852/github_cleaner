"""
readme_client — fetch README (or fallback) text for one repo via GitHub API.

Total tasks for YOU to implement: **5**

-------------------------------------------------------------------------------
Task 1 — Discover the right GitHub API for file content
-------------------------------------------------------------------------------
What:
  - Given owner, repo, and a GitHub HTTP client you already have, learn how to
    GET README body (markdown) without cloning.

How to search:
  - Docs: "GitHub REST API repository README"
  - Endpoint is typically GET /repos/{owner}/{repo}/readme (returns base64
    content in JSON). Alternatively raw.githubusercontent.com (no JSON).

-------------------------------------------------------------------------------
Task 2 — Map response to plain text
-------------------------------------------------------------------------------
What:
  - Decode base64 if using the REST README endpoint, or read raw bytes as UTF-8
    with a safe fallback (replace errors).

How to search:
  - "GitHub API readme content base64 decode python"
  - httpx response handling in your existing `github_client.py` patterns.

-------------------------------------------------------------------------------
Task 3 — Truncate and store excerpt only
-------------------------------------------------------------------------------
What:
  - Accept max_chars (e.g. 8000). If longer, cut and optionally add "…".

How to search:
  - "python truncate string max length"

-------------------------------------------------------------------------------
Task 4 — Handle missing README / 404
-------------------------------------------------------------------------------
What:
  - If README missing, return None or empty excerpt without crashing the scan.

How to search:
  - "GitHub API readme 404"

-------------------------------------------------------------------------------
Task 5 — Rate-limit batching (design only in this module or in caller)
-------------------------------------------------------------------------------
What:
  - Do not fetch README for every repo blindly. Accept a policy: e.g. only
    first N repos by your existing inspect order, or only showcase/cleanup.

How to search:
  - Read `MAX_REPOS_TO_INSPECT` in `api/routes/scan.py` and mirror the idea.

-------------------------------------------------------------------------------
After implementing: import from `data.github_client` or extend it; keep this
module focused on "get text" only — not scoring.
-------------------------------------------------------------------------------
"""
