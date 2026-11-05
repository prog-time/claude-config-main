# Release Notes, CHANGELOG & Publishing (Modes D, E, G)

Load this file when handling:

- `git-agent desc release {version}` (Mode D — release notes, show only)
- `git-agent desc changelog {version}` (Mode E — release notes + CHANGELOG)
- `git-agent publish release {version}` (Mode G — release notes, Issue audit,
  then publish and close)

## Input Collection

Collect these inputs (ask the user if not provided):

- **Previous tag** — default: `git describe --tags --abbrev=0`
- **New version tag** — ask the user (normalize `6` → `v6`, `2.3` → `v2.3.0`)

Fetch commits:

```bash
git fetch origin --tags
git log {last_tag}..origin/main --oneline --no-merges
```

If no previous tag exists, use all commits:

```bash
git log origin/main --oneline --no-merges
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

## Release Notes Template

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

Omit empty sections. Write bullets from the user/system-impact perspective, not
implementation detail.

## CHANGELOG.md Entry (Mode E)

Same format as Release Notes. Prepend the new entry above the previous entries.
If `CHANGELOG.md` does not exist, create it with only the new entry. Show the
diff to the user before writing.

## Version Bump Guidance

When the user asks what version to use next:

| Condition | Bump |
|-----------|------|
| Any breaking change (API removed, behavior changed) | **Major** (X.0.0) |
| New features, no breaking changes | **Minor** (x.Y.0) |
| Only bug fixes, docs, refactoring, maintenance | **Patch** (x.y.Z) |

Always state the recommendation and let the user confirm.

## Publishing via `gh` CLI (Mode G)

**Always ask for user confirmation before running any publishing command.** Show
the generated content first.

**Create GitHub Release:**

```bash
gh release create {tag} -R {origin_repo} --target main --title "Release {tag}" --notes "{generated_release_notes}"
```

**Create Draft Release (optional — if the user asks):**

```bash
gh release create {tag} -R {origin_repo} --target main --title "Release {tag}" --notes "{generated_release_notes}" --draft
```

## Issue Audit (Mode G)

Run before the release confirmation, against what will actually ship. Audit
**all** open Issues, not only those touched since the last tag. A PR into
`develop` never auto-closes its Issue, and the `develop` → `main` PR rarely
repeats `Closes #N`, so finished Issues stay open.

```bash
git fetch origin
gh issue list -R {origin_repo} --state open --limit 1000 --json number,title,body
gh pr list -R {origin_repo} --state merged --limit 1000 \
  --json number,mergeCommit,closingIssuesReferences
git merge-base --is-ancestor {merge_commit} origin/main  # exit 0 = shipped
```

Sort each open Issue into one group:

| Evidence | Group |
|----------|-------|
| A merged PR lists it in `closingIssuesReferences` and the PR's `mergeCommit` is an ancestor of `origin/main` | **Close** |
| No such PR, but the Issue's body states its criteria (e.g. `## Готово когда`) and each one is verifiably met by the code on `origin/main` | **Close** — name what you checked |
| Work is only on `develop`, a branch, or an unmerged PR | **Leave open** — not shipped |
| Anything else: partial work, vague criteria, no criteria, no trace in the code | **Leave open** — say why |

Commits or a `Related to #N` link alone do not prove an Issue is finished. If
`develop` is squash-merged into `main`, merge commits are not ancestors of
`origin/main`, so judge those Issues by the code criteria instead.

Add both lists to the release preview: Issues to close, each with its evidence
(`#12 — PR #15 merged`), and Issues left open that have related work. For open
Issues with no trace of work, report only their count.

After `gh release create` succeeds, for each Issue in the **Close** group:

```bash
gh issue close {N} -R {origin_repo} --reason completed --comment "Released in {tag}."
```

If `github-tasks.json` exists at the repo root and has a record for the Issue,
set `"status": "done"` and `"close": true` on it, so `/task_sync` does not post a
second comment. Do not add records and do not commit the file.

Report the Issues closed, those left open, and any `gh` failures.

## Self-Verification Before Reporting

- [ ] Actual git commits were fetched — nothing was invented
- [ ] Noise commits (merges, typos, formatting) are excluded
- [ ] Output describes user/system impact, not implementation detail
- [ ] Bullets grouped by category; empty categories are omitted
- [ ] Version bump recommendation is justified by the change types found
- [ ] (Mode E) CHANGELOG diff was shown before writing
- [ ] No publishing action was taken without explicit user confirmation
- [ ] (Mode G) All open Issues were audited, and each closed Issue has evidence
      that was shown in the confirmation
- [ ] (Mode G) Issues were closed only after the release succeeded
