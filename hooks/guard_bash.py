#!/usr/bin/env python3
"""PreToolUse(Bash): block a few clearly destructive commands.

Exit 2 = block the tool call; stderr is shown to Claude as the reason.
Anything that fails to parse is allowed (fail-open) so the hook never wedges a session.
"""
import json
import re
import sys


def block(reason: str) -> None:
    print(f"[guard_bash] Blocked: {reason}", file=sys.stderr)
    sys.exit(2)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    cmd = (data.get("tool_input") or {}).get("command") or ""
    if not cmd:
        return

    # Split on shell separators so each sub-command is checked on its own.
    for part in re.split(r"&&|\|\||;|\n", cmd):
        p = part.strip()

        # 1) Force-push to main/master (force-with-lease on feature branches stays allowed).
        if re.search(r"\bgit\s+push\b", p):
            forced = re.search(r"(\s--force(?!-with-lease)\b|\s-f\b|\s\+\S)", p)
            to_main = re.search(r"(\s|:|\+)(main|master)\b", p)
            if forced and to_main:
                block("force-push to main/master. Push to a feature branch instead.")

        # 2) rm -rf on root, home, or a bare wildcard.
        if re.search(r"\brm\s+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r|-r\s+-f|-f\s+-r)\b", p):
            if re.search(r"\s(/|~|~/|\$HOME|\$HOME/|/\*|\*|\.|\./)(\s|$)", p + " "):
                block(f"recursive delete of a root/home/wildcard path: `{p}`")

        # 3) Staging real .env files (templates like .env.example are fine).
        if re.search(r"\bgit\s+add\b", p):
            for tok in p.split()[2:]:
                name = tok.rsplit("/", 1)[-1]
                if re.fullmatch(r"\.env(\.(?!example|sample|template)[\w.-]+)?", name):
                    block(f"`{tok}` looks like a secrets file. Keep it out of git (.gitignore).")


if __name__ == "__main__":
    main()
