# Release Notes, CHANGELOG & Publishing (Modes D, E, G)

Load this file when handling:

- `git-agent desc release {version}` (Mode D — release notes, show only)
- `git-agent desc changelog {version}` (Mode E — release notes + CHANGELOG)
- `git-agent publish release {version}` (Mode G — release notes, then publish)

## Input Collection

Collect these inputs (ask the user if not provided):

- **Previous tag** — default: `git describe --tags --abbrev=0`
- **New version tag** — ask the user (normalize `6` → `v6`, `2.3` → `v2.3.0`)

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
gh release create {tag} --title "Release {tag}" --notes "{generated_release_notes}"
```

**Create Draft Release (optional — if the user asks):**

```bash
gh release create {tag} --title "Release {tag}" --notes "{generated_release_notes}" --draft
```

## Self-Verification Before Reporting

- [ ] Actual git commits were fetched — nothing was invented
- [ ] Noise commits (merges, typos, formatting) are excluded
- [ ] Output describes user/system impact, not implementation detail
- [ ] Bullets grouped by category; empty categories are omitted
- [ ] Version bump recommendation is justified by the change types found
- [ ] (Mode E) CHANGELOG diff was shown before writing
- [ ] No publishing action was taken without explicit user confirmation
