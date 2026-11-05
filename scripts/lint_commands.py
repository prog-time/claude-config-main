#!/usr/bin/env python3
"""Validate contract compliance of slash-commands in commands/*.md.

Checks:
- file starts with YAML frontmatter, declares `contract: _contract.md`
- body cites `_contract.md` in its first 20 lines
- every `### Step N — <title>` has Preconditions, Action, Failure modes
- every STOP reference uses `error-templates.md#<key>` and the key
  exists in `_shared/error-templates.md`
- the command includes at least one reference to a template section
  in `_shared/report-templates.md` (by command name)
- `_shared/` and `_contract.md` themselves are skipped

Usage:
  python3 scripts/lint_commands.py           # warnings are informational
  python3 scripts/lint_commands.py --strict  # warnings become errors
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
COMMANDS_DIR = REPO / "commands"
SHARED_DIR = COMMANDS_DIR / "_shared"
ERROR_TEMPLATES = SHARED_DIR / "error-templates.md"
REPORT_TEMPLATES = SHARED_DIR / "report-templates.md"
CONTRACT = COMMANDS_DIR / "_contract.md"

errors: list[str] = []
warnings: list[str] = []


# ---------------------------------------------------------------------------
# Frontmatter & helpers
# ---------------------------------------------------------------------------


def split_frontmatter(text: str) -> tuple[dict[str, str] | None, str]:
    """Return (frontmatter-dict, body) or (None, full-text) if none."""
    if not text.startswith("---"):
        return None, text
    lines = text.splitlines()
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None, text
    fm: dict[str, str] = {}
    for raw in lines[1:end]:
        if ":" in raw and not raw.startswith(" "):
            key, _, value = raw.partition(":")
            fm[key.strip()] = value.strip().strip('"').strip("'")
    body = "\n".join(lines[end + 1 :])
    return fm, body


def load_error_template_keys() -> set[str]:
    """Extract all `## <key>` headings from error-templates.md."""
    if not ERROR_TEMPLATES.is_file():
        return set()
    keys: set[str] = set()
    for line in ERROR_TEMPLATES.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^##\s+`([^`]+)`\s*$", line)
        if m:
            keys.add(m.group(1))
    return keys


def load_report_command_sections() -> set[str]:
    """Extract all `## <command>` headings from report-templates.md."""
    if not REPORT_TEMPLATES.is_file():
        return set()
    sections: set[str] = set()
    for line in REPORT_TEMPLATES.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^##\s+`([^`]+)`\s*$", line)
        if m:
            sections.add(m.group(1))
    return sections


# ---------------------------------------------------------------------------
# Per-command checks
# ---------------------------------------------------------------------------


STEP_HEADER = re.compile(r"^###\s+Step\s+[\w.]+\s+[—-]\s+", re.MULTILINE)
STOP_REF = re.compile(r"error-templates\.md#([a-zA-Z0-9\-]+)")
REPORT_REF = re.compile(r"report-templates\.md")


def check_command(path: Path, error_keys: set[str], report_sections: set[str]) -> None:
    rel = path.relative_to(REPO)
    text = path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)

    # Frontmatter checks
    if fm is None:
        errors.append(f"{rel}: missing or malformed frontmatter")
        return
    if fm.get("contract") != "_contract.md":
        errors.append(
            f"{rel}: frontmatter must declare `contract: _contract.md` "
            f"(got {fm.get('contract')!r})"
        )
    for key in ("description", "argument-hint"):
        if key not in fm:
            warnings.append(f"{rel}: missing frontmatter key '{key}'")

    # Contract citation in first 20 body lines
    head = "\n".join(body.splitlines()[:20])
    if "_contract.md" not in head:
        errors.append(
            f"{rel}: body must cite `_contract.md` within the first 20 lines"
        )

    # Step anatomy: every step has Preconditions, Action, Failure modes
    step_positions = [m.start() for m in STEP_HEADER.finditer(body)]
    if not step_positions:
        warnings.append(f"{rel}: no `### Step N —` sections detected")
    step_positions.append(len(body))
    for i in range(len(step_positions) - 1):
        block = body[step_positions[i] : step_positions[i + 1]]
        header_line = block.splitlines()[0].strip()
        for required in ("**Preconditions:**", "**Action:**", "**Failure modes:**"):
            if required not in block:
                errors.append(
                    f"{rel}: step missing `{required}` "
                    f"under `{header_line}`"
                )

    # STOP references point at existing error-template keys
    for match in STOP_REF.finditer(body):
        key = match.group(1)
        if key not in error_keys:
            errors.append(
                f"{rel}: references unknown error-template key `{key}`"
            )

    # Report step references report-templates.md
    if "### Step" in body and "Report" in body:
        if not REPORT_REF.search(body):
            errors.append(
                f"{rel}: Report step must reference `report-templates.md`"
            )

    # Command name matches a section in report-templates.md
    command_name = path.stem  # e.g. 'task_create'
    if command_name not in report_sections:
        warnings.append(
            f"{rel}: no section `## {command_name}` in report-templates.md"
        )


# ---------------------------------------------------------------------------
# Shared-file checks
# ---------------------------------------------------------------------------


def check_shared_files() -> None:
    for required in (CONTRACT, ERROR_TEMPLATES, REPORT_TEMPLATES,
                     SHARED_DIR / "workflow.md",
                     SHARED_DIR / "repo-resolution.md"):
        if not required.is_file():
            errors.append(f"missing required foundation file: {required.relative_to(REPO)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    strict = "--strict" in sys.argv

    check_shared_files()

    error_keys = load_error_template_keys()
    report_sections = load_report_command_sections()

    command_files = sorted(
        p for p in COMMANDS_DIR.glob("*.md")
        if p.name not in {"_contract.md", "README.md"}
    )

    print(
        f"Linting {len(command_files)} command(s) — "
        f"{len(error_keys)} error keys, "
        f"{len(report_sections)} report sections known."
    )

    for p in command_files:
        check_command(p, error_keys, report_sections)

    for w in warnings:
        print(f"warn: {w}")
    for e in errors:
        print(f"FAIL: {e}")

    if errors:
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s).")
        return 1
    if strict and warnings:
        print(
            f"\n0 error(s), {len(warnings)} warning(s) — "
            "treated as errors (--strict)."
        )
        return 1
    print(f"OK ({len(warnings)} warning(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
