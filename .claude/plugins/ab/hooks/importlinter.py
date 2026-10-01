#!/usr/bin/env python3
"""PreToolUse hook: apply the pending edit to a temp copy and block it if import-linter fails."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

LAYERS = ("domain", "application", "infrastructure", "presentation")
LOG_FILE = Path(__file__).resolve().parent.parent / "importlinter.log"


def log(outcome: str, tool_name: str | None, rel: Path | str, detail: str = "") -> None:
    line = f"{datetime.now(timezone.utc):%Y-%m-%dT%H:%M:%SZ} [{outcome}] [{tool_name}] {rel}"
    if detail:
        line += "\n" + "\n".join(f"  {d}" for d in detail.splitlines())
    with LOG_FILE.open("a") as f:
        f.write(line + "\n")


def violations(output: str) -> str:
    return "\n".join(ln for ln in output.splitlines() if "->" in ln or "is not allowed" in ln)


def apply_edit(text: str, old: str, new: str, replace_all: bool) -> str | None:
    count = text.count(old)
    if count == 0 or (count > 1 and not replace_all):
        return None  # the Edit tool itself will report this error
    return text.replace(old, new) if replace_all else text.replace(old, new, 1)


def run_linter(project_root: Path, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["uv", "run", "--project", str(project_root), "lint-imports"],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


def main() -> int:
    data = json.load(sys.stdin)
    tool_name = data.get("tool_name")
    tool_input = data.get("tool_input", {})
    project_root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd", ".")).resolve()

    target = Path(tool_input.get("file_path", "")).resolve()
    try:
        rel = target.relative_to(project_root)
    except ValueError:
        return 0
    if target.suffix != ".py" or rel.parts[0] not in LAYERS:
        return 0

    original = target.read_text() if target.exists() else ""
    if tool_name == "Write":
        updated: str | None = tool_input.get("content", "")
    elif tool_name in ("Edit", "MultiEdit"):
        edits = tool_input.get("edits") or [tool_input]
        updated = original
        for e in edits:
            updated = apply_edit(
                updated,
                e.get("old_string", ""),
                e.get("new_string", ""),
                e.get("replace_all", False),
            )
            if updated is None:
                return 0
    else:
        return 0

    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        shutil.copy(project_root / "pyproject.toml", tmp_root)
        for layer in LAYERS:
            if (project_root / layer).is_dir():
                shutil.copytree(
                    project_root / layer,
                    tmp_root / layer,
                    ignore=shutil.ignore_patterns("__pycache__"),
                )
        (tmp_root / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_root / rel).write_text(updated)

        after = run_linter(project_root, tmp_root)
        if after.returncode == 0:
            log("PASS", tool_name, rel)
            return 0

        # Allow edits that do not add violations (e.g. a fix for an already-broken contract).
        (tmp_root / rel).write_text(original)
        if original or target.exists():
            before = run_linter(project_root, tmp_root)
            if before.returncode != 0 and before.stdout == after.stdout:
                log(
                    "ALLOWED",
                    tool_name,
                    rel,
                    "pre-existing violations:\n" + violations(after.stdout),
                )
                return 0

    log("BLOCKED", tool_name, rel, violations(after.stdout))
    print(
        f"import-linter would fail after this {tool_name} on {rel}:\n{after.stdout}",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # fail open: a broken hook must not block work
        log("ERROR", None, "-", repr(exc))
        print(f"importlinter hook skipped: {exc!r}", file=sys.stderr)
        sys.exit(0)
