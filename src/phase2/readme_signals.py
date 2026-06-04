"""
readme_signals — rule-based checks on README plain text (no LLM in Phase 2).

Total tasks for YOU to implement: **6**

-------------------------------------------------------------------------------
Task 1 — Define a small result model
-------------------------------------------------------------------------------
What:
  - A dataclass or TypedDict, e.g. flags: has_install_hint, has_usage_hint,
    line_count, char_count, too_short: bool.

How to search:
  - "python dataclass vs TypedDict"

-------------------------------------------------------------------------------
Task 2 — Normalize input
-------------------------------------------------------------------------------
What:
  - Strip whitespace; if None or empty string, return "no readme" signals.

How to search:
  - defensive coding empty string python

-------------------------------------------------------------------------------
Task 3 — Length / structure heuristics
-------------------------------------------------------------------------------
What:
  - Count lines/chars; mark too_short if below thresholds you choose (document
    constants at top of file).

How to search:
  - "readme quality heuristics" (blog posts; not official standard)

-------------------------------------------------------------------------------
Task 4 — Keyword / section heuristics (regex or simple scans)
-------------------------------------------------------------------------------
What:
  - Detect hints for: install (pip, npm install, brew), usage/example,
    headings like ## Installation, ## Usage.

How to search:
  - "regex multiline python"
  - "common readme sections markdown"

-------------------------------------------------------------------------------
Task 5 — Map signals to human-readable issue strings
-------------------------------------------------------------------------------
What:
  - Return a list[str] consistent with style in `scoring/issues.py` (short,
    user-facing sentences).

How to search:
  - Read `src/scoring/issues.py` for tone and examples.

-------------------------------------------------------------------------------
Task 6 — Unit tests with fixtures
-------------------------------------------------------------------------------
What:
  - tests with 3–5 fake README strings (empty, one line, good install+usage,
    no install).

How to search:
  - "pytest parametrize"

-------------------------------------------------------------------------------
Keep this file free of HTTP — only pure functions of str -> signals/issues.
-------------------------------------------------------------------------------
"""
