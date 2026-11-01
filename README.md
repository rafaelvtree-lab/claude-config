# claude-config

Mein abgespecktes Claude-Code-Setup, abgeleitet aus [Everything Claude Code (ECC)](https://github.com/affaan-m/everything-claude-code) v2.2.3.
Es funktioniert **lokal und in Cloud-Sessions** (claude.ai/code, App, `claude --cloud`).

| | ECC komplett | claude-config |
|---|---|---|
| Agents | 71 | **14** |
| Skills | 314 | **45** |
| Commands | 98 | **1** |
| Hooks | 27 Node-Hooks pro Tool-Call | **3** kleine Python-Hooks |
| Regeln | 23 Ordner | 1 kompakte `CLAUDE.md` mit klarer Zuordnung, wann welcher Agent/Skill genutzt wird |

## Inhalt

**Agents (14):**
- Code und Qualität: `planner`, `code-reviewer`, `python-reviewer`, `typescript-reviewer`, `react-reviewer`, `security-reviewer`, `tdd-guide`, `silent-failure-hunter`, `code-simplifier`, `build-error-resolver`, `database-reviewer`, `mle-reviewer`
- Marketing: `marketing-agent`, `seo-specialist`

**Skills (45):**
- Python und Qualität: `python-patterns`, `python-testing`, `tdd-workflow`, `verification-loop`, `error-handling`, `search-first`, `security-review`
- Trading und Research: `llm-trading-agent-security`, `latency-critical-systems`, `scientific-thinking-literature-review`, `market-research`, `mle-workflow`, `cost-aware-llm-pipeline`, `prompt-caching-strategy`
- Web-Apps (Vibe Coding): `frontend-patterns`, `react-patterns`, `typescript-patterns`, `nextjs-turbopack`, `frontend-design-direction`, `make-interfaces-feel-better`, `design-system`, `api-design`, `backend-patterns`, `fastapi-patterns`, `postgres-patterns`, `docker-patterns`, `deployment-patterns`, `e2e-testing`, `codebase-onboarding`
- Marketing und Business: `marketing-campaign`, `content-engine`, `article-writing`, `brand-voice`, `seo`, `competitive-platform-analysis`, `benchmark-methodology`, `competitive-report-structure`, `product-lens`, `product-capability`, `investor-materials`, `investor-outreach`
- Daten und Reporting: `dashboard-builder`, `data-scraper-agent`, `regex-vs-llm-structured-text`, `frontend-slides`. Für Datenanalyse, SQL, Diagramme und KPI-Dashboards gibt es zusätzlich das Daten-Plugin aus deinem claude.ai-Account (`data:*`), das lokal und in der Cloud schon geladen wird.

**Command:** `/python-review`. Für `/code-review`, `/security-review` und `/simplify` gibt es in Claude Code bereits eingebaute Versionen.

**Hooks:**
- `guard_bash.py`: blockiert Force-Push auf main/master, `rm -rf /` bzw. `~`, und `git add .env`
- `secret_scan.py`: blockiert hart codierte API-Keys (Alpaca, Anthropic, OpenAI, AWS, GitHub …) in Code-Dateien
- `py_check.py`: meldet nach jedem Python-Edit Syntaxfehler und undefinierte Namen (ändert nichts am Code)

**`CLAUDE.md`:** Tabelle „Situation → Agent/Skill“ sowie Regeln für Python, Trading und Security.
Die Tabelle sorgt dafür, dass Claude das Setup auch wirklich benutzt.

## Warum ECC vorher in der Cloud nie gewirkt hat

Cloud-Sessions lesen **weder** `~/.claude/` von deinem Computer **noch** Plugins (auch nicht aus der
`.claude/settings.json` eines Repos). Geladen werden dort nur Dateien aus dem geklonten Repo, Skills
aus deinem claude.ai-Account und was das Setup-Script der Umgebung auf die VM schreibt. Deshalb:

1. **Setup-Script der Cloud-Umgebung** → installiert Agents, Skills und `CLAUDE.md` nach `~/.claude/` auf der VM
2. **`.claude/settings.json` in jedem Projekt-Repo** → Hooks und ein SessionStart-Update (Hooks aus User-Settings ignoriert die Cloud)

## Einrichtung

### 1. Cloud (einmalig)
claude.ai/code → Umgebung auswählen → Einstellungen → **Setup script** → Inhalt von [`cloud-setup.sh`](cloud-setup.sh) einfügen.

### 2. Projekt-Repos (pro Repo einmal, schon erledigt für alle bestehenden Repos)
```bash
~/.claude-config/install.sh --project /pfad/zum/repo
```
Danach `.claude/settings.json` committen.

### 3. Lokal (Windows: in **Git Bash**; Mac/Linux: Terminal)
Altes ECC zuerst entfernen (siehe unten), dann:
```bash
git clone https://github.com/rafaelvtree-lab/claude-config.git ~/.claude-config
~/.claude-config/install.sh
```
Der Installer macht vorher ein Backup nach `~/.claude/backups/` und überschreibt nur seine eigenen Dateien.
Deine eigene `CLAUDE.md` und andere Einstellungen bleiben erhalten.

Update lokal: `git -C ~/.claude-config pull && ~/.claude-config/install.sh --quiet`

### Altes ECC lokal entfernen
- Als Plugin installiert: in Claude Code `/plugin uninstall ecc@ecc`, danach `/plugin marketplace remove ecc`
- Per Installer installiert: `npx ecc-universal@2.2.3 uninstall --dry-run` (zeigt, was gelöscht wird), dann ohne `--dry-run`
- Danach in `~/.claude/settings.json` prüfen, ob noch Hooks mit `CLAUDE_PLUGIN_ROOT` oder `ecc` drinstehen, und diese löschen

## Anpassen
Agent/Skill hinzufügen: Datei bzw. Ordner nach `agents/` oder `skills/` kopieren (aus ECC: `agents/<name>.md`,
`skills/<name>/`), Zeile in der Tabelle in `CLAUDE.md` ergänzen, pushen. Die Cloud holt das bei der nächsten
Session automatisch nach. Entfernen geht genauso, und der Installer räumt die alten Dateien selbst auf.

Lizenz: ECC-Inhalte unter MIT (siehe `LICENSE.ecc`).
