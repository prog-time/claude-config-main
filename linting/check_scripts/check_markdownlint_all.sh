#!/usr/bin/env bash
# markdownlint over every *.md not in .markdownlintignore. Used by linting/pre-push-check.sh.
set -euo pipefail
cd "$(dirname "$0")/../.."
command -v markdownlint >/dev/null || { echo "markdownlint not installed — skipped (npm i -g markdownlint-cli)"; exit 0; }
markdownlint --ignore-path .markdownlintignore "**/*.md"
echo "markdownlint: OK"
