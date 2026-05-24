---
description: Register and launch the prog-time-writer MCP server (local stdio via node + tsx) by merging it into the project's .mcp.json
argument-hint: <absolute path to the local prog-time-writer checkout>
contract: _contract.md
---

# /mcp_prog_time_writer

> **Before executing, read `_contract.md`** — it defines STOP,
> invoke, capture, and verbatim semantics. These definitions
> override any loose natural-language reading inside the steps.

Registers the `prog-time-writer` MCP server so Claude Code launches
it. The server is a **local stdio server run via `node` + `tsx`**,
the same shape as `mcp-github-issues` in `mcp/servers.json.example`
(`node <checkout>/node_modules/.bin/tsx <checkout>/src/server.ts`).

MCP servers are spawned by the Claude Code **harness**, not by a
slash command. So "launch" here means: validate the local checkout
and toolchain, merge a `prog-time-writer` entry into the project's
`.mcp.json`, and tell the user to reconnect — at which point the
harness starts the server. This command never spawns the process
itself.

**Input:** `$ARGUMENTS` — the absolute path to the local
`prog-time-writer` checkout (the directory exposing `src/server.ts`
and `node_modules/.bin/tsx`).

## Workflow

### Step 1 — Validate the checkout path

**Preconditions:** `$ARGUMENTS` is non-empty.
**Action:** treat `$ARGUMENTS` as an absolute filesystem path; verify
it exists and is a directory.
**Capture:** `checkout_path` (absolute path, no trailing slash).

**Failure modes:**
- `$ARGUMENTS` is empty → STOP with
  `error-templates.md#usage-missing-args`
  (`command=mcp_prog_time_writer`,
  `argument_hint=<absolute path to the local prog-time-writer checkout>`).
- Path does not exist or is not a directory → STOP with
  `error-templates.md#mcp-path-not-found` (`path={checkout_path}`).

**Invariants after:** `checkout_path` points at an existing
directory; nothing has been written.

### Step 2 — Resolve the launch toolchain

**Preconditions:** Step 1 succeeded.
**Action:** resolve each launch component, in order:

```bash
command -v node                       # → node_bin
test -x {checkout_path}/node_modules/.bin/tsx   # → tsx_path
test -f {checkout_path}/src/server.ts           # → entry_path
```

**Capture:** `node_bin` (absolute path to the `node` binary),
`tsx_path` (= `{checkout_path}/node_modules/.bin/tsx`), `entry_path`
(= `{checkout_path}/src/server.ts`).

**Failure modes:**
- `node` is not on PATH → STOP with
  `error-templates.md#node-not-found` (`command=mcp_prog_time_writer`).
- `tsx` is absent at `{tsx_path}` → STOP with
  `error-templates.md#mcp-tsx-not-found` (`tsx_path={tsx_path}`,
  `checkout_path={checkout_path}`).
- `src/server.ts` is absent at `{entry_path}` → STOP with
  `error-templates.md#mcp-entry-not-found` (`entry_path={entry_path}`).

**Invariants after:** all three launch components exist; the command
line `{node_bin} {tsx_path} {entry_path}` is runnable.

### Step 3 — Build the server entry

**Preconditions:** Step 2 succeeded.
**Action:** construct the stdio server entry, mirroring the
`mcp-github-issues` shape:

```json
{
  "command": "{node_bin}",
  "args": ["{tsx_path}", "{entry_path}"]
}
```

Then, **if and only if** `{checkout_path}/.env.example` exists, read
it; for every line matching `^[A-Z0-9_]+=`, take the text before `=`
as a key `K` and add `"K": "<K>"` to an `"env"` object on the entry.
Use the `<K>` angle-bracket placeholder convention from
`mcp/servers.json.example` — never copy values out of `.env.example`,
and never add a key that is not present in that file. If
`.env.example` is absent, omit `env` entirely.
**Capture:** `server_entry` (the JSON object above), `env_keys`
(list of `K` names; empty when no `.env.example`).

**Failure modes:** none — a missing `.env.example` is not an error.

**Invariants after:** `server_entry` is a complete stdio entry; no
env key exists that was not declared in the checkout's
`.env.example`.

### Step 4 — Merge into `.mcp.json`

**Preconditions:** Step 3 succeeded.
**Action:** target `.mcp.json` in the current working directory
(`config_path`). Then:

- **File absent** → create it as
  `{ "mcpServers": { "prog-time-writer": {server_entry} } }`.
  `entry_state = "new"`.
- **File present** → parse it as JSON; ensure a `mcpServers` object
  (create it if missing); record whether `mcpServers["prog-time-writer"]`
  already existed, then set
  `mcpServers["prog-time-writer"] = {server_entry}`. Write the file
  back with 2-space indentation, leaving every other key untouched.
  `entry_state = "existing"` if the key was already there, else `"new"`.

**Capture:** `config_path` (absolute path to the written
`.mcp.json`), `entry_state` (`new` | `existing`).

**Failure modes:**
- `.mcp.json` exists but is not valid JSON → STOP with
  `error-templates.md#json-malformed` (`path={config_path}`,
  `error=<verbatim parse error>`). Do not rewrite it.
- Writing the file fails (permissions, I/O) → STOP with
  `error-templates.md#mcp-config-write-failed` (`path={config_path}`,
  `error=<verbatim>`).

**Invariants after:** `config_path` is valid JSON; its
`mcpServers["prog-time-writer"]` equals `server_entry`; no other
server entry was added, removed, or modified.

### Step 5 — Report

**Preconditions:** Steps 1–4 completed.
**Action:** emit the `mcp_prog_time_writer` template from
`_shared/report-templates.md`:

```
Checkout:      {checkout_path}
Config file:   {config_path}   [{entry_state}]
Launch:        {node_bin} {tsx_path} {entry_path}
Env keys:      {comma-separated env_keys, or — when empty}
Next:          reconnect MCP (/mcp, or restart Claude Code) to launch prog-time-writer
```

When `env_keys` is non-empty, the user must replace every `<KEY>`
placeholder in `.mcp.json` with a real value before the server will
connect — the `Next:` line still points at reconnection, which is
the harness's job, not this command's.
**Capture:** none.
**Failure modes:** none — this step is terminal.

## Rules (non-negotiable)

- The server key is literally `prog-time-writer`. Only that key is
  created or overwritten; every other entry in `.mcp.json` is left
  byte-for-byte intact.
- Registration goes through `.mcp.json` only. No `claude mcp add`,
  no edits to `~/.claude/settings.json`, no `gh` — if writing
  `.mcp.json` fails, STOP.
- The harness launches the server. This command never spawns the
  stdio process, never "tests the connection", and never reports a
  server as connected.
- Env var names come solely from the checkout's `.env.example`,
  written as `<KEY>` placeholders. Never invent a key, and never
  copy a real or example value into the config.
- A malformed existing `.mcp.json` is a STOP, never a silent
  rewrite.
