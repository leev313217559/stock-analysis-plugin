import assert from "node:assert/strict";
import { Context } from "@deepseek-ai/cordis";
import type { Agent } from "@deepseek-ai/dsh-agent";
import SkillRegistry from "@deepseek-ai/dsh-skill";
import { createScope } from "@deepseek-ai/dsh-scope";
import SystemPrompt from "@deepseek-ai/dsh-system-prompt";
import ToolRuntime, { defineTool } from "@deepseek-ai/dsh-tools";
import * as NativeExecutor from "@deepseek-ai/dsh-tool-executor-native";
import { ToolCallId } from "@deepseek-ai/dsh-llm";
import * as stockPlugin from "../dsh/index.js";
import { CORE_TOOLS } from "../dsh/discovery.js";
import { TOOL_KEYWORDS } from "../dsh/tool-keywords.js";

const ctx = new Context();
await ctx.plugin(SystemPrompt);
await ctx.plugin(ToolRuntime);
await ctx.plugin(NativeExecutor);
await ctx.plugin(SkillRegistry);
const plugin = await ctx.plugin(stockPlugin);
try {
  ctx.tools.register(defineTool({
    name: "other_plugin", description: "Unrelated tool", parameters: {},
    output: {schema: {type: "string"}, render: (_args, value) => [{type: "text", text: value}]},
    async execute() { return "other"; },
  }));
  const first = {};
  const second = {};
  let scopeOwner = ctx;
  await ctx.plugin({name: "discovery-test-scopes", inject: ["tools"], apply(inner: Context) { scopeOwner = inner; }});
  const firstScope = createScope(scopeOwner, first);
  const secondScope = createScope(scopeOwner, second);
  const step = (scope: object) => ctx.tools.resolve({agent: scope as Agent, modelSelection: {provider: "p", model: "m"} as never, signal: new AbortController().signal});
  const names = async (scope: object) => {
    const toolSet = await step(scope);
    try { return (await ctx.systemPrompt.assemble({scope, toolSet})).tools.map(tool => tool.name); } finally { toolSet.dispose(); }
  };
  const call = async (scope: object, name: string, args: object) => {
    const toolSet = await step(scope);
    try {
      const batch = await ctx.tools.execute({calls: [{type: "tool-call", id: ToolCallId(name), name, arguments: JSON.stringify(args)}],
        agent: scope as Agent, toolSet, signal: new AbortController().signal});
      return batch.results[0].result;
    } finally { toolSet.dispose(); }
  };
  const search = async (scope: object, query: string, limit = 5) => {
    const result = await call(scope, "stock_tool_search", {query, limit});
    assert.equal(result.isError, false, JSON.stringify(result));
    return JSON.parse(String(result.value));
  };

  const initial = await names(first);
  for (const name of ["other_plugin", "stock_tool_search", ...CORE_TOOLS]) {
    assert(initial.includes(name), `core tool ${name} should be eager`);
  }
  assert(!initial.includes("get_financials"), "non-core tools stay search-gated");
  const disabledAtStartup = secondScope.ctx.tools.restrict({deny: ["stock_tool_search"]});
  assert((await names(second)).includes("get_quote"), "unavailable search at startup keeps stock tools exposed");
  disabledAtStartup();
  assert((await names(second)).includes("get_quote"), "core tools stay eager after search is re-enabled");
  const found = await search(first, "get_quote", 1);
  assert.equal(found.loaded[0].name, "get_quote");
  assert.equal((await search(first, "stock quote", 1)).loaded[0].name, "get_quote", "a general stock keyword must not bury the requested quote capability");
  assert((await search(first, "股票回测")).loaded.some((tool: {name: string}) => tool.name === "run_backtest"), "Chinese capability terms must outrank generic stock characters");
  assert.equal((await search(first, "股票回测", 1)).loaded[0].name, "run_backtest", "generic backtest query must prefer the canonical tool");
  const financialsLoaded = await search(first, "get_financials", 1);
  assert.equal(financialsLoaded.loaded[0].name, "get_financials");
  assert((await names(first)).includes("get_financials"));
  assert(!(await names(second)).includes("get_financials"), "loading must remain agent-local");

  firstScope.ctx.tools.restrict({deny: ["get_financials"]});
  const financials = await search(first, "财务");
  assert(!financials.loaded.some((tool: {name: string}) => tool.name === "get_financials"), "search cannot bypass permission restrictions");
  const chinese = await search(second, "财务");
  assert(chinese.loaded.some((tool: {name: string}) => tool.name === "get_financials"), "Chinese descriptions must be searchable");
  await search(second, "get_market_capabilities", 1);
  assert((await names(second)).includes("get_market_capabilities"));
  const capabilities = await call(second, "get_market_capabilities", {market: "HK"});
  assert.equal(capabilities.isError, false);
  assert.equal(JSON.parse(String(capabilities.value)).market, "HK", "a discovered tool must execute the real Python CLI");
  const keywordHits = [
    ["资金流", "get_capital_flow"],
    ["龙虎榜", "get_dragon_tiger"],
    ["研报", "search_comprehensive_intel"],
    ["财报", "get_financials"],
    ["13F", "get_us_holdings"],
  ] as const;
  for (const [query, tool] of keywordHits) {
    const hit = await search(second, query, 5);
    assert(hit.loaded.some((item: {name: string}) => item.name === tool), `keyword ${query} should load ${tool}`);
  }
  assert.deepEqual((await search(first, "nonexistent_zzzzz")).loaded, []);
  assert.equal(typeof (await search(first, "get_quote", 0)).error, "string");

  const blockSearch = firstScope.ctx.tools.restrict({deny: ["stock_tool_search"]});
  const fallback = await names(first);
  assert(fallback.includes("run_backtest"), "disabled search must restore the stock catalog");
  assert(!fallback.includes("get_financials"), "fallback must preserve permission restrictions");
  blockSearch();
  assert(!(await names(first)).includes("get_financials"), "re-enabled discovery starts with an empty loaded set");
  const disposePtc = ctx.on("system-prompt/assemble", async (_assembly, _context, next) => {
    const assembly = await next();
    return {...assembly, sections: [...assembly.sections, {name: "tools:sdk", order: 0, text: "sdk", interpolate: false} as never]};
  });
  await names(first); // the PTC SDK section is observed by assembly, after this step's activation
  assert((await names(first)).includes("run_backtest"), "PTC presentation keeps the host-owned catalog");
  disposePtc();
  await firstScope.dispose();
  await secondScope.dispose();
} finally {
  await plugin.dispose();
  await ctx.fiber.dispose();
}

const eager = new Context();
await eager.plugin(SystemPrompt);
await eager.plugin(ToolRuntime);
await eager.plugin(NativeExecutor);
await eager.plugin(SkillRegistry);
await eager.plugin(stockPlugin, {toolDiscovery: false});
try {
  assert.equal(eager.tools.schemas().length, 73);
  assert.equal(eager.tools.get("stock_tool_search"), undefined);
  assert.equal((await eager.systemPrompt.assemble({scope: {}})).tools.length, 73);
  const eagerNames = eager.tools.schemas().map(tool => tool.name).sort();
  assert.deepEqual(Object.keys(TOOL_KEYWORDS).sort(), eagerNames, "every registered tool needs one keyword entry");
  for (const [name, keywords] of Object.entries(TOOL_KEYWORDS)) {
    assert(keywords.length >= 3, `${name} needs at least 3 keywords`);
    assert.equal(new Set(keywords).size, keywords.length, `${name} has duplicate keywords`);
  }
} finally { await eager.fiber.dispose(); }
console.log("dsh discovery: scoped loading, Chinese search, permissions, fallback, and real Python round-trip passed");
