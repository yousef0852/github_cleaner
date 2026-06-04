# GitHub Cleaner AI — Architecture

## Overview

A layered system for analyzing GitHub profiles and recommending portfolio improvements. Core logic is **deterministic**; AI is used only for explanation and conversation.

---

## Layer Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 1 — Agent (Voiceflow / LLM)                              │
│  Conversation, user input, tool calls, result explanation        │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP / tool calls
┌────────────────────────────▼────────────────────────────────────┐
│  Layer 2 — Backend API (FastAPI)                                 │
│  Request validation, orchestration, response shaping             │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌───────────────┐   ┌────────────────┐   ┌──────────────────────┐
│ Layer 3       │   │ Contracts       │   │ Layer 4               │
│ Scoring       │   │ (Pydantic)      │   │ Data (GitHub API)     │
│ Engine        │   │ Input/Output    │   │ Repo fetch, no writes │
└───────────────┘   └────────────────┘   └──────────────────────┘
```

---

## Module Boundaries

| Module | Path | Responsibility |
|--------|------|----------------|
| **api** | `src/api/` | FastAPI app, routes, dependency injection |
| **contracts** | `src/contracts/` | Pydantic models for request/response |
| **scoring** | `src/scoring/` | Deterministic scoring, classification, issues, suggestions |
| **data** | `src/data/` | GitHub API client, repo metadata fetching |

**Rules:**

- API depends on contracts + scoring + data.
- Scoring depends only on contracts (repo DTOs).
- Data returns only contract/DTO types; no scoring logic.

---

## Data Flow (MVP — Read-Only)

1. Agent sends `ScanRequest` (username, review_mode, scan_scope).
2. API validates, calls Data layer → fetch repos from GitHub.
3. API passes repo list to Scoring engine → scores, classifications, issues, suggestions.
4. API builds `ScanResponse` and returns to agent.
5. Agent explains results to user (no destructive actions).

---

## Safety (MVP)

- **Read-only**: No GitHub write operations.
- **No destructive actions** in Phase 1.
- Future phases: preview-first, explicit confirmation for archive/rename/edit.

---

## Input Contract

```json
{
  "github_username": "string",
  "review_mode": "portfolio | cleanup",
  "scan_scope": "public | all"
}
```

---

## Output Contract

```json
{
  "summary": {
    "total_repos": "number",
    "showcase_ready": "number",
    "needs_cleanup": "number",
    "archive_candidates": "number"
  },
  "top_issues": ["string", "..."],
  "repos": [
    {
      "name": "string",
      "score": "number",
      "classification": "showcase | cleanup | archive",
      "issues": ["string"],
      "suggestions": ["string"]
    }
  ],
  "recommended_next_step": "string"
}
```

---

## Tech Stack

- **Backend**: FastAPI, Pydantic
- **Data**: GitHub REST API (httpx), optional env token
- **Scoring**: Pure Python, no ML models
- **Agent**: External (Voiceflow/LLM); integrates via API

---

## Build Order

1. **Contracts** — Input/Output and repo DTOs.
2. **Data** — GitHub client, fetch repos (read-only).
3. **Scoring** — Score, classify, issues, suggestions.
4. **API** — Wire routes and dependencies.
5. **Agent** — Document integration and example tool call.
