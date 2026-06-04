# Module Definitions

## 1. `contracts`

**Purpose:** Single source of truth for request/response and shared DTOs.

- `scan_request.py` — `ScanRequest`: github_username, review_mode, scan_scope.
- `scan_response.py` — `ScanResponse`, `Summary`, `RepoResult`, etc.
- `repo_dto.py` — `RepoDTO`: raw repo data from GitHub (name, description, stars, forks, last_commit, language, has_readme, has_license).

**Dependencies:** None (only Pydantic + stdlib).

---

## 2. `data`

**Purpose:** Fetch repository metadata from GitHub. Read-only.

- `github_client.py` — HTTP client for GitHub REST API.
- `repo_fetcher.py` — Fetch all repos for a user, map to `RepoDTO`.

**Dependencies:** `contracts` (RepoDTO). Uses `httpx`, optional `GITHUB_TOKEN` env.

---

## 3. `scoring`

**Purpose:** Deterministic scoring, classification, issue detection, suggestions.

- `scorer.py` — Score 0–100 from RepoDTO (documentation, activity, structure, naming, portfolio value).
- `classifier.py` — Map score + rules → showcase | cleanup | archive.
- `issues.py` — Detect issues (missing README, no description, inactive, etc.).
- `suggestions.py` — Generate suggestions per repo (add README, improve description, etc.).
- `aggregator.py` — Build summary counts, top issues, recommended_next_step.

**Dependencies:** `contracts` (RepoDTO, RepoResult). No HTTP, no GitHub.

---

## 4. `api`

**Purpose:** FastAPI app and orchestration.

- `main.py` — App factory, lifespan.
- `routes/scan.py` — POST /scan: validate ScanRequest → data.fetch → scoring → ScanResponse.
- `dependencies.py` — Inject GitHub client, optional config.

**Dependencies:** `contracts`, `data`, `scoring`.

---

## 5. Agent (external)

**Purpose:** Conversation, tool calls to Backend API, explain results.

- Integration: POST to `/scan` with JSON body (ScanRequest).
- No logic here; only calls API and formats for user.
