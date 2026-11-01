#!/usr/bin/env python3
"""PostToolUse(Write|Edit|MultiEdit): fast correctness check on edited Python files.

Reports only real errors (syntax errors, undefined names, broken comparisons); never
reformats or rewrites files. Exit 2 sends the findings back to Claude to fix.
"""
import json
import os
import shutil
import subprocess
import sys


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    path = (data.get("tool_input") or {}).get("file_path") or ""
    if not path.endswith(".py") or not os.path.isfile(path):
        return

    ruff = shutil.which("ruff")
    if ruff:
        # E9 = syntax/IO errors, F63 = bad comparisons, F7 = misplaced statements, F82 = undefined names.
        cmd = [ruff, "check", "--no-cache", "--quiet", "--output-format", "concise",
               "--select", "E9,F63,F7,F82", path]
    else:
        cmd = [sys.executable, "-m", "py_compile", path]

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    except Exception:
        return
    if res.returncode != 0:
        out = (res.stdout + res.stderr).strip()
        print(f"[py_check] {os.path.basename(path)} has errors:\n{out[:2000]}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
