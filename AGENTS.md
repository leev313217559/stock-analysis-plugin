# AGENTS.md

A dsh-only stock analysis plugin: one Python CLI core, one dsh adapter, and a local dashboard.

## Architecture

- `tools/*.py` — the single source of truth for stock data and calculations. Every tool prints JSON on stdout.
- `dsh/index.ts` — dsh Cordis plugin. Registers 75 tools via `defineTool`; each tool carries inline `keywords` for discovery and dispatches to a `tools/*.py` CLI with argv, never a shell.
- `dsh/discovery.ts` — on-demand `stock_tool_search`; core tools stay eager, aliases are derived from inline keywords.
- `dsh/dashboard.ts` + `dsh/web/` — local-only dashboard server and browser UI.
- `skills/*/SKILL.md` — 21 methodology/workflow skills registered by the dsh adapter.
- `mcp_host/`, `pi/`, `openclaw/`, `hermes/` are intentionally absent in this fork; do not reintroduce them.

## Commands

```bash
npm ci --ignore-scripts
npm run build:dsh
npx tsc --noEmit
.venv/bin/python -m ruff check tools/ skills/ tests/
.venv/bin/python -m ruff format --check tools/ skills/ tests/
.venv/bin/python -m pytest -q
npm run audit:keywords
npm run export:keywords
```

dsh tests:

```bash
npx tsx tests/test_dsh_integration.ts
npx tsx tests/test_dsh_discovery.ts
npx tsx tests/test_dsh_dashboard.ts
npx tsx tests/test_dsh_web_poll.ts
npx tsx tests/test_process_tree.ts
npx tsx tests/e2e/test_dsh_e2e.ts
```

## Tool changes

A model tool is one inline definition in `dsh/index.ts`:

- add its name, description, `keywords` and parameters in the same block
- add the `script`/`argv` mapping
- update `README.md` / `dsh/README.md` if user-facing
- run the dsh integration and discovery tests
- `keywords` is required by TypeScript; the generated `docs/tool-keywords.md` is read-only

## Security

- Credentials load from `$DSH_HOME/stock-analysis.env` with mode 600; never hardcode or log keys.
- Tool stdout is JSON and may reach the model: keep secrets and stack traces out.
- Dashboard APIs are local-only and same-origin checked; do not add arbitrary Python/script execution routes.
- New dependencies go into `tools/requirements.txt`; keep them minimal and pinned where possible.

## Releases

The only published package is `dsh/`. Build with `npm run build:dsh`, verify `npm pack --dry-run` in `dsh/`, then publish via the release workflow.

## Fork policy and upstream merges (MANDATORY)

This fork intentionally supports dsh only. **Before fetching, merging or
cherry-picking upstream, read `docs/upstream-merge-guardrails.md`.** It is the
authoritative inventory of fork customizations and the conflict-resolution
rules. Never merge upstream wholesale.

Hard rules:

- Keep the host surface dsh-only. Never reintroduce `pi/`, `openclaw/`,
  `hermes/`, `mcp_host/`, `typings/openclaw/`, `scripts/tool-calls.mjs`,
  `tools/tool_schemas.json`, or their tests/docs/workflows.
- Keep tool definitions **inline** in `dsh/index.ts` (currently 75 tools) with
  inline `keywords`. Do not adopt upstream's shared schema indirection.
- Keep the fork dashboard, not upstream's: A-share breadth only, no HK/US
  breadth or `#pulse`; 120-day watchlist/index charts + intraday/MA/volume/
  OHLC; settings editor; version hint; batch quotes. Do not replace
  `dsh/web/*` or `dsh/dashboard.ts` wholesale.
- Keep Python paths/credentials: `$DSH_HOME/stock-analysis.env`,
  `$DSH_HOME/stock-analysis/`, `_credentials.py` loaded by every CLI,
  `tools/sources.py` lean/full profiles, akshare rename shims, and the
  removed-provider policy (no baostock/TIAA/youzhiyouxing; no
  Brave/Bocha/SerpAPI; adanos/Xueqiu stay key-gated).
- Keep packaging dsh-only: root package private, only
  `@leev313217559/dsh-stock-analysis` published, custom `custom-v*` release.
- Keep exactly three workflows: `ci.yml`, `canary.yml`, `custom-release.yml`.
  `autofix.yml` and `publish.yml` were deliberately deleted; never restore them
  or merge upstream workflow files wholesale.
- Keep custom tests and fixtures. If upstream adds a tool, update
  `tests/fixtures/dsh-tool-names.json`, `tests/test_dsh_discovery.ts`,
  `scripts/export-tool-keywords.mjs`, `docs/tool-keywords.md`, README/AGENTS
  counts, and tool-search cases together.
- After a merge run the full verification in the guardrails doc: Python tests,
  tsc, dsh tests, build, keyword audit, staged tarball, and a check that no
  upstream host files returned.
