#!/usr/bin/env bash
# Creates/removes symlinks from the repository into ~/.claude/.
# Safe: only touches what exists in the repo. Anthropic built-in skills are left alone.

set -euo pipefail

CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.claude}"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DRY_RUN=0
UNINSTALL=0
PRUNE=0

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --uninstall) UNINSTALL=1 ;;
    --prune) PRUNE=1 ;;
    -h|--help)
      cat <<EOF
Usage: $0 [--dry-run] [--uninstall] [--prune]

  --dry-run     show actions without making changes
  --uninstall   remove previously created symlinks
  --prune       remove our symlinks whose target is gone from the repo
                or is now skipped (see is_skipped)
EOF
      exit 0
      ;;
    *) echo "unknown flag: $arg" >&2; exit 1 ;;
  esac
done

# Categories that we symlink entry-by-entry (not the whole folder, to avoid clashing with built-ins)
CATEGORIES=(skills agents commands hooks)

# Entries that must never be linked: OS/editor junk, caches, and files that
# Claude Code would otherwise register as slash commands (/README, /task_example).
# commands/_contract.md and commands/_shared/ stay linked: commands read them at runtime.
# scripts/doctor.sh sources this file's is_skipped via INSTALL_SH_LIB=1.
is_skipped() {
  local cat="$1" name="$2"
  case "$name" in
    .*|__pycache__) return 0 ;;
  esac
  if [[ "$cat" == "commands" ]]; then
    case "$name" in
      README.md|*_example.md) return 0 ;;
    esac
  fi
  return 1
}

[[ "${INSTALL_SH_LIB:-0}" == "1" ]] && return 0

log() { printf "%s\n" "$*"; }
run() {
  if [[ $DRY_RUN -eq 1 ]]; then
    log "DRY: $*"
  else
    eval "$*"
  fi
}

ensure_dir() {
  local dir="$1"
  if [[ ! -d "$dir" ]]; then
    run "mkdir -p '$dir'"
  fi
}

link_one() {
  local src="$1" dst="$2"
  if [[ -L "$dst" ]]; then
    local current
    current="$(readlink "$dst")"
    if [[ "$current" == "$src" ]]; then
      log "  = $dst (already linked)"
      return
    fi
    log "  ! $dst is a symlink, but points to '$current'. Skipping."
    return
  fi
  if [[ -e "$dst" ]]; then
    log "  ! $dst exists and is not a symlink. Skipping."
    return
  fi
  run "ln -s '$src' '$dst'"
  log "  + $dst -> $src"
}

unlink_one() {
  local src="$1" dst="$2"
  if [[ -L "$dst" ]]; then
    local current
    current="$(readlink "$dst")"
    if [[ "$current" == "$src" ]]; then
      run "rm '$dst'"
      log "  - $dst"
      return
    fi
  fi
  log "  · $dst skipped (not our symlink)"
}

# Remove symlinks in ~/.claude/<cat>/ that point into $REPO/<cat>/ but whose
# target no longer exists or is skipped. Links pointing elsewhere are left alone.
prune_category() {
  local cat="$1"
  local src_root="$REPO/$cat"
  local dst_root="$CLAUDE_HOME/$cat"
  [[ -d "$dst_root" ]] || return 0
  local dst target name
  for dst in "$dst_root"/* "$dst_root"/.[!.]*; do
    [[ -L "$dst" ]] || continue
    target="$(readlink "$dst")"
    [[ "$target" == "$src_root/"* ]] || continue
    name="${target#"$src_root/"}"
    if [[ ! -e "$target" ]]; then
      run "rm '$dst'"
      log "  - $dst (stale)"
    elif is_skipped "$cat" "$name"; then
      run "rm '$dst'"
      log "  - $dst (skipped entry)"
    fi
  done
}

process_category() {
  local cat="$1"
  local src_root="$REPO/$cat"
  local dst_root="$CLAUDE_HOME/$cat"

  if [[ ! -d "$src_root" ]]; then
    return
  fi

  ensure_dir "$dst_root"
  log "[$cat]"

  shopt -s nullglob
  if [[ $PRUNE -eq 1 ]]; then
    prune_category "$cat"
  fi
  for entry in "$src_root"/* "$src_root"/.[!.]*; do
    local name
    name="$(basename "$entry")"
    local src="$src_root/$name"
    local dst="$dst_root/$name"
    # uninstall still removes links to skipped entries made by older versions
    if [[ $UNINSTALL -eq 0 ]] && is_skipped "$cat" "$name"; then
      continue
    fi
    if [[ $UNINSTALL -eq 1 ]]; then
      unlink_one "$src" "$dst"
    else
      link_one "$src" "$dst"
    fi
  done
  shopt -u nullglob
}

log "claude-config: $REPO"
log "target:        $CLAUDE_HOME"
[[ $DRY_RUN -eq 1 ]] && log "(dry-run)"
[[ $UNINSTALL -eq 1 ]] && log "(uninstall)"
[[ $PRUNE -eq 1 ]] && log "(prune)"
log ""

for cat in "${CATEGORIES[@]}"; do
  process_category "$cat"
done

log ""
log "Done."

# Remind the user to update LICENSE if it still contains the template placeholder name.
if [[ $UNINSTALL -eq 0 ]] && grep -q "TODO (after fork)" "$REPO/LICENSE" 2>/dev/null; then
  log ""
  log "REMINDER: update LICENSE — replace the author name and year in the Copyright line."
fi
