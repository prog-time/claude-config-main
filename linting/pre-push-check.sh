#!/usr/bin/env bash
# Runs every local check and fails if any of them fails.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
failed=()
for check in shellcheck markdownlint yamllint; do
  echo "== $check"
  bash "linting/check_scripts/check_${check}_all.sh" || failed+=("$check")
done
echo "== secrets"
bash linting/check_scripts/check_secrets.sh || failed+=("secrets")
if [[ ${#failed[@]} -gt 0 ]]; then
  echo "FAILED: ${failed[*]}"
  exit 1
fi
echo "All checks passed."
