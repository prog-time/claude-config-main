# CLAUDE.md

## This repository is public

`prog-time/claude-config-main` is a **public** GitHub repository. Everything
that reaches GitHub is visible to anyone and stays visible: files, the full git
history, commit messages, branch names, Issues, PRs, and review comments.
Deleting or rewriting something later does not take it back. Forks, clones, and
GitHub's `refs/pull/*` keep the old commits.

The repository has already leaked a live GitHub token once:
`mcp/servers.json.example` carried a real `GITHUB_TOKEN` for one commit. Treat
security as a gate on every change, not as a review afterthought.

## Secrets: never commit them

- Never write a real token, key, password, cookie, webhook URL, or connection
  string into a tracked file, even an `*.example` file or a code block in docs.
  Use placeholders in angle brackets: `<GITHUB_TOKEN>`, `<API_KEY>`,
  `<NODE_BIN_PATH>`.
- Real configs stay local and gitignored: `mcp/servers.json`, `.env`,
  `*.local`, `.claude/` (including `settings.local.json` and logs). Never
  bypass `.gitignore` with `git add -f`.
- Stage files explicitly (never `git add .` / `git add -A`) and read the
  staged diff before every commit.
- Before every commit, scan the staged diff and stop if anything matches:

  ```bash
  git diff --cached | grep -nEi 'ghp_|github_pat_|gho_|ghs_|sk-ant-|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|xox[abprs]-|BEGIN [A-Z ]*PRIVATE KEY|bot[0-9]{8,}:|(password|passwd|secret|token|api_?key)"?[[:space:]]*[:=][[:space:]]*"?[A-Za-z0-9_/+=-]{12,}'
  ```

  Placeholders like `<GITHUB_TOKEN>` and regex examples in docs are fine. A
  real-looking value is not: stop and ask the user.

## If a secret was committed

1. Stop. Do not push. If it is already pushed, say so immediately.
2. Tell the user which secret it is, the commit, and the file. Do not repeat the
   full value in chat, Issues, or PRs.
3. The fix is **revoking or rotating the secret**. Removing it from the file or
   rewriting history is not enough on a public repository.
4. Never force-push or rewrite shared history without the user's explicit
   request.

## Personal and private data

- No absolute home paths (`/Users/<name>/...`). Write `~/.claude/...` or
  `$HOME/...`. They expose the username and break for anyone who forks the
  repository.
- No personal emails, phone numbers, private repository names, internal URLs,
  customer data, or excerpts from session transcripts and logs. The GitHub
  `noreply` address is fine.
- Issue, PR, and commit text is public too. Do not paste raw command output
  that may hold tokens, paths, or environment variables.

## Code that runs on users' machines

Hooks, `install.sh`, `scripts/`, and `linting/` run on every machine that
installs this config, often with no review. Keep them safe by default:

- `set -euo pipefail` and quoted variables in shell, no `eval` on input, and
  bounded reads of hook stdin.
- No network calls, `curl | bash`, or downloads unless the task requires them.
  Never send local files or environment data anywhere.
- Never delete or overwrite anything outside the repository's own symlinks in
  `~/.claude`.
- Skills, agents, and commands must not tell Claude to skip permission prompts,
  widen allowlists, disable hooks, or use `--no-verify`.

## GitHub Actions

- Set an explicit, minimal `permissions:` block in every workflow.
- Never use `pull_request_target` or `workflow_run` to check out and run code
  from fork PRs.
- Never echo secrets or `${{ secrets.* }}` into logs. Pass them through `env:`,
  not inline into `run:` scripts.
- Pin third-party actions to a release tag at least. Prefer a commit SHA for
  actions outside `actions/*`.

## Third-party content

Keep upstream licenses and attribution, for example `skills/humanizer/LICENSE`.
Do not copy code or text whose license does not allow redistribution.
