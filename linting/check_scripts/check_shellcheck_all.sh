#!/usr/bin/env bash
# ShellCheck over every *.sh in the project. Used by linting/pre-push-check.sh.
# Written for bash 3.2 (macOS), so no mapfile.
set -euo pipefail
cd "$(dirname "$0")/../.."
command -v shellcheck >/dev/null || { echo "shellcheck not installed — skipped"; exit 0; }
count="$(find . -name '*.sh' -not -path './.git/*' -not -path '*/node_modules/*' | wc -l | tr -d ' ')"
[[ "$count" -eq 0 ]] && { echo "No shell scripts found"; exit 0; }
find . -name '*.sh' -not -path './.git/*' -not -path '*/node_modules/*' -print0 | xargs -0 shellcheck
echo "ShellCheck: $count file(s) OK"
