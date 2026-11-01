#!/usr/bin/env python3
"""PreToolUse(Write|Edit|MultiEdit): stop hard-coded secrets from landing in source files.

Writes to .env-style files are allowed (they belong there, and should be gitignored).
Exit 2 = block; stderr goes to Claude, which should switch to os.environ / a .env file.
"""
import json
import re
import sys

PATTERNS = [
    ("Anthropic API key", r"sk-ant-[A-Za-z0-9_\-]{20,}"),
    ("OpenAI API key", r"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_\-]{32,}"),
    ("Alpaca API key ID", r"\b(?:PK|AK|CK)[A-Z0-9]{18}\b"),
    ("AWS access key", r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    ("GitHub token", r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{60,})\b"),
    ("Slack token", r"\bxox[abprs]-[A-Za-z0-9-]{10,}"),
    ("Google API key", r"\bAIza[0-9A-Za-z_\-]{35}\b"),
    ("Private key block", r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----"),
    (
        "Hard-coded credential",
        r"(?i)\b(?:api[_-]?key|secret[_-]?key|api[_-]?secret|access[_-]?token|auth[_-]?token|password|passwd)\b"
        r"\s*[:=]\s*['\"](?!\s*(?:\$\{|<|your|xxx|changeme|example|dummy|test|placeholder))[^'\"\s]{16,}['\"]",
    ),
]

ALLOWED_FILE = re.compile(r"(^|/)\.env(\.[\w.-]+)?$|\.(example|sample|template)$")


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    ti = data.get("tool_input") or {}
    path = ti.get("file_path") or ""
    if ALLOWED_FILE.search(path):
        return

    chunks = [ti.get("content") or "", ti.get("new_string") or ""]
    for edit in ti.get("edits") or []:
        chunks.append((edit or {}).get("new_string") or "")
    text = "\n".join(chunks)
    if not text:
        return

    for label, pat in PATTERNS:
        m = re.search(pat, text)
        if m:
            snippet = m.group(0)
            masked = snippet[:6] + "…" + snippet[-2:] if len(snippet) > 10 else "…"
            print(
                f"[secret_scan] Blocked write to {path or 'file'}: looks like a {label} ({masked}). "
                "Load it from the environment instead (os.environ / python-dotenv + .env in .gitignore).",
                file=sys.stderr,
            )
            sys.exit(2)


if __name__ == "__main__":
    main()
