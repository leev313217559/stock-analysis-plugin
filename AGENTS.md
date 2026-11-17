# AGENTS.md

A dsh-only stock analysis plugin: one Python CLI core, one dsh adapter, and a local dashboard.

## Architecture

- `tools/*.py` — the single source of truth for stock data and calculations. Every tool prints JSON on stdout.
- `dsh/index.ts` — dsh Cordis plugin. Registers 74 tools via `defineTool`; each tool carries inline `keywords` for discovery and dispatches to a `tools/*.py` CLI with argv, never a shell.
- `dsh/discovery.ts` — on-demand `stock_tool_search`; core tools stay eager, aliases are derived from inline keywords.
- `dsh/dashboard.ts` + `dsh/web/` — local-only dashboard server and browser UI.
- `skills/*/SKILL.md` — 21 methodology/workflow skills registered by the dsh adapter.
- `mcp_host/`, `pi/`, `openclaw/`, `hermes/` are intentionally absent in this fork; do not reintroduce them.

## Commands

```bash
npm ci --ignore-scripts
npm run build:dsh
npx tsc --noEmit
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
- run the parity and discovery tests
- `keywords` is required by TypeScript; the generated `docs/tool-keywords.md` is read-only

## Security

- Credentials load from `$DSH_HOME/stock-analysis.env` with mode 600; never hardcode or log keys.
- Tool stdout is JSON and may reach the model: keep secrets and stack traces out.
- Dashboard APIs are local-only and same-origin checked; do not add arbitrary Python/script execution routes.
- New dependencies go into `tools/requirements.txt`; keep them minimal and pinned where possible.

## Releases

The only published package is `dsh/`. Build with `npm run build:dsh`, verify `npm pack --dry-run` in `dsh/`, then publish via the release workflow.

## Fork policy

This fork intentionally supports dsh only. Upstream multi-host code must not be merged back in bulk; cherry-pick Python core or dsh changes only.
