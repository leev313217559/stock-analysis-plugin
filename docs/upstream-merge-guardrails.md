# Upstream merge guardrails (dsh-only fork)

This file is part of the project contract. **Read it before fetching or merging
anything from `upstream`.** It records the fork's intentional changes, why they
exist, and how to resolve conflicts without losing them.

If this file and an upstream README/AGENTS/doc disagree, this file and the
`dsh`-only fork policy win.

## 1. Non-negotiable fork invariants

1. **dsh is the only supported host.**
   `pi/`, `openclaw/`, `hermes/`, `mcp_host/`, `typings/openclaw/`,
   `scripts/tool-calls.mjs` and `tools/tool_schemas.json` must not be
   reintroduced. Also do not reintroduce their tests, docs, workflows, stubs or
   package entries.
2. **The dsh adapter owns its tool definitions.**
   Every model tool is an inline `defineTool(...)` / `pyTool(...)` block in
   `dsh/index.ts`, with its own `keywords`. Do not switch to upstream's shared
   `tool_schemas.json` + `tool-calls.mjs` indirection.
3. **Current tool count is 75 and skills count is 21.**
   The canonical names are in `tests/fixtures/dsh-tool-names.json`. The
   generated keyword inventory is `docs/tool-keywords.md`.
4. **The dashboard is a fork-specific UI, not upstream's dashboard.**
   It is A-share-breadth-only, has 120-day watchlist/index charts, intraday
   cards, a credentials editor, and a version/update hint. Do not replace it
   with upstream `dsh/web/` files. Do not add HK/US breadth or the upstream
   `#pulse` strip.
5. **The Python core keeps the fork's data-path, credentials and source policy.**
   `DSH_HOME` paths, the credential-file loader, `lean`/`full` source profiles,
   akshare rename shims, removed providers, and the healthcheck/canary contract
   are custom. Preserve them when merging upstream `tools/`.
6. **Only the dsh npm package is published.**
   Fork names are `@leev313217559/stock-analysis-plugin` (private root dev
   workspace) and `@leev313217559/dsh-stock-analysis` (published bundle).
   Do not restore root/PyPI/OpenClaw publishing. Only three workflows are
   maintained: `ci.yml`, `canary.yml`, `custom-release.yml`;
   `autofix.yml` and `publish.yml` are intentionally deleted.
7. **Never merge upstream wholesale.**
   `git merge upstream/main` or a blind `git checkout --theirs` on `dsh/`,
   `tests/`, `README.md`, `AGENTS.md`, `package.json`, `pyproject.toml` or
   `.github/workflows/` will destroy fork work.
8. **After every merge, the dsh-only shape must still be true.**
   Run the verification checklist in section 6 before pushing.

## 2. Customization inventory

### Chronology (why this fork looks the way it does)

| period / commit(s) | fork customization |
|---|---|
| `5f9b66c`, `0f7c220` | Renamed packages to `@leev313217559/*`; added the independent `custom-v*` tarball release; stopped depending on upstream CI for release builds. |
| `3519ee5`, `b90b694`, `a285b25`, `ceefdd3` | Added akshare 1.20.44+ rename shims, compatibility tests, and Python 3.10 aliases. |
| `02a70c2` | Made dsh-only e2e skip cleanly when LLM secrets are absent. |
| `4cf6683` | Added data-source healthcheck, scheduled canary, canary issue reporting and Dependabot. |
| `512fa85` | Added `lean`/`full` source profiles, contract fixtures and source audit. |
| `aa7094f`, `65c9285` | Removed baostock, TIAA/youzhiyouxing, extra search clients and some sentiment; then deliberately restored key-gated adanos and wired Xueqiu token. |
| `e2c0231`, `7d8938f`, `8428b35`, `ece5f64` | Added `$DSH_HOME` credential loading, unified data paths, the dashboard credentials editor and settings behavior. |
| `204d4bd`, `3a62116`, `6fbf9a5`, `fcb4c66`, `ab82b09` | Added inline tool keywords, the alias index, eager core tools, Chinese query normalization, keyword audit/export, docs and search-case fixtures. |
| `1a77d11`, `b108953`, `b09f787`, `c498880`, `a3b2c12`, `8a85fbc` | Reworked the dashboard: intraday cards, 120-day watchlist/index charts, compact layout, delay tooltip, docs/screenshots. |
| `98d2a9e`, `bba4ae7`, `ba73c4f` | Historical canary fixes (Shenzhen index fallback, unpriced breadth warning, fast snapshot); the fast-snapshot/index-fallback code was later superseded by upstream #91. |
| `6f3f5a4` | Removed all non-dsh hosts, host tests/docs/workflows and shared schema indirection; made the repo and packaging dsh-only. |
| `5a9bdea`, `cace5d3`, `3a1e84d`, `1427321`, `655ec48` | Ported upstream CDS, full-market-table removal, version hint, batch quotes; dropped legacy baostock again. These are fork integrations, not wholesale upstream merges. |

The inventory below describes the **current** state; the chronology is for
understanding why a later upstream change may conflict.

### A. Host surface and repository shape

| Customization | Current files / behavior | Merge rule |
|---|---|---|
| dsh-only host surface | `pi/`, `openclaw/`, `hermes/`, `mcp_host/`, `typings/openclaw/`, `scripts/tool-calls.mjs`, `tools/tool_schemas.json` are intentionally absent | Keep deleted. Upstream re-adds them as modify/delete conflicts; resolve deletions. |
| Host tests/e2e/docs removed | Pi/OpenClaw/Hermes/MCP integration tests, host e2e, `docs/*-integration.md`, `docs/mcp.md`, host OpenClaw manifest references | Keep deleted; do not port their test fixtures. |
| Root package is a private dev workspace | `package.json`: `private: true`, no `main`/`pi`/`files`/`build:openclaw`, dsh-only scripts | Keep private and dsh-only; take only dependency/version facts from upstream. |
| Python packaging is tools-only | `pyproject.toml`: no hatch build, no `hermes`/`mcp_host` packages, no PyPI entry points | Keep tools-only metadata. Do not restore `build-system`/Hermes entry points. |
| dsh-only CI | `.github/workflows/ci.yml`: Python matrix + dsh/compat/e2e/build; no host matrix | Keep host jobs out. Preserve e2e secret-skip behavior. |
| dsh-only CI/release | Only `.github/workflows/ci.yml`, `canary.yml` and `custom-release.yml` are allowed. `autofix.yml` and `publish.yml` were deliberately deleted (never used; publish conflicts with `custom-v*` release). | Never restore `autofix.yml` or `publish.yml`; do not take upstream workflow files wholesale. |
| Fork documentation | `README.md`, `AGENTS.md`, `dsh/README.md`, `docs/source-profiles.md`, `docs/source-audit.md`, `docs/tool-keywords.md` are fork-oriented | Keep ours; port only factual upstream changes manually. |
| Fork screenshots | `docs/images/dsh-dashboard-*.png` are the fork's screenshots | Do not overwrite with upstream old screenshots. |

### B. dsh adapter, tools and discovery

| Customization | Current files / behavior | Merge rule |
|---|---|---|
| Inline tool definitions | `dsh/index.ts` has 75 inline tool blocks with `script`/`argv`, output renderers and `keywords`; no shared schema lookup | New upstream tools must be ported manually into inline blocks. Never replace `dsh/index.ts` with upstream's schema-driven adapter. |
| Inline keyword metadata | Each tool has `keywords`; discovery derives the alias index from them | Preserve keywords when porting a tool; update `docs/tool-keywords.md` via the export script. |
| Eager core tools | `dsh/discovery.ts` `CORE_TOOLS`: `get_quote`, `get_kline`, `get_market_indices`, `get_market_stats`, `get_technical_analysis`, `get_news` stay visible without search | Do not merge upstream's discovery wholesale; keep core-eager behavior. |
| Chinese-normalized discovery | `stock_tool_search` normalizes Chinese functional terms, keeps finance abbreviations/codes, uses weighted terms, bigrams and an alias table | Preserve. Upstream's simpler scoring/description must not overwrite it. |
| Tool count is coupled | `dsh/index.ts` (75) + `tests/fixtures/dsh-tool-names.json` (75) + `tests/test_dsh_discovery.ts` (75) + `scripts/export-tool-keywords.mjs` hardcoded 75 + README/AGENTS/dsh README counts | When upstream adds/removes a tool, update **all** of these in the same change. |
| Tool names without host manifest | `tests/fixtures/dsh-tool-names.json` replaces upstream's use of `openclaw/openclaw.plugin.json` | Keep the fixture; do not restore manifest reads in dsh tests. |
| Keyword tooling | `scripts/audit-tool-keywords.mjs`, `scripts/export-tool-keywords.mjs`, `scripts/lib/tool-keywords.mjs`, `docs/tool-keywords.md`, `tests/fixtures/tool-search-cases.json` | Keep; port data changes only. `export` must fail if the count/parser is wrong, not silently truncate. |
| dsh research presets | `dsh/research-role.ts`, `dsh/research.patch.yml`, `dsh/deepseek-search.patch.yml`; package ids use the fork package name | Preserve fork package ids in patch files. |

### C. Dashboard and browser UI

| Customization | Current files / behavior | Merge rule |
|---|---|---|
| A-share breadth only | `dsh/dashboard.ts` has a single `stats` slot; `dsh/web/index.html` has no `#pulse`; `CN_INDEX_SYMBOLS` is only `sh000001`, `sz399001`, `sz399006` | Do **not** merge upstream `STATS_MARKETS`/HK/US breadth, `#pulse`, or the 6-code CN index list. This is an explicit product decision. |
| 120-day charts | Watchlist trend is 120 days; index cards use `index_chart.py --days 120` with intraday, MA5/MA20/MA60, volume, OHLC and hover details | Preserve `tools/index_chart.py`, `chartJob`, chart SVG code and 120-day commands. Do not let upstream's 30-day chart replace them. |
| Dashboard layout | Flattened index section, compact session row, exact delay badge/tooltip, index tiles, A-share-only stats panel | Keep our `dsh/web/app.ts`, `style.css` and `index.html`; port only genuinely relevant upstream fixes manually. |
| Credentials editor | Dashboard settings modal + `/api/config`; reads/writes `$DSH_HOME/stock-analysis.env`; atomic write, mode 600, mtime conflict check, same-origin guard | Preserve endpoints, security checks and config template. Do not accept upstream path-only config changes. |
| Version/update hint | Footer shows installed package version; npm latest check is throttled; header pill opens the plugin page; fork GitHub URL | Was ported from upstream with fork adaptations. Keep the hint and fork URL; merge upstream logic only if it does not regress. |
| Batch quotes | `dsh/dashboard.ts` coalesces due quotes into one `stock_data.py quotes` process; per-symbol slots/backoff remain | This is upstream #93 but already integrated with our UI. Keep the batch path; do not revert to per-symbol `quote` subprocesses. |
| Local-only security | Dashboard accepts only fixed routes/parameters; no arbitrary Python/script execution; same-origin checks | Do not add generic proxy/script endpoints while merging dashboard changes. |

### D. Python data layer, credentials and paths

| Customization | Current files / behavior | Merge rule |
|---|---|---|
| `DSH_HOME` layout | `tools/_paths.py`, `dsh/paths.ts`: config `$DSH_HOME/stock-analysis.env`; state `$DSH_HOME/stock-analysis/`; per-file env overrides for tests | Preserve; upstream's `Path.home()`/`~/.stock-analysis` defaults must not return. |
| Credential file loader | `tools/_credentials.py`; loaded by `utf8_stdio()` in every CLI; `KEY=VALUE`, comments, quotes, real env wins; never log values | Preserve loader and startup call. Do not replace with host-specific credential code. |
| Unified state paths | `tools/_cache.py`, `watchlist.py`, `signal_tracker.py`, `market_review.py` use `_paths.data_dir()` | Preserve `$DSH_HOME` resolution and env overrides. |
| Source profiles | `tools/sources.py`: `DATA_SOURCE_PROFILE=lean` default, `full` for upstream chains; `_yf_failover` applies profile; tests default to `full` | Preserve `LEAN`, `LABEL_CAPABILITIES`, `select`/`select_for_label` and the `_yf_failover` hook. Do not flatten chains. |
| Provider policy | Removed: baostock, TIAA/youzhiyouxing, Brave/Bocha/SerpAPI search clients. Kept key-gated: adanos, Xueqiu, tushare, longbridge, finnhub, alphavantage, lixinger; baidu hot-stock backstop; efinance fund-flow backstop | Do not re-add removed providers while merging. Adanos stays key-gated; Xueqiu uses `XUEQIU_TOKEN`. |
| akshare compatibility | `_ak_any` in `stock_data.py`, `index_hist_csindex`/`index_value_csindex` in `value_data.py`, renamed calendar/spot APIs; `tests/conftest.py` aliases old CSI names for Python 3.10; `tests/test_akshare_api_compat.py` guards | Keep shims and compat test. Upstream may use a single name; resolve both names. |
| Removed legacy K-line fallback | `tools/stock_data.py` chain is akshare → tushare → efinance → tencent (no baostock); `tools/requirements.txt` has no baostock | Keep baostock out. The old canary/fast-snapshot workarounds were superseded by upstream #91; do not restore them. |
| Contract fixtures | `tests/fixtures/contracts/` + `tests/test_output_contracts.py` assert normalized CLI shapes offline | Preserve fixtures/test; update deliberately only when a contract intentionally changes. |
| Search/sentiment | `tools/search_intel.py`: Tavily + SearXNG; adanos X-API-Key endpoints; Xueqiu token-gated | Preserve provider set/routes; don't restore removed search clients. |

### E. Reliability, CI and healthcheck

| Customization | Current files / behavior | Merge rule |
|---|---|---|
| Production healthcheck | `scripts/healthcheck.py` runs real CLI checks; transient/rate-limit/HTML gateway warnings; hard failures exit nonzero | Preserve check names, transient markers, JSON shape and exit semantics. |
| Scheduled canary | `.github/workflows/canary.yml`: weekdays, hard-failure issue open/update, recovery close, artifact; `tests/test_healthcheck.py` | Keep workflow; port upstream fixes only after adapting to current check names/fields. |
| Dependabot | `.github/dependabot.yml` for pip/npm/GitHub Actions | Keep. |
| Fork-friendly e2e | `ci.yml` e2e jobs skip when LLM secrets absent; no host matrix; `e2e-host` only dsh | Keep skip behavior. |
| Baostock-free CI | CI installs `tools/requirements.txt` only; baostock is not there | Never add a test that needs an optional dependency not in requirements. This caused a red CI on commit 1427321. |
| Canary diagnostics | Healthcheck should not fail on unpriced breadth rows; old `fast snapshot`/Shenzhen fallback fixes are historical, superseded by the #91 server-side stats refactor | Do not blindly restore old snapshot helpers; validate against current `market_stats`. |

### F. Packaging and release

| Customization | Current files / behavior | Merge rule |
|---|---|---|
| Fork package names | `@leev313217559/stock-analysis-plugin` (private root), `@leev313217559/dsh-stock-analysis` (published dsh bundle) | Keep names, repository URL and patch ids. |
| Custom tarball release | `.github/workflows/custom-release.yml`, tags `custom-v*`, manual version input; builds/stages/packs dsh payload | Keep workflow; do not replace with upstream release. |
| Payload staging | `dsh/` gets `tools/`, `skills/`, `schemas/`, `templates/`, `strategies/`, `scripts/` copied (symlinks in dev; copies in release) | Preserve staging and verification; dsh package must include tools/scripts. |
| dsh manifest | `dsh/package.json` `dsh.bundle.patch`, `files`, exports, peer deps | Keep fork name and payload list. |
| Version sync | `scripts/sync-version.sh` updates pyproject + root + `dsh` only; `scripts/setup-python.mjs`/`venv-python.mjs` have no OpenClaw logic | Do not restore OpenClaw/PyPI version handling. |
| Release guards | `custom-release.yml` checks the fork package id, `dist/index.js`, patch files, web assets, LICENSE and the packed payload | Preserve checks; adapt only paths if packaging changes. |

### G. Tests, fixtures and docs to keep

These are fork-specific and must not be dropped when taking upstream test changes:

- `tests/fixtures/dsh-tool-names.json` (75 names)
- `tests/fixtures/tool-search-cases.json`
- `tests/fixtures/contracts/` + `tests/test_output_contracts.py`
- `tests/test_akshare_api_compat.py`
- `tests/test_credentials.py`, `tests/test_paths.py`
- `tests/test_source_profiles.py`, `tests/test_healthcheck.py`
- `tests/test_index_chart.py`
- `tests/test_dsh_dashboard.ts`, `tests/test_dsh_discovery.ts`, `tests/test_dsh_integration.ts`, `tests/test_dsh_web_poll.ts`
- `docs/source-audit.md`, `docs/source-profiles.md`, `docs/tool-keywords.md`
- `tests/conftest.py`: `DATA_SOURCE_PROFILE=full`, `STOCK_ANALYSIS_ENV_FILE=/dev/null`, Python 3.10 CSI aliases, SEC test throttle stub

## 3. Historical decisions and superseded code

These were intentional at the time but are **not** current code; do not
reintroduce them just because an old branch/commit mentions them:

- **Fast efinance market-stats snapshot / Shenzhen index fallback** (commits
  `ba73c4f`, `98d2a9e`): superseded by upstream #91's server-side filtered
  stats and index queries. The canary now validates the current
  `market_stats`/`index_chart` paths.
- **Unpriced breadth rows as canary warning** (`bba4ae7`): keep the *policy*
  (warn, don't hard-fail), but the old breadth implementation is not current.
- **Adanos removal**: it was removed then deliberately restored (`65c9285`).
  Current policy is key-gated adanos; do not remove it again without an explicit
  decision.
- **baostock removal**: was removed, accidentally reintroduced by upstream #91,
  removed again in `655ec48`. Keep it removed.
- **TIAA / youzhiyouxing**: removed from code and tests; do not restore the old
  portfolio metadata path.
- **Upstream #90 (dashboard version/update)**: we keep only the version/update
  hint; upstream's HK/US breadth and layout changes are intentionally not
  merged (A-only product decision).
- **Upstream #91 (full-market table removal)**: accepted core refactor; do not
  restore full-market snapshots.
- **Upstream #92 (CDS/asymmetric risk)**: accepted; `get_cds_index` is now an
  inline dsh tool (75th), with keywords/tests.
- **Upstream #93 (batch dashboard quotes)**: accepted and integrated with our
  dashboard; do not revert to per-symbol quote subprocesses.

## 4. Upstream merge procedure

### 4.1 Inspect before touching the worktree

```bash
git fetch upstream --prune
git log --oneline --date=short upstream/main -10
git log --oneline upstream/main..custom
git diff --stat custom...upstream/main
```

Identify whether each upstream file is:

- **core Python/data** — merge, then re-apply custom shims;
- **dsh adapter/tool/dashboard** — manual port only;
- **host-only** — discard/deleted;
- **docs/CI/package** — keep fork version and port only facts.

### 4.2 Work on a temporary branch

```bash
git switch -c merge/upstream-<short-sha> custom
git merge --no-commit --no-ff <upstream-sha>
```

Do not use `git pull upstream main` directly on `custom` and do not push the
temporary branch after merging.

### 4.3 Resolve by category

- **Host-only conflicts (`pi/`, `openclaw/`, `hermes/`, `mcp_host/`,
  `typings/openclaw/`, host docs/tests, `tools/tool_schemas.json`,
  `scripts/tool-calls.mjs`)**: keep deleted:
  ```bash
  git rm -r --ignore-unmatch pi openclaw hermes mcp_host typings/openclaw \
    tools/tool_schemas.json scripts/tool-calls.mjs
  ```
- **`dsh/index.ts`**: never `--theirs`. Start from our file and port new tool
  blocks (name, description, parameters, keywords, script/argv). Update the
  canonical fixture, tool count, audit/export count, README counts.
- **`dsh/discovery.ts`**: keep eager `CORE_TOOLS`, alias index and Chinese
  normalization; do not take upstream's simpler scoring wholesale.
- **`dsh/dashboard.ts`, `dsh/web/app.ts`, `dsh/web/index.html`,
  `dsh/web/style.css`**: keep ours; cherry-pick only small relevant fixes
  (e.g., batch quotes, bug fixes) and preserve A-only breadth/120-day charts/
  settings/version hint.
- **`tools/*.py`**: merge upstream logic, then verify custom shims remain:
  `_ak_any`, CSI wrappers, `sources.select`, `_yf_failover` profile, no
  baostock/TIAA, `_paths`/`_credentials` imports, `_subproc` credential load.
- **`tests/`**: keep custom tests/fixtures; update counts; do not delete
  custom regression tests just because upstream lacks them.
- **`README.md`, `AGENTS.md`, `dsh/README.md`, docs**: keep fork structure;
  take only factual upstream changes that are still true for dsh-only.
- **`package.json`, `pyproject.toml`, `.github/workflows/`**: keep dsh-only
  versions; port dependency versions only. Upstream re-adds `autofix.yml` and
  `publish.yml`: keep them deleted. Only `ci.yml`, `canary.yml` and
  `custom-release.yml` may exist.
- **`dsh/package.json`, patch files, `scripts/sync-version.sh`**: keep fork
  package ids and payload rules.

### 4.4 Forbidden shortcuts

- Do not `git checkout --theirs` on `dsh/`, `tests/test_dsh_*`,
  `tests/fixtures/`, `README.md`, `AGENTS.md`, `package.json`, `pyproject.toml`
  or `.github/workflows/`.
- Do not accept an upstream commit merely because its CI passed: upstream CI
  does not test this fork's dashboard/product requirements.
- Do not “clean up” custom files by replacing them with upstream copies.
- Do not add optional runtime dependencies without adding them to
  `tools/requirements.txt` and a CI test.

## 5. What to do when upstream adds a tool

1. Add an inline `pyTool`/`renderTool` block in `dsh/index.ts`.
2. Add Chinese + English `keywords` (>= 8; >= 12 for high-frequency tools).
3. Add `script`/`argv`; never shell-interpolate.
4. Add the name to `tests/fixtures/dsh-tool-names.json`.
5. If needed, add `tools/capabilities.py` matrix entry and `get_cds_index`-style
   market support.
6. Update:
   - `tests/test_dsh_discovery.ts` (`75` → new count)
   - `scripts/export-tool-keywords.mjs` hardcoded expected count
   - `README.md`, `AGENTS.md`, `dsh/README.md` counts
7. Run `npm run export:keywords` and `npm run audit:keywords`.
8. Add a tool-search case to `tests/fixtures/tool-search-cases.json` when the
   tool has user-facing synonyms.
9. Add/update tests (dsh integration, Python if applicable) and dashboard
   tool docs.

## 6. Post-merge verification checklist

Run from the repository root:

```bash
npm ci --ignore-scripts
npx tsc --noEmit
npm run build:dsh
npm run audit:keywords
npm run export:keywords
.venv/bin/python -m ruff check tools/ skills/ tests/
.venv/bin/python -m ruff format --check tools/ skills/ tests/
.venv/bin/python -m pytest -q

npx tsx tests/test_dsh_integration.ts
npx tsx tests/test_dsh_discovery.ts
npx tsx tests/test_dsh_dashboard.ts
npx tsx tests/test_dsh_web_poll.ts
npx tsx tests/test_json_input.ts
npx tsx tests/test_process_tree.ts
npx tsx tests/e2e/test_dsh_e2e.ts
```

Then verify the fork shape:

```bash
# must print exactly ci.yml, canary.yml, custom-release.yml
find .github/workflows -maxdepth 1 -type f -printf '%f\n' | sort

# must print nothing
ls pi openclaw hermes mcp_host 2>/dev/null || true
test ! -e tools/tool_schemas.json
test ! -e scripts/tool-calls.mjs
grep -RIn --exclude-dir=.git --exclude-dir=node_modules \
  --exclude-dir=.venv -E 'tool_schemas|tool-calls|openclaw|hermes/|mcp_host' \
  dsh tests tools scripts | head
```

Verify the dsh package staging/tarball includes the Python payload and built UI
before merging to `custom`/`main`:

```bash
tmp=$(mktemp -d)
cp -R dsh "$tmp/dsh"
for d in tools skills schemas templates strategies scripts; do
  rm -rf "$tmp/dsh/$d"
  cp -R "$d" "$tmp/dsh/$d"
done
rm -f "$tmp/dsh/scripts/sync-version.sh"
cp LICENSE "$tmp/dsh/LICENSE"
(cd "$tmp/dsh" && npm pack)
tar -tzf "$tmp/dsh"/*.tgz | grep -E \
  'package/(dist/index.js|dist/client.js|dist/web/index.html|scripts/setup-python.mjs|tools/stock_data.py)'
rm -rf "$tmp"
```

Only after these pass:

```bash
git switch custom
git merge --ff-only merge/upstream-<sha>
git switch main
git merge --ff-only custom
git push origin custom main
git branch -d merge/upstream-<sha>
```

## 7. Merge review questions

Before declaring an upstream merge complete, answer yes to each:

- Does the change preserve dsh-only (no host files, tests, docs or workflows)?
- Does it preserve inline dsh tool definitions and keywords?
- Does the dashboard still show A-only breadth and 120-day/intraday charts?
- Do credentials still load from `$DSH_HOME/stock-analysis.env` in every CLI?
- Do `lean`/`full` profiles and the removed-provider policy still hold?
- Are custom tests/fixtures still present and updated for any new tool?
- Is the dsh package still the only published artifact?
- Did CI test a clean environment (no optional packages such as baostock)?
- Does `git diff` contain only intended files, not upstream host/README/UI noise?
