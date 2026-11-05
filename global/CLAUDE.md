# Global Claude Code Rules

## Absolute Output Constraint — git-agent commit mode

When the user message starts with `git-agent desc commit`, your **entire response** must be the raw commit message text and nothing else.

- No preamble: no "Here is the generated commit message:", "Suggested commit message:", "Generated commit message:", or any similar phrase
- No trailing commentary or explanation
- No markdown formatting, bold, headers, or fences
- No quotes around the message

The output is captured by a git hook and written directly to `COMMIT_EDITMSG`. Any extra text becomes part of the commit message.

**The response IS the commit message. Nothing else.**

## Git & GitHub — every project

- **The project repository is always the `origin` remote.** Resolve it with
  `gh repo view "$(git remote get-url origin)" --json nameWithOwner -q .nameWithOwner`
  and pass `-R <owner/repo>` to every `gh` call. Ignore `upstream` and other
  remotes. No GitHub `origin` → say so and stop; don't guess.
- **Every Pull Request targets `develop`.** Branch from `origin/develop`, open
  PRs with `--base develop`. Never open or retarget a PR into `main` (or
  `master`) — those are opened by humans. If `origin/develop` does not exist,
  stop and tell the user; never fall back to `main`.
- **When a PR has to be opened by hand, put its compare link in the chat** so
  the user can follow it and create the PR:
  `https://github.com/<owner/repo>/compare/<base>...<head>`, for example
  `https://github.com/prog-time/claude-config-main/compare/main...develop`. Take
  `<owner/repo>` from `origin`. This applies to every project with a GitHub
  repository, including when `gh` or a hook blocks PR creation.
- A PreToolUse hook (`~/.claude/hooks/pr-base-guard.py`) denies any PR whose
  base is not `develop`. If it fires, fix the base — don't work around it.

## Delivery — every project

- **test** deploys automatically when the `CI` workflow is green on a push to
  `main`.
- **production** deploys on a `v*` tag (`git tag v1.0.0 && git push --tags`)
  or manually via *Run workflow*; Required reviewers on the `production`
  environment add an approval button before rollout.
- Deploys live only in `.github/workflows/deploy.yml` (canonical template:
  `~/.claude/skills/ci-setup/templates/deploy.yml`, rules in
  `~/.claude/skills/ci-setup/references/delivery.md`). Never deploy from
  `develop` or feature branches, never put a deploy into CI.
- Pushing to `main`, creating/pushing a `v*` tag, `gh release create`, or
  `gh workflow run` on a deploy workflow **ship code to an environment**. Do
  them only when the user explicitly asks in the current message, and say
  which environment it will hit before running it.

## Project `rules/` — every project

- `rules/` has one layout everywhere (`~/.claude/skills/rules-generator/references/layout.md`). Read `rules/README.md` first, then only the schema the task touches.
- When you change the DB schema, update `rules/database/erd.md`. When you change the API, run `api.generate` from `rules/sync.yml` (or edit `rules/api/openapi.yaml`) and rebuild `postman.json`. When you change containers or integrations, update `rules/architecture/c4-*.md`.
- The `rules_check` hook warns after a commit when they drift, and CI fails the PR. Skip a section only with a `Rules-Skip: <section> — <reason>` commit line.
- If the project has no `rules/`, suggest `rules-generator`. Do not invent another location.
