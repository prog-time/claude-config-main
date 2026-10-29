#!/usr/bin/env bash
# Creates the skeleton for a new skill: skills/<name>/SKILL.md + README.md
set -euo pipefail

NAME="${1:-}"
DESC="${2:-TODO: describe triggers and behaviour}"

if [[ -z "$NAME" ]]; then
  echo "usage: $0 <skill-name> [\"description\"]"
  exit 1
fi

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIR="$REPO/skills/$NAME"

if [[ -e "$DIR" ]]; then
  echo "skill '$NAME' already exists: $DIR"
  exit 1
fi

mkdir -p "$DIR"

# Single source of truth for the SKILL.md shape: the skill-creator asset
# template. Rendering from it (rather than an inline heredoc) keeps the
# scaffold and the canonical template from drifting apart.
TEMPLATE="$REPO/skills/skill-creator/assets/SKILL.md.template"

if [[ -f "$TEMPLATE" ]]; then
  NAME="$NAME" DESC="$DESC" python3 - "$TEMPLATE" > "$DIR/SKILL.md" <<'PY'
import os, sys
t = open(sys.argv[1]).read()
t = t.replace('name: <skill-name>', 'name: ' + os.environ['NAME'])
t = t.replace('<One sentence on what the skill does.>', os.environ['DESC'])
t = t.replace('# <Skill Title>', '# ' + os.environ['NAME'])
sys.stdout.write(t)
PY
else
  # Fallback — keep the good frontmatter shape (literal description + allowed-tools)
  # even if the template asset is missing.
  cat > "$DIR/SKILL.md" <<EOF
---
name: $NAME
description: |
  $DESC
  Use ALWAYS when the user says "<trigger 1>", "<trigger 2>", "<trigger 3>".
  Do NOT use for <explicit exclusion>.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
---

# $NAME

TODO: describe what the skill does, when it triggers, and what output it
produces.

## Workflow

### Step 1 — <action>

1. TODO
EOF
fi

cat > "$DIR/README.md" <<EOF
# $NAME

$DESC

## Installation

Picked up automatically after \`make install\` at the repository root.

## Usage

TODO: example user requests.
EOF

echo "created skills/$NAME/"
echo "  - SKILL.md"
echo "  - README.md"
