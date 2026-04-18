---
description: Reference skeleton for a new /task_* command — copy, rename, and replace step bodies
argument-hint: <example-input>
contract: _contract.md
---

# /task_example

> **Before executing, read `_contract.md`** — it defines STOP,
> invoke, capture, and verbatim semantics. These definitions
> override any loose natural-language reading inside the steps.

**This file is a reference skeleton.** It is not part of the
happy-path workflow (see `_shared/workflow.md`). Copy it,
rename it to `commands/task_<your_command>.md`, and replace
the step bodies with your own logic. Every section below
demonstrates a required element of `_contract.md` §6.

**Input:** `$ARGUMENTS` — a single descriptive string (replace
with your command's actual argument spec).

## Workflow

### Step 1 — Validate input

**Preconditions:** `$ARGUMENTS` is non-empty and well-formed.
**Action:** parse `$ARGUMENTS` and confirm it matches the
expected shape for this command (replace with your actual
validation logic).
**Capture:** `validated_input` (string).

**Failure modes:**
- `$ARGUMENTS` is empty → STOP with template
  `error-templates.md#usage-missing-args`
  (`command=task_example`, `argument_hint=<example-input>`).
- `$ARGUMENTS` is present but malformed → STOP with template
  `error-templates.md#usage-missing-args`
  (`command=task_example`, `argument_hint=<example-input>`).

**Invariants after:** `validated_input` holds the parsed value;
no external state has been modified.

### Step 2 — Report

**Preconditions:** Step 1 succeeded.
**Action:** emit the `task_example` template from
`_shared/report-templates.md`:

```
Input:         {validated_input}
Status:        ok
```

**Capture:** none.
**Failure modes:** none — this step is terminal.

## Rules (non-negotiable)

- This file is a skeleton only. Do not invoke it in any real
  workflow chain.
- When you derive a real command from this skeleton, remove
  this Rules block and replace it with the actual constraints
  of your command.
- Every STOP must reference a key from
  `_shared/error-templates.md`; never inline a new message
  without adding a key there first.
- End every derived command with a Report step that references
  `_shared/report-templates.md`.
