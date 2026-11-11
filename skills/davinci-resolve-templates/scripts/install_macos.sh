#!/usr/bin/env bash
# Install a .drfx bundle into DaVinci Resolve's Fusion Templates folder (macOS).
# Unzips into Templates/ so files land in Edit/<Category>/<Group>/.
# Does NOT start, stop, or script Resolve — restart it yourself (Cmd+S, Cmd+Q).
#
# Usage: install_macos.sh <file.drfx>
set -euo pipefail

DRFX="${1:-}"
if [[ -z "$DRFX" || ! -f "$DRFX" ]]; then
  echo "usage: $0 <file.drfx>" >&2
  exit 1
fi
if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "macOS only. Paths for other OS: references/setting-format.md" >&2
  exit 1
fi

T="$HOME/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Templates"

# Only accept archives whose entries stay under Edit/ (no absolute paths, no ..).
BAD="$(unzip -Z1 "$DRFX" | grep -vE '^Edit/[^/]+/[^/]+/[^/]+$' | grep -vE '/$' || true)"
if [[ -n "$BAD" ]]; then
  echo "refusing: unexpected entries in $DRFX:" >&2
  echo "$BAD" >&2
  exit 1
fi
if unzip -Z1 "$DRFX" | grep -q '\.\.'; then
  echo "refusing: '..' in archive paths" >&2
  exit 1
fi

mkdir -p "$T"
unzip -o -q "$DRFX" -d "$T"

echo "Installed into: $T"
unzip -Z1 "$DRFX" | sed 's/^/  /'
GROUP="$(unzip -Z1 "$DRFX" | head -n1 | cut -d/ -f3)"
CATEGORY="$(unzip -Z1 "$DRFX" | head -n1 | cut -d/ -f2)"
echo
echo "Next: save the project (Cmd+S), quit Resolve (Cmd+Q), start it again."
echo "Find it: Edit page -> Effects -> Toolbox -> $CATEGORY -> Fusion $CATEGORY -> group \"$GROUP\" (or search by name)."
