# team-lead

Orchestrator skill. It analyzes a development request and routes it through
specialized agents **adaptively**: a simple request goes to the one best-fit
agent; a complex one becomes a chain (pipeline) where each stage's output feeds
the next. Every step is logged to `.claude/logs/log_agents.log`. The team-lead
routes and sequences work — it never writes code or does the task itself.

## Triggers

- "team lead", "тимлид"
- "оркеструй", "распредели задачу", "делегируй", "кому отдать эту задачу"
- "who should do this", "route this task", "pick an agent for this"
- Any build/fix/review task handed over without naming an agent

## Does not trigger for

- A specific agent or skill the user named explicitly
- Plain questions (no work to delegate)
- Commits (use `git-commit`), PRs (use `git-pr`), releases (use `git-release`)

## How it works

1. **Analyze** — classify the task type, restate it, decide simple vs complex.
2. **Plan** — project-local agents in `.claude/agents/` first, then base agents
   as fallback. Simple → one agent; complex → an ordered chain of stages
   (honouring design-before-impl, schema-before-code, impl-before-review,
   validation-last), with parallel stages where they have no dependency.
3. **Execute** — invoke each stage via the Agent tool with the task passed
   verbatim, threading the prior stage's output into the next as handoff
   context.
4. **Log** — append a JSON Lines event for every step to
   `.claude/logs/log_agents.log` (`start_work`, `analyze`, `plan`,
   `agent_start`, `agent_complete`, `agent_handoff`, `workflow_complete` /
   `error`), grouped under one `workflow_id`.

## Output

A strict JSON object — `{ analysis, plan, execution, outcome }` — and nothing
else. `analysis.complexity` is `simple` | `complex`; `plan` and `execution` are
arrays of stages (one element for a simple run); the top-level `outcome` is
`success` | `blocked` | `partial`. On routing failure it returns
`{ "error": { "reason": "no agent found" } }`.

## Installation

Picked up automatically after `make install` at the repository root.

## Notes

- `agent-builder` is never invoked from here — it may only be started by the
  user directly.
- This skill replaces the former `team-lead` agent; orchestration now runs in
  the main conversation rather than an isolated subagent.
