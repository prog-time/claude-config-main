#!/usr/bin/env bash
# UserPromptSubmit hook: when the project is backed by a GitHub repo, tell
# Claude to offer /task_create before implementing a request that looks like
# new functionality. Classifying the prompt is left to the model; this script
# only does the deterministic part (is there a repo, which one).

set -euo pipefail

input="$(cat)"
prompt="$(jq -r '.prompt // ""' <<<"$input")"
cwd="$(jq -r '.cwd // ""' <<<"$input")"
[[ -n "$cwd" ]] || cwd="$PWD"

# Empty prompts and slash commands are explicit — nothing to offer.
[[ -z "${prompt//[[:space:]]/}" || "$prompt" == /* ]] && exit 0

git -C "$cwd" rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

# On an issues-{N} branch the task already exists.
branch="$(git -C "$cwd" rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
[[ "$branch" =~ ^issues-[0-9]+$ ]] && exit 0

# git@github.com:owner/repo.git | https://github.com/owner/repo(.git)
url="$(git -C "$cwd" remote get-url origin 2>/dev/null || true)"
[[ "$url" =~ github\.com[:/]([^/]+/[^/]+)$ ]] || exit 0
repo="${BASH_REMATCH[1]%.git}"

context="Project repository: ${repo} (GitHub).
If the user's prompt asks to build NEW functionality (a new feature, capability, command, endpoint, screen, skill, agent, etc.) — not a bug fix, question, review, refactor, docs, commit/PR, or a follow-up to work already under way in this conversation — then BEFORE doing any work ask with AskUserQuestion, question text exactly: \"Создать задачу в репозитории ${repo}?\" with options \"Да\" and \"Нет\".
- \"Да\" → run /task_create with the user's prompt verbatim as the task description, report its result, and stop.
- \"Нет\" → carry out the request as usual.
Otherwise ignore this note and do not mention it."

jq -n --arg ctx "$context" \
  '{hookSpecificOutput: {hookEventName: "UserPromptSubmit", additionalContext: $ctx}}'
