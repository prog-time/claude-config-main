---
name: rules-generator
description: |
  Orchestrates generation of a complete `rules/` AI knowledge base for a
  project: handles pre-checks (existing `rules/`, monorepo, template path),
  then delegates the codebase analysis and file generation to the
  `rules-writer` agent via the Agent tool, and relays its report. Use ALWAYS
  when the user says "generate rules", "generate rules for this project",
  "create a rules/ directory", "document the codebase for AI agents", "set up
  an AI knowledge base", "сгенерируй rules", "создай rules", "построй rules/",
  "документируй проект для AI", "сделай AI knowledge base", or asks to
  bootstrap AI-ready project documentation derived from real code. Do NOT use
  for: editing a single existing rules file (use Edit), writing a README or
  CHANGELOG (use docs-quality), authoring blog posts (use blog-article-writer),
  or creating skills/agents.
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
  - Agent
---

# Rules Generator

A thin orchestrator. It does **not** analyze code or write files itself — it
prepares the inputs, delegates the heavy work to the `rules-writer` agent (which
runs Phase 0 analysis and writes every file from the templates in an isolated
context), and relays the agent's JSON report.

The canonical templates ship with this skill, in `references/`. The agent reads
them; this skill just tells the agent where they are.

## Workflow

### Step 1 — Resolve the template directory

The templates live next to this `SKILL.md`, in `references/`. Resolve the
absolute path to that directory — this becomes `template_dir` for the agent.

### Step 2 — Resolve the target project root

Run `git rev-parse --show-toplevel`.

- Success → `target_root` is that path.
- Not a git repo → use the current working directory and warn the user that the
  location was inferred from CWD.

### Step 3 — Pre-checks (decide `mode`, never clobber silently)

- **`rules/` does not exist** → `mode: full`.
- **`rules/` already exists** → ask the user: overwrite (`full`), fill gaps only
  (`gap-fill`), or abort. Default to **abort** on no answer. Never silently
  overwrite.
- **Monorepo with multiple apps** → ask which app to document (set `target_root`
  to that app's root), or run once per app.

### Step 4 — Delegate to the `rules-writer` agent

Invoke the `rules-writer` agent via the Agent tool. Pass a self-contained prompt
with:

- **`template_dir`** — the absolute path from Step 1.
- **`target_root`** — from Step 2.
- **`mode`** — `full` or `gap-fill` from Step 3.
- **The user's original request**, verbatim.

The agent runs the full Phase 0 analysis, writes the mandatory structure from the
templates, lints the output, and returns a JSON completion report.

### Step 5 — Relay the report

Capture the agent's JSON report and present it. If the agent reports an error or
a blocking deviation, surface it; do not retry or write files yourself.

## Rules (non-negotiable)

- **Never analyze code or write `rules/` files yourself.** This skill routes —
  the `rules-writer` agent does the work.
- **Never overwrite an existing `rules/`** without explicit user choice
  (`full` vs `gap-fill` vs abort).
- **Always pass `template_dir`** so the agent reads the canonical templates,
  never invents structure.
- **Do not invoke `agent-builder`.**

## Examples

### Example 1 — Standard bootstrap

**User:** сгенерируй rules для этого проекта

**Assistant:** *(resolves `template_dir` and `target_root`, finds no existing
`rules/` → `mode: full`, delegates to the `rules-writer` agent, relays its JSON
report)*

### Example 2 — Existing rules/ present

**User:** create a rules/ directory

**Assistant:** "`rules/` already exists. Overwrite, fill gaps only, or abort?"
*(waits, then delegates to `rules-writer` with the chosen `mode`)*

### Example 3 — Monorepo

**User:** документируй проект для AI

**Assistant:** "This looks like a monorepo (`apps/web`, `apps/api`). Which app
should I document — or both?" *(delegates once per chosen app root)*

## Edge Cases

- **Not a git repo** — infer `target_root` from CWD and warn.
- **User requests partial output** (only schema, only API) — the `rules-writer`
  agent produces the complete mandatory structure; for targeted edits, point the
  user at Edit.
- **Agent returns a blocking error** — surface it verbatim; do not fall back to
  writing files inline.
