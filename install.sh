#!/usr/bin/env bash
# claude-config installer
#
#   ./install.sh                 local install into ~/.claude (backs up first, merges hooks into settings.json)
#   ./install.sh --cloud         cloud-session install (no settings.json: cloud ignores user settings)
#   ./install.sh --project DIR   add the hook config to DIR/.claude/settings.json (commit it in that repo)
#   ./install.sh --quiet         less output
#
# Re-running is safe: it updates its own files and removes ones that were dropped from this repo.
# It never touches agents/skills/commands it did not install.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
MANIFEST="$CLAUDE_DIR/.claude-config-manifest"
MODE=local
QUIET=0
PROJECT=""

while [ $# -gt 0 ]; do
  case "$1" in
    --cloud) MODE=cloud ;;
    --quiet) QUIET=1 ;;
    --project) MODE=project; PROJECT="${2:?--project needs a directory}"; shift ;;
    -h|--help) sed -n '2,11p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 1 ;;
  esac
  shift
done

PY="$(command -v python3 || command -v python || true)"
[ -n "$PY" ] || { echo "[claude-config] python3/python not found" >&2; exit 1; }

log() { [ "$QUIET" = 1 ] || echo "[claude-config] $*"; }

# merge_hooks SRC_JSON DEST_JSON: add our hook entries to DEST without duplicating or dropping others.
merge_hooks() {
  "$PY" -I - "$1" "$2" <<'PY'
import json, os, sys
src, dest = sys.argv[1], sys.argv[2]
new = json.load(open(src))
cur = {}
if os.path.exists(dest):
    with open(dest) as f:
        txt = f.read().strip()
    cur = json.loads(txt) if txt else {}
hooks = cur.setdefault("hooks", {})
for event, groups in new["hooks"].items():
    existing = hooks.setdefault(event, [])
    have = {h.get("command") for g in existing for h in g.get("hooks", [])}
    for g in groups:
        if not all(h["command"] in have for h in g["hooks"]):
            existing.append(g)
os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
with open(dest, "w") as f:
    json.dump(cur, f, indent=2)
    f.write("\n")
PY
}

if [ "$MODE" = project ]; then
  merge_hooks "$REPO/templates/project-settings.json" "$PROJECT/.claude/settings.json"
  log "hooks added to $PROJECT/.claude/settings.json (commit it)"
  exit 0
fi

mkdir -p "$CLAUDE_DIR"/{agents,skills,commands,hooks,backups}

if [ "$MODE" = local ]; then
  ts="$(date +%Y%m%d-%H%M%S)"
  backup="$CLAUDE_DIR/backups/pre-claude-config-$ts.tar.gz"
  (cd "$CLAUDE_DIR" && tar czf "$backup" --ignore-failed-read \
      agents skills commands hooks rules CLAUDE.md settings.json 2>/dev/null) || true
  log "backup: $backup"
fi

# Remove files from a previous run that no longer exist in this repo.
if [ -f "$MANIFEST" ]; then
  while IFS= read -r rel; do
    [ -n "$rel" ] || continue
    [ -e "$REPO/$rel" ] || rm -rf "${CLAUDE_DIR:?}/$rel"
  done < "$MANIFEST"
fi

: > "$MANIFEST.tmp"
for f in "$REPO"/agents/*.md "$REPO"/commands/*.md "$REPO"/hooks/*.py; do
  rel="${f#"$REPO"/}"
  cp "$f" "$CLAUDE_DIR/$rel"
  echo "$rel" >> "$MANIFEST.tmp"
done
for d in "$REPO"/skills/*/; do
  name="$(basename "$d")"
  rm -rf "${CLAUDE_DIR:?}/skills/$name"
  cp -R "$d" "$CLAUDE_DIR/skills/$name"
  echo "skills/$name" >> "$MANIFEST.tmp"
done
chmod +x "$CLAUDE_DIR"/hooks/*.py 2>/dev/null || true
mv "$MANIFEST.tmp" "$MANIFEST"

# Global CLAUDE.md: replace only our marked block, keep anything else the user wrote.
"$PY" -I - "$REPO/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md" <<'PY'
import os, re, sys
src, dest = sys.argv[1], sys.argv[2]
start, end = "<!-- claude-config:start -->", "<!-- claude-config:end -->"
block = f"{start}\n{open(src).read().strip()}\n{end}"
cur = open(dest).read() if os.path.exists(dest) else ""
if start in cur and end in cur:
    cur = re.sub(re.escape(start) + r".*?" + re.escape(end), lambda m: block, cur, flags=re.S)
else:
    cur = (cur.rstrip() + "\n\n" if cur.strip() else "") + block
open(dest, "w").write(cur.rstrip() + "\n")
PY

if [ "$MODE" = local ]; then
  merge_hooks "$REPO/templates/user-settings.json" "$CLAUDE_DIR/settings.json"
  log "hooks merged into $CLAUDE_DIR/settings.json"
fi

log "installed $(ls "$REPO"/agents | wc -l | tr -d ' ') agents, $(ls -d "$REPO"/skills/*/ | wc -l | tr -d ' ') skills, $(ls "$REPO"/commands | wc -l | tr -d ' ') command(s), $(ls "$REPO"/hooks | wc -l | tr -d ' ') hooks into $CLAUDE_DIR"
