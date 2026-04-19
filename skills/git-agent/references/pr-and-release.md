# Modes C–G — PR Descriptions, Release Notes, Publishing

Load this file when handling any of:

- `git-agent desc pr [branch] -> [target]` (Mode C)
- `git-agent desc release {version}` (Mode D)
- `git-agent desc changelog {version}` (Mode E)
- `git-agent publish pr [branch] -> [target]` (Mode F)
- `git-agent publish release {version}` (Mode G)

## Input Collection

### For PR Description (Modes C, F)

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

### For Release Notes (Modes D, E, G)

Collect these inputs (ask the user if not provided):

- **Previous tag** — default: `git describe --tags --abbrev=0`
- **New version tag** — ask the user (normalize `6` → `v6`,
  `2.3` → `v2.3.0`)

Fetch commits:

```bash
git log {last_tag}..HEAD --oneline --no-merges
```

If no previous tag exists, use all commits:

```bash
git log --oneline --no-merges
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

1. **Write from the user's perspective** — describe the effect, not
   the implementation detail. "Users can now reset their password via
   email", not "Added PasswordResetController".
2. **Consolidate** — if multiple commits touch the same feature or
   fix, collapse them into one mention. The PR body is not a
   commit-by-commit log.
3. **PR body is a short summary, not a ledger.** Detailed breakdowns
   belong in the diff and commits.

Rule 1–3 apply to PR summaries (Mode C, F). For Release Notes
(Modes D, E, G) — see the Release Notes section; there bullets by
category are still the format.

## PR Description Template (Mode C, F)

The template matches `templates/github/PULL_REQUEST_TEMPLATE.md` — the
file a human sees when opening a PR manually. Generated and manual PRs
look the same.

```markdown
## Summary

[1–2 sentences: what changed and why. Consolidate all commits into
one short paragraph. No bullet list.]

## Linked issues

Closes #{N}
[Add "Related to #{M}" on its own line for linked-but-not-closed issues.]

## Checklist

- [ ] Tests pass locally
- [ ] Docs / CHANGELOG updated if behavior changed
- [ ] No leftover debug code, prints, or stale TODOs
- [ ] Breaking changes flagged in the summary

## Notes for reviewer

[Optional. Fill with trade-offs, risks, migration steps, or uncertain
areas inferred from the diff. If nothing stands out, write:
"No significant risks identified."]

---

_The task was generated using the MCP server — [prog-time/mcp-github-issues](https://github.com/prog-time/mcp-github-issues)._
```

### Auto-fill rules (Mode C, F)

- **`Closes #{N}`** — extract `{N}` from the current branch
  (`^issues-(\d+)$`). If the branch does not match, leave `Closes #`
  and warn the user that the issue number must be filled manually.
- **Checklist** — always emit empty checkboxes. The agent cannot know
  whether tests ran or docs are updated; the human author ticks them
  before merge.
- **MCP footer** — always append the footer verbatim. It's a static
  marker identifying this repo's task-origin workflow.

## Release Notes Template (Modes D, E, G)

```markdown
# Release v{version} — {YYYY-MM-DD}

## Features

- [Feature 1]
- [Feature 2]

## Bug Fixes

- [Fix 1]
- [Fix 2]

## Refactoring

- [Refactor 1]

## Documentation

- [Doc 1]

## Performance

- [Perf 1]

## Maintenance

- [Chore 1]
```

Omit empty sections.

## CHANGELOG.md Entry (Mode E)

Same format as Release Notes. Prepend the new entry above the previous
entries. If `CHANGELOG.md` does not exist, create it with only the new
entry. Show the diff to the user before writing.

## Version Bump Guidance

When the user asks what version to use next:

| Condition | Bump |
|-----------|------|
| Any breaking change (API removed, behavior changed) | **Major** (X.0.0) |
| New features, no breaking changes | **Minor** (x.Y.0) |
| Only bug fixes, docs, refactoring, maintenance | **Patch** (x.y.Z) |

Always state the recommendation and let the user confirm.

## Publishing via `gh` CLI (Modes F, G)

**Always ask for user confirmation before running any publishing
command.** Show the generated content first.

**Create PR (Mode F):**

```bash
gh pr create --title "{title}" --body "{generated_description}" --base {target_branch}
```

**Create GitHub Release (Mode G):**

```bash
gh release create {tag} --title "Release {tag}" --notes "{generated_release_notes}"
```

**Create Draft Release (optional — if the user asks):**

```bash
gh release create {tag} --title "Release {tag}" --notes "{generated_release_notes}" --draft
```

## Self-Verification Before Reporting

**All modes:**

- [ ] Actual git commits were fetched — nothing was invented
- [ ] Noise commits (merges, typos, formatting) are excluded
- [ ] Output describes user/system impact, not implementation detail
- [ ] No publishing action was taken without explicit user confirmation

**PR modes (C, F):**

- [ ] Summary is 1–2 sentences, not a per-commit ledger
- [ ] `Closes #{N}` was auto-filled from the current branch name
      (or a warning was raised)
- [ ] Checklist is present with all boxes empty — for the human to tick
- [ ] MCP footer is appended verbatim

**Release modes (D, E, G):**

- [ ] Bullets grouped by category; empty categories are omitted
- [ ] Version bump recommendation is justified by the change types
      found
