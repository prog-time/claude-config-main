---
name: agent-builder
description: |
  Designs and writes Claude Code agent definition files (the .md files in
  agents/). Use ALWAYS when the user says "create an agent", "build an agent",
  "new agent", "design an agent", "improve the X agent", "refine the X agent",
  "добавь агента", "создай агента", "сделай агента", "переработай агента", or
  describes a specialized role they want a subagent to play. Walks through
  role clarification, fleet exploration, drafting, review, and file creation.
  Do NOT use for creating skills (use skill-creator), slash commands (use
  commands/), or editing unrelated Markdown.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Bash
---

# Agent Builder

Author high-quality Claude Code agent definition files — the `.md` files in
`agents/` that define how specialized subagents behave. Produce agents that are
precise, non-overlapping, and immediately usable.

## Absolute Rules

1. **Markdown only.** Create or edit files with the `.md` extension. Never
   write `.ts`, `.py`, `.json`, `.yaml`, `.sh`, or other non-Markdown files.
2. **Draft before writing.** Always present the full agent content to the user
   and get confirmation before writing it to disk.
3. **No duplicates.** Read the existing fleet in `agents/` first. If the
   requested role overlaps an existing agent, propose extending that agent
   instead of creating a new one.

## Workflow

### Step 1 — Read the existing fleet

Before designing anything:

1. `ls agents/` and read every existing `.md` file to understand:
   - Which roles are already covered.
   - Conventions used (structure, tone, naming, colors).
   - Which colors are already taken — the new agent needs an unused one.
2. Identify overlap. If the request duplicates an existing agent, stop and
   propose extending the existing one.

### Step 2 — Clarify the role

Answer these before writing anything. Ask the user if any are unclear:

- What is the single focused responsibility of this agent?
- What does it produce? (files, reports, commits, decisions, code)
- What triggers it? List 2–3 concrete user requests.
- What should it never do? (to avoid overlap)
- Is it a pipeline agent (the team-lead skill can route to it) or standalone?

### Step 3 — Design the structure

Plan every section before drafting:

- Frontmatter (name, description, model, color, memory)
- Role sentence
- Core Responsibilities (3–7 items)
- Step 0 exploration (specific to the agent's domain)
- Workflow (steps or modes)
- Rules (if applicable)
- Output format (if producing structured reports)
- Self-verification checklist
- Persistent memory section

### Step 4 — Draft and present

Write the full agent content in chat and show it to the user. Invite feedback.
Apply corrections. Do NOT write the file yet.

### Step 5 — Write the agent file

After explicit confirmation, write to `agents/<name>.md` using the canonical
structure below.

### Step 6 — Update the team-lead skill if needed

If the new agent is a pipeline agent (one the team-lead skill can route to):

- Read `skills/team-lead/SKILL.md`.
- Add the agent to the Step 2 routing table (`Task type` → `Best-fit agent`).
- If the agent introduces a new sequencing constraint, note it under the
  ordering rules.

### Step 7 — Lint

Validate the new agent's frontmatter with the repository linter:

```bash
make lint        # or: python3 scripts/lint_skills.py
```

This checks frontmatter validity, `description` length (≤ 1024 chars), and that
`name` matches the file stem. Fix any reported errors before continuing.

### Step 8 — Offer to commit

Ask whether the user wants to commit the new/changed `.md` files. Do not
commit without explicit confirmation.

## Canonical Agent Structure

Every agent file must follow this structure, in order.

### 1. Frontmatter

```yaml
---
name: <agent-name>
description: "<trigger description with 2-3 <example> blocks>"
model: sonnet
color: <unused color>
memory: user
---
```

- **Colors:** red, orange, yellow, green, blue, purple, cyan, pink, gray, white.
- **Model:** default `sonnet` unless there is a specific reason for `opus` or `haiku`.
- **memory:** always `user`.

### 2. Role definition

```markdown
You are a <Role Title>. Your role is to <one sentence: what you do and what you produce>.

**You work with any project and any technology stack.** <one sentence on approach>.
```

### 3. Core Responsibilities

Numbered list of 3–7 items. Each: `**Verb** — description.`

### 4. Step 0 — Always Explore the Project First

What the agent must read before acting. Typical checks:

- `CLAUDE.md`, `README.md`, `rules/`, `docs/`
- Stack detection files
- Relevant source directories
- Agent memory for prior findings

### 5. Workflow

Use **Steps** for linear flows, **Modes** for multi-mode agents. Each step
must be concrete and actionable.

### 6. Rules (if applicable)

Numbered list with bold headers for non-negotiable constraints.

### 7. Output Format (if applicable)

Exact Markdown format inside a fenced code block when the agent produces
structured reports.

### 8. Self-Verification Checklist

```markdown
## Self-Verification Before <action>

- [ ] Specific binary check
- [ ] Specific binary check
```

### 9. Persistent Agent Memory

Use this template (replace `<name>`):

```markdown
## Persistent Agent Memory

You have a persistent memory directory at the agent-memory path for <name>.

Use it to track:
- <what to save, specific to this agent's role>

Guidelines:
- MEMORY.md is always loaded — keep it concise (under 200 lines)
- Create separate topic files and link from MEMORY.md
- Update or remove entries that turn out to be wrong
- Organize by project name when working across projects
```

## Description Writing Rules

The `description` field controls when Claude invokes the agent. Write it
carefully.

**Structure:**

1. One sentence starting "Use this agent when..." covering triggers.
2. 2–3 `<example>` blocks, each for a different scenario.

**Each example:**

```markdown
<example>
Context: [one sentence setting the scene]
user: "[realistic user message]"
assistant: "[how the assistant responds, naming the agent]"
<commentary>
[Why this agent is the right choice. What it will do.]
</commentary>
</example>
```

**Rules:**

- Realistic scenarios with concrete domain language — no generic placeholders.
- Every example covers a different trigger.
- Commentary explains the agent's approach, not just its name.

## Anti-Patterns to Avoid

| Anti-pattern | Fix |
|---|---|
| Agent does everything | Split into focused agents |
| Vague description | Rewrite with concrete triggers and examples |
| No Step 0 exploration | Always add project exploration |
| Checklist items are vague | Make each binary and specific |
| Missing output format | Define the exact Markdown structure |
| Color already used | Check the fleet, pick an unused color |
| Overlaps existing agent | Extend the existing agent instead |
| File written before confirmation | Draft → present → confirm → write |

## Self-Verification Before Saving

- [ ] Only `.md` files were created or modified
- [ ] All existing agents in `agents/` were read before designing
- [ ] The new agent does not duplicate an existing role
- [ ] Frontmatter is complete: name, description, model, color, memory
- [ ] Color is not used by any other agent in the fleet
- [ ] Description has 2–3 `<example>` blocks with realistic scenarios
- [ ] Role definition is one focused sentence
- [ ] Core Responsibilities are 3–7 bold-verb items
- [ ] Step 0 exploration is present and specific to the domain
- [ ] Workflow steps are concrete and actionable
- [ ] Self-verification checklist items are binary and specific
- [ ] Persistent memory section uses the correct path
- [ ] Agent file was presented to the user and confirmed before writing
- [ ] If pipeline agent: the routing table in `skills/team-lead/SKILL.md` was updated
- [ ] `make lint` passed with no errors
- [ ] User was asked whether to commit

## Examples

### Example 1 — Fleet overlap

**User:** create an agent that reviews database migrations

**Assistant:** *(reads `agents/`)* The existing `db-agent` already covers
migration review. I recommend extending `db-agent` with an explicit "review
mode" section rather than creating a new agent. Want me to draft that change?

### Example 2 — New role, clear scope

**User:** we need something that monitors and summarizes CI/CD failures

**Assistant:** No existing agent covers CI/CD monitoring. I'll design a
`ci-monitor` agent. Quick questions before I draft:

1. Does it run on demand, or scheduled?
2. What output — a report, a Slack-style summary, or a task file?
3. Which CI systems (GitHub Actions, GitLab, CircleCI)?

### Example 3 — Vague request

**User:** make an agent that helps with backend

**Assistant:** Too broad — "helps with backend" overlaps with `backend-agent`,
`db-agent`, `api-designer`, and `perf-agent`. What is the single task? Examples:
"reviews SQL query plans", "writes repository layer code", "audits REST
endpoints for REST conventions".

## Edge Cases

- **Agent name already exists** — ask whether to extend the existing agent or
  pick a new name. Never silently overwrite.
- **Request is actually a skill** — skills (auto-triggered workflows) go in
  `skills/`. Point the user to the `skill-creator` skill.
- **Request is actually a slash command** — slash commands go in `commands/`.
- **User wants to edit `agent-builder.md` itself** — apply minimal targeted
  edits and show the diff before writing.
