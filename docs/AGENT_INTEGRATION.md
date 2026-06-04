# Layer 1 — Agent Integration

The backend is **read-only** and stateless. The agent (Voiceflow, custom LLM, or any client) calls the API and explains results to the user.

**Production example:** `https://github-cleaner-api.onrender.com` — use **`POST …/scan/voiceflow`** for Voiceflow (flat JSON). **Local:** `http://127.0.0.1:8000`.

## API contract

- **Base URL**: `http://localhost:8000` (local) or your **Render / other host** HTTPS URL
- **Health**: `GET /health` → `{"status": "ok"}`

### Scan endpoint

- **Method**: `POST /scan`
- **Request body** (JSON):

```json
{
  "github_username": "octocat",
  "review_mode": "portfolio",
  "scan_scope": "public"
}
```

| Field             | Type                         | Description                                       |
| ----------------- | ---------------------------- | ------------------------------------------------- |
| `github_username` | string                       | GitHub username (required)                        |
| `review_mode`     | `"portfolio"` \| `"cleanup"` | Focus of the review                               |
| `scan_scope`      | `"public"` \| `"all"`        | Repos to include; `"all"` requires `GITHUB_TOKEN` |

- **Response** (200):

```json
{
  "summary": {
    "total_repos": 10,
    "showcase_ready": 2,
    "needs_cleanup": 5,
    "archive_candidates": 3
  },
  "top_issues": [
    "Missing README",
    "No or very short description",
    "Inactive for over 12 months"
  ],
  "repos": [
    {
      "name": "my-project",
      "score": 85.0,
      "classification": "showcase",
      "issues": [],
      "suggestions": ["Add repository topics for discoverability"],
      "structure_report": {
        "has_files": {
          "readme": true,
          "license": true,
          "gitignore": true,
          "deps": true,
          "tests": false,
          "docs": false,
          "src_layout": true
        },
        "has_folders": { "tests": false, "docs": false, "src": true },
        "has_files_and_folders": {}
      }
    }
  ],
  "recommended_next_step": "Focus on cleaning up repos: add READMEs and descriptions..."
}
```

Each `repos[]` item may include **`structure_report`**: root-level file/folder evidence from the GitHub Contents API (`has_files`, `has_folders`, `has_files_and_folders`). It is **`null`** if inspection failed for that repo, or if the repo is beyond the server’s inspection limit (first **40** repos per scan are inspected; all repos are still scored). The scan still succeeds for the full repo list.

- **Errors** (JSON body is always an object with a **`detail`** field unless noted):

| Code | When | Example body |
| ---- | ---- | ------------- |
| **400** | Invalid request or `scan_scope: "all"` without `GITHUB_TOKEN` on the server | `{"detail": "scan_scope 'all' requires GITHUB_TOKEN to be set"}` |
| **404** | GitHub has no user for that username (public lookup) | `{"detail": "GitHub user not found"}` |
| **422** | Pydantic validation (bad JSON shape, empty username, etc.) | `{"detail": [ { "loc": [...], "msg": "...", "type": "..." } ]}` — **`detail` is a list** here |
| **502** | GitHub API failure, rate limit, bad token, network, etc. | `{"detail": "GitHub API error: ..."}` |

Use **`detail`** in no-code tools: if it’s a **string**, show it to the user or map it to a friendly message. If **`detail`** is an **array** (422), show a generic “check username and JSON body” message.

### Voiceflow / no-code: flat response

Use **`POST /scan/voiceflow`** when your client (e.g. Voiceflow) maps **one JSON field → one variable** and does not handle nested objects or arrays well.

- **Request body**: Same as `POST /scan` (see above).
- **Response** (200): **Scalars only** — no `summary`, `repos`, or `top_issues` arrays.

Example:

```json
{
  "total_repos": 10,
  "showcase_ready": 2,
  "needs_cleanup": 5,
  "archive_candidates": 3,
  "top_issue_1": "Missing README",
  "top_issue_2": "No or very short description",
  "top_issue_3": "Inactive for over 12 months",
  "recommended_next_step": "Focus on cleaning up repos: add READMEs...",
  "archive_repo_1": "old-fork",
  "archive_repo_2": "empty-prototype",
  "cleanup_repo_1": "needs-readme",
  "cleanup_repo_2": "short-desc",
  "showcase_repo_1": "best-project",
  "showcase_repo_2": "next-best"
}
```

Empty slots use `""`. **`archive_repo_*` / `cleanup_repo_*`** are filled with repo **names** (lowest score first within each classification). **`showcase_repo_*`** are the **highest-scoring** showcase repos (best first). Same errors as `POST /scan`.

## Agent behavior rules

1. **No destructive actions** — Do not call any endpoint that modifies GitHub (there are none in MVP). Do not tell the user you will archive/rename/edit repos; only suggest and explain.
2. **Explain from data** — For `POST /scan`, use `summary`, `top_issues`, `repos[].issues`, `repos[].suggestions`, and `recommended_next_step`. For `POST /scan/voiceflow`, use the flat `total_repos`, `top_issue_1..3`, `recommended_next_step`, `showcase_repo_1..2`, and cleanup/archive repo slots. Do not invent scores or issues.
3. **Prioritize** — Use `classification` and `score` to order what to talk about (e.g. showcase first, then cleanup, then archive).
4. **Confirm scope** — Before calling `/scan`, confirm username and whether they want public-only or all repos (if they have a token).

## Example tool definition (for LLM/Voiceflow)

- **Name**: `scan_github_profile`
- **Description**: Scan a GitHub user's repositories and get a portfolio audit: scores, classifications, issues, and recommendations.
- **Input**: `github_username` (required), `review_mode` (optional, default `portfolio`), `scan_scope` (optional, default `public`).
- **Action**: POST to `{BASE_URL}/scan` (full JSON) or `{BASE_URL}/scan/voiceflow` (flat fields for Voiceflow); return the response to the user in clear language.

## Safety (MVP)

- The API only **reads** from GitHub. No write operations.
- Future phases will add guided cleanup or safe execution; those will use separate endpoints and **preview + confirmation** before any change.
