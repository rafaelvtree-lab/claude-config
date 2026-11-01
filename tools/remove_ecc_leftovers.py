"""Remove leftovers of the old ECC plugin from ~/.claude/settings.json (backup first)."""
import json, pathlib, shutil
p = pathlib.Path.home() / ".claude" / "settings.json"
shutil.copy(p, p.with_name("settings.json.bak-ecc"))
d = json.loads(p.read_text(encoding="utf-8"))
d.get("env", {}).pop("ECC_DISABLED_HOOKS", None)
if d.get("env") == {}:
    d.pop("env")
def is_ecc(x):
    s = x.get("serverName", "") if isinstance(x, dict) else x
    return isinstance(s, str) and s.startswith("plugin:ecc:")
def clean(o):
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, list):
        return [clean(x) for x in o if not is_ecc(x)]
    return o
d = {k: v for k, v in clean(d).items() if v != []}
p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("settings.json bereinigt, Backup: settings.json.bak-ecc")
