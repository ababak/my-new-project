#!/usr/bin/env python3
"""PreToolUse hook: apply the pending edit to a temp copy and block it if import-linter fails."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

LAYERS = ("domain", "application", "infrastructure", "presentation")
LOG_FILE = Path(__file__).resolve().parent.parent / "importlinter.log"


def log(outcome: str, tool_name: str | None, rel: Path | str, detail: str = "") -> None:
    line = f"{datetime.now().astimezone():%Y-%m-%dT%H:%M:%S%z} [{outcome}] [{tool_name}] {rel}"
    if detail:
        line += "\n" + "\n".join(f"  {d}" for d in detail.splitlines())
    with LOG_FILE.open("a") as f:
        f.write(line + "\n")


def violations(output: str) -> str:
    return "\n".join(ln for ln in output.splitlines() if "->" in ln or "is not allowed" in ln)


def apply_edit(text: str, old: str, new: str, replace_all: bool) -> str | None:
    count = text.count(old) if old else 0
    if count == 0 or (count > 1 and not replace_all):
        return None  # the Edit tool itself will report this error
    return text.replace(old, new) if replace_all else text.replace(old, new, 1)


def pick(d: dict[str, Any], *keys: str) -> Any:
    return next((d[k] for k in keys if k in d), None)


def planned_contents(tool_name: str | None, tool_input: dict[str, Any]) -> dict[Path, str] | None:
    """Content of every touched file after the tool runs; None if unsupported or not applicable."""
    contents: dict[Path, str] = {}
    if tool_name in ("Write", "create_file"):
        path = Path(pick(tool_input, "file_path", "filePath")).resolve()
        contents[path] = tool_input.get("content", "")
        return contents
    if tool_name == "MultiEdit":
        edits = [{**e, "file_path": tool_input["file_path"]} for e in tool_input["edits"]]
    elif tool_name == "multi_replace_string_in_file":
        edits = tool_input["replacements"]
    elif tool_name in ("Edit", "replace_string_in_file"):
        edits = [tool_input]
    else:
        return None
    for e in edits:
        path = Path(pick(e, "file_path", "filePath")).resolve()
        text = contents.get(path)
        if text is None:
            text = path.read_text() if path.exists() else ""
        text = apply_edit(
            text,
            pick(e, "old_string", "oldString") or "",
            pick(e, "new_string", "newString") or "",
            bool(pick(e, "replace_all", "replaceAll")),
        )
        if text is None:
            return None
        contents[path] = text
    return contents


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
    project_root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd", ".")).resolve()

    changes = planned_contents(tool_name, data.get("tool_input", {}))
    if not changes:
        return 0
    updated: dict[Path, str] = {}
    for path, text in changes.items():
        try:
            rel = path.relative_to(project_root)
        except ValueError:
            continue
        if path.suffix == ".py" and rel.parts[0] in LAYERS:
            updated[rel] = text
    if not updated:
        return 0
    names = ", ".join(str(r) for r in updated)
    originals = {
        rel: (project_root / rel).read_text() if (project_root / rel).exists() else None
        for rel in updated
    }

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
        for rel, text in updated.items():
            (tmp_root / rel).parent.mkdir(parents=True, exist_ok=True)
            (tmp_root / rel).write_text(text)

        after = run_linter(project_root, tmp_root)
        if after.returncode == 0:
            log("PASS", tool_name, names)
            return 0

        # Allow edits that do not add violations (e.g. a fix for an already-broken contract).
        for rel, original in originals.items():
            if original is None:
                (tmp_root / rel).unlink(missing_ok=True)
            else:
                (tmp_root / rel).write_text(original)
        before = run_linter(project_root, tmp_root)
        if before.returncode != 0 and before.stdout == after.stdout:
            log(
                "ALLOWED",
                tool_name,
                names,
                "pre-existing violations:\n" + violations(after.stdout),
            )
            return 0

    log("BLOCKED", tool_name, names, violations(after.stdout))
    print(
        f"import-linter would fail after this {tool_name} on {names}:\n{after.stdout}",
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
