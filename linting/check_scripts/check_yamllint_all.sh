#!/usr/bin/env bash
# yamllint over the project with .yamllint.yml. Used by linting/pre-push-check.sh.
set -euo pipefail
cd "$(dirname "$0")/../.."
command -v yamllint >/dev/null || { echo "yamllint not installed — skipped (pip install yamllint)"; exit 0; }
yamllint .
echo "yamllint: OK"
