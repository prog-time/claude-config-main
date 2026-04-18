# Sub-agent design

## When to use a skill vs. an agent

- A **skill** is "trigger + instruction". It activates automatically based on
  its `description` and runs inside the main Claude session.
- An **agent** is a standalone sub-session with its own context and its own
  set of tools. It is launched via the `Agent` tool.

Rule of thumb: if the task needs its own context, a multi-step process, or
isolation — it is an agent. If a short instruction inside the main session is
enough — it is a skill.

## The "router → agent" pattern

A handy pattern: a lightweight skill with an aggressive `description` catches
the request and immediately delegates to an agent of the same name. This way
activation is reliable, while all the heavy logic lives in the agent, where
it is easier to restrict tools and model.

Example: a lightweight router skill catches the request and delegates to an
agent of the same name.

## When to introduce a new agent

- The same task shows up across several skills in an identical way — extract
  it into an agent.
- You need a separate context / model / toolset.
- The pipeline has 3+ steps with its own memory.

## Things to avoid

- One agent = one area of responsibility. Do not build a "do-everything" god
  agent.
- Do not give the agent more tools than it needs (`tools:` in frontmatter).
- Do not call agents recursively without a clear exit condition.

## Agent file layout

Claude Code only discovers agents from `.md` files at the top level of
`agents/`. Subdirectories are never scanned for agent definitions. This
dictates the layout:

- **Simple agent:** a single file `agents/<name>.md`. No directory.
- **Agent with private resources** (stack profiles, reference snippets,
  prompts loaded on demand): a file `agents/<name>.md` **plus** a
  directory `agents/<name>/` of the same name, read by the agent itself
  via `Read`. Example: `agents/backend-agent.md` +
  `agents/backend-agent/{php,python}.md`.
- **Shared export assets** (README/CHANGELOG/PR templates that the agent
  copies into *other* projects) do not belong under `agents/`. They
  live in the repo-root `templates/` directory — shared and
  discoverable by any skill or agent.

This is the agent equivalent of the `skills/<name>/references/` pattern
skills use. The difference is cosmetic: the `.md` stays at the top
level because the platform requires it.
