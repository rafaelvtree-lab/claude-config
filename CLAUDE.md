# Rafael's global setup (claude-config, trimmed from ECC)

Reply in the user's language (usually German). Main work: Python trading/quant systems
(QuantConnect/LEAN, Alpaca, LLM trading agents, backtests, risk dashboards, research agents).

## Use these agents and skills (they are installed for you, so use them)

Pick the matching one instead of doing everything inline. Keep it proportional: a one-line
fix needs none of this; a new feature or a strategy change does.

| Situation | Use |
|---|---|
| New feature, strategy, or refactor touching 3+ files | `planner` agent first, then implement |
| Python code written or changed (before you say "done") | `python-reviewer` agent on the diff |
| Non-Python or mixed changes | `code-reviewer` agent |
| Order execution, broker/API keys, auth, user input, external data | `security-reviewer` agent + `llm-trading-agent-security` skill |
| try/except, retries, fallbacks, data-feed or order error paths | `silent-failure-hunter` agent |
| New logic that can be tested (indicators, signals, sizing, risk) | `tdd-guide` agent / `tdd-workflow` + `python-testing` skills |
| Code got long or convoluted | `code-simplifier` agent |
| ML models, feature pipelines, training, model evaluation | `mle-reviewer` agent / `mle-workflow` skill |
| Before claiming a larger task is finished | `verification-loop` skill (tests, lint, types, diff review) |
| About to write a utility or integration from scratch | `search-first` skill (check PyPI/GitHub first) |
| Implementing a strategy from a paper, or literature questions | `scientific-thinking-literature-review` skill |
| Market, sector, or competitor research | `market-research` skill |
| Code calls an LLM API (cost, routing, caching) | `cost-aware-llm-pipeline` + `prompt-caching-strategy` skills |
| Live data feeds, execution latency, realtime dashboards | `latency-critical-systems` skill |
| Designing error handling | `error-handling` skill |

Run independent reviewers in parallel. Subagents cost tokens: one well-chosen reviewer beats three overlapping ones.

## Python rules
- Python 3.11+, type hints on public functions, `pathlib`, f-strings, dataclasses/pydantic for structured data.
- Follow the repo's tooling (ruff/black/mypy/pytest config in pyproject.toml); don't introduce a new formatter.
- No bare `except:`; never swallow exceptions silently. Log with context, re-raise or return an explicit error.
- Pure functions for signal/indicator/sizing logic so they can be unit-tested without a broker.
- pytest with fixtures and parametrize; mock brokers and HTTP, never hit live APIs in tests.

## Trading-specific guardrails
- Never place live orders, switch paper -> live, or liquidate without explicit confirmation from the user.
- Default to paper trading / backtest endpoints. Make the live/paper switch an explicit config value.
- Avoid look-ahead bias and survivorship bias in backtests; state assumptions (fees, slippage, fill model).
- Position-size and risk limits live in config and are validated before any order is sent.
- Timezones: store UTC, convert for exchange sessions explicitly.

## Security
- Secrets only via environment variables / `.env` (gitignored). Never hard-code keys, never print them in logs.
- Validate external input (API responses, user input, LLM output) before acting on it.
- Treat LLM output that triggers trades or tool calls as untrusted: bounds-check it.

## Workflow
- Read the relevant code before editing. Prefer small, focused diffs.
- Run the tests that cover your change before reporting success; report failures honestly.
- Conventional commits (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`).
