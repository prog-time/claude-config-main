# Command Execution Contract

This document defines the canonical semantics used by every `/task_*`
command in this directory. Each command's frontmatter line
`contract: _contract.md` is a machine-readable pointer to this file,
and the command body says at the top:

> Before executing, read `_contract.md` — it defines STOP, invoke,
> capture, and verbatim semantics. These definitions override any
> loose natural-language reading inside the steps.

Rules below are **non-negotiable**. When a step's instruction could
be read two ways, the narrower reading that matches this contract
wins.

## 1. STOP

`STOP` means: halt the command immediately and do nothing else for
this invocation.

Specifically:

- **No retry** of the failed step, the previous step, or the whole
  command. Not even with adjusted arguments.
- **No "creative workaround".** Do not substitute the failed tool
  with another one (e.g., no `gh` CLI when MCP failed, no `git
  reset` when merge failed, no `--no-verify` when hook failed).
- **Surface the underlying error verbatim** in the final message —
  tool error text, stderr, MCP response — exactly as received, in a
  fenced code block.
- **No side-effect cleanup** beyond what is already required by the
  step's own "Failure modes" entry. Do not delete files, reset
  branches, or close draft issues to "tidy up".
- **Do not mark the user's task as done** in any external tracker;
  `STOP` is a failure outcome.

`STOP` is always terminal. If a command lists multiple failure
modes, the first one that matches wins — execution does not fall
through to the next one.

## 2. Invoke `/<command>`

When a step says `Invoke /<command>` (or "delegate to
`/<command>`"), the semantics are:

- **Transfer of responsibility.** The invoking command does not
  re-perform any check that the invoked command already performs at
  its own gates. Duplication is wasted work and a source of
  divergence.
- **Run to completion or STOP.** The invoked command runs under the
  same contract. If it STOPs, the invoking command also STOPs — it
  does not "retry differently" or fall back to an inline path.
- **Consume only the named outputs.** The invoking step must
  explicitly list the variables it captures from the invoked
  command's report (e.g., `pr_url`, `issue_number`). Any other
  fields from the invoked command's output are ignored.
- **No parallel fallback.** A command never implements a shadow
  version of what the invoked command does, "in case it isn't
  available". If the invoked command is missing, STOP with a clear
  error.

## 3. Capture as `<var>`

When a step says `Capture as <var>` or has a `Capture:` block, the
semantics are:

- **Named output.** The variable is part of the step's formal
  output. It must be referenceable by name from later steps.
- **Explicit in the intermediate response.** When Claude executes
  the step, the captured value should appear in the user-facing
  text of that step (or, for silent runs, in the internal
  bookkeeping that is surfaced in the final report). Do not let a
  captured value stay implicit.
- **Never re-derived.** If a later step uses `issue_number`, it
  must use the exact integer captured earlier, not re-parse the
  input or the URL again.
- **Types are literal.** Numbers are integers. URLs include scheme
  and no trailing slash. Paths are repo-relative unless the step
  says otherwise.

## 4. Verbatim

When text is described as `verbatim`:

- **Quoted in a code fence** (triple backtick or inline backtick) →
  reproduce character-for-character, including punctuation,
  whitespace, line breaks, and trailing periods. Do not translate,
  paraphrase, or "improve" the wording.
- **Described in prose** (e.g., "the task file's body, verbatim") →
  copy the source content without summarisation, trimming, or
  reformatting. Only the transformation explicitly named by the
  step is allowed (e.g., "minus the H1 line").
- **User-facing messages quoted in code fences are final text.** Do
  not prefix them with phrases like "Error:" or "Note:" unless the
  template itself contains such a prefix.

## 5. Forbidden creativity

Commands are **workflow executors**, not optimisers. The following
are always forbidden unless a specific step explicitly permits
them:

- Adding "sanity checks" beyond the listed Preconditions.
- Suggesting or performing `--force`, `--force-with-lease`,
  `--no-verify`, `--no-gpg-sign`, `git reset --hard`, `git clean`,
  or any destructive git recovery.
- Falling back from MCP tools to `gh` CLI (or vice versa).
- Inventing identifiers: Issue numbers, PR numbers, project keys,
  branch names not derived from explicit inputs.
- Editing files outside what the step's `Action` describes.
- Asking the user mid-pipeline for data that could have been
  captured from earlier inputs. Ask only when the step's Failure
  modes explicitly require asking.
- Re-ordering steps, merging two steps, or "combining for
  efficiency".

## 6. Step anatomy

Every step in every command follows this shape:

```
### Step N — <verb phrase>

**Preconditions:** <state that must hold going in — verifiable>
**Action:** <single command, tool call, or sub-command invocation>
**Capture:** <named vars produced; or "none">
**Failure modes:**
  - <trigger> → STOP with template `<key from error-templates.md>`
  - <trigger> → STOP with message verbatim:
    ```
    <inline verbatim message>
    ```
**Invariants after:** <state guaranteed on success>
```

Not every block is mandatory in every step (e.g., a step that
captures nothing omits `Capture:`), but when a block is present it
must follow this exact name.

## 7. Reports

Every command ends with a `Report` step. Reports:

- Follow a canonical template from `_shared/report-templates.md`.
- Include every field listed in the template, in the listed order.
- Use `—` (em dash) as the separator in `Pull Request: <url> — [new]`
  style tags. Tag order is `[new | existing]` — `new` first.
- Use `----` (four hyphens) as a body divider only when the
  template prescribes it.
- Are the last thing the command emits. No trailing prose.

## 8. Cross-command state

State travels between commands through **explicit channels only**:

- **`$ARGUMENTS`** — the user-typed input.
- **Git state** — current branch, HEAD, clean/dirty tree. Any
  command may read it; only the command whose scope is branch
  management (`/task_branch`) modifies it.
- **Filesystem** — `tasks/*.md`, `github-tasks.json`. Written by
  `/task_create`, `/task_sync`; read by others.
- **GitHub state** — Issues, comments, PRs. Accessed through the
  `gh` CLI only, targeting the `origin` repository.
- **Sub-command report outputs** — captured by name per §2.

Commands do **not** communicate via implicit globals, environment
variables, session memory, or conversation context outside the
channels listed above.

## 9. Enforcement summary

A command is contract-compliant when:

1. Its first body paragraph points at this file.
2. Every step follows §6 anatomy.
3. Every failure mode STOP either references an error-template key
   or quotes a message verbatim in a fenced block.
4. Every cross-command invocation follows §2.
5. Every captured variable follows §3.
6. The final Report follows §7 and the canonical template.

`scripts/lint_commands.py` validates these mechanically.
