# agent-builder

A meta-skill that designs and writes Claude Code agent definition files — the
`.md` files under `agents/`. Walks through fleet exploration, role
clarification, drafting, review, and file creation.

## Triggers

- "create an agent", "build an agent", "new agent", "design an agent"
- "improve the X agent", "refine the X agent", "extend the X agent"
- "создай агента", "сделай агента", "добавь агента", "переработай агента"
- Any description of a specialized role the user wants a subagent to play.

## Does not trigger for

- Creating **skills** — use the `skill-creator` skill.
- Creating **slash commands** — use `commands/`.
- Editing unrelated Markdown files.

## What it produces

A fully-formed `agents/<name>.md` file containing:

- Frontmatter with `name`, `description` (2–3 `<example>` blocks), `model`,
  unused `color`, and `memory: user`.
- Role sentence, Core Responsibilities, Step 0 exploration.
- Workflow, Rules, Output format, Self-verification checklist.
- Persistent memory section.

Optionally, an updated routing table in `skills/team-lead/SKILL.md` if the
agent is a pipeline agent.

## Workflow summary

1. Read every file in `agents/` to understand conventions and detect overlap.
2. Clarify role, output, triggers, exclusions, and pipeline fit.
3. Draft the full agent content and present to the user.
4. Write `agents/<name>.md` only after explicit confirmation.
5. Update the routing table in `skills/team-lead/SKILL.md` when the agent
   belongs in the orchestration pipeline.
6. Run `make lint` to validate the agent's frontmatter.
7. Offer to commit — never commit without confirmation.

## Installation

Picked up automatically after `make install` at the repository root.
