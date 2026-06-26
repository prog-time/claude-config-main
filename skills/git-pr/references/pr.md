# PR Descriptions & Publishing (Modes C, F)

Load this file when handling:

- `git-agent desc pr [branch] -> [target]` (Mode C — describe only)
- `git-agent publish pr [branch] -> [target]` (Mode F — describe, then publish)

## Input Collection

Collect these inputs (ask the user if not provided):

- **Source branch** — default: current branch (`git branch --show-current`)
- **Target branch** — default: `main`, then `master`
- **Related issues/tickets** — optional

Fetch commits:

```bash
git log origin/{target}..HEAD --oneline --no-merges
```

Or if remote tracking is unavailable:

```bash
git log {target}..HEAD --oneline --no-merges
```

## Commit Classification

### Conventional Commits (if the project uses them)

| Prefix | Category |
|--------|----------|
| `feat:`, `feature:` | Features |
| `fix:`, `bugfix:` | Bug Fixes |
| `refactor:` | Refactoring |
| `docs:` | Documentation |
| `test:` | Tests |
| `perf:` | Performance |
| `chore:`, `build:`, `ci:` | Maintenance |
| `style:` | Style (usually noise — evaluate) |

### Non-Conventional Commits

Infer category from the commit message:

- "fix", "bug", "error", "crash", "broken" → Bug Fixes
- "add", "new", "implement", "create", "support" → Features
- "refactor", "extract", "move", "rename", "reorganize" → Refactoring
- "doc", "readme", "comment", "changelog" → Documentation
- "test", "spec", "coverage" → Tests
- "perf", "speed", "optim", "cache" → Performance
- Everything else → Maintenance (Chore)

### Noise Filter — Always Ignore

Skip commits that match any of these patterns (case-insensitive):

- `^merge (pull request|branch|remote)`
- `^merged?:`
- `wip`
- `typo`, `typos`
- `formatting`, `whitespace`, `indent`
- `minor fix`, `small fix`, `quick fix`
- `linting`, `lint fix`
- `revert "revert` (double reverts that cancel out)

## Consolidation Rules

Before writing output:

1. **Write from the user's perspective** — describe the effect, not the
   implementation detail. "Users can now reset their password via email", not
   "Added PasswordResetController".
2. **Consolidate** — if multiple commits touch the same feature or fix, collapse
   them into one mention. The PR body is not a commit-by-commit log.
3. **PR body is a short summary, not a ledger.** Detailed breakdowns belong in
   the diff and commits.

## PR Description Template

The template matches `templates/github/PULL_REQUEST_TEMPLATE.md` — the file a
human sees when opening a PR manually. Generated and manual PRs look the same.

```markdown
## Summary

[1–2 sentences: what changed and why. Consolidate all commits into one short
paragraph. No bullet list.]

## Linked issues

Closes #{N}
[Add "Related to #{M}" on its own line for linked-but-not-closed issues.]

## Checklist

- [ ] Tests pass locally
- [ ] Docs / CHANGELOG updated if behavior changed
- [ ] No leftover debug code, prints, or stale TODOs
- [ ] Breaking changes flagged in the summary

## Notes for reviewer

[Optional. Fill with trade-offs, risks, migration steps, or uncertain areas
inferred from the diff. If nothing stands out, write:
"No significant risks identified."]

---

_The task was generated using the MCP server — [prog-time/mcp-github-issues](https://github.com/prog-time/mcp-github-issues)._
```

### Auto-fill rules

- **`Closes #{N}`** — extract `{N}` from the current branch
  (`^issues-(\d+)$`). If the branch does not match, leave `Closes #` and warn
  the user that the issue number must be filled manually.
- **Checklist** — always emit empty checkboxes. The skill cannot know whether
  tests ran or docs are updated; the human author ticks them before merge.
- **MCP footer** — always append the footer verbatim. It's a static marker
  identifying this repo's task-origin workflow.

## Publishing via `gh` CLI (Mode F)

**Always ask for user confirmation before running any publishing command.** Show
the generated content first.

```bash
gh pr create --title "{title}" --body "{generated_description}" --base {target_branch}
```

## Self-Verification Before Reporting

- [ ] Actual git commits were fetched — nothing was invented
- [ ] Noise commits (merges, typos, formatting) are excluded
- [ ] Output describes user/system impact, not implementation detail
- [ ] Summary is 1–2 sentences, not a per-commit ledger
- [ ] `Closes #{N}` was auto-filled from the current branch name (or a warning
      was raised)
- [ ] Checklist is present with all boxes empty — for the human to tick
- [ ] MCP footer is appended verbatim
- [ ] No publishing action was taken without explicit user confirmation
