#!/usr/bin/env bash
# gitleaks over the commits not yet on origin/develop (or a range given as $1).
# Uses a local gitleaks, else the pinned Docker image, else skips with a warning.
set -euo pipefail
cd "$(dirname "$0")/../.."
range="${1:-}"
if [[ -z "$range" ]]; then
  if git rev-parse -q --verify origin/develop >/dev/null; then range="origin/develop..HEAD"; else range="HEAD"; fi
fi
if [[ -z "$(git rev-list "$range" 2>/dev/null | head -1)" ]]; then
  echo "secrets: no new commits in $range"
  exit 0
fi
args=(detect --source . --log-opts="$range" --config .gitleaks.toml --redact --no-banner)
if command -v gitleaks >/dev/null; then
  gitleaks "${args[@]}"
elif command -v docker >/dev/null && docker info >/dev/null 2>&1; then
  docker run --rm -v "$PWD:/repo" -w /repo zricethezav/gitleaks:v8.21.2 "${args[@]}"
else
  echo "secrets: gitleaks and Docker unavailable — skipped (brew install gitleaks)"
  exit 0
fi
echo "secrets: $range clean"
