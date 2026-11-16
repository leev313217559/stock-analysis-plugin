// Keyword coverage audit. `--check` fails on missing breadth or duplicate entries.
import { readToolKeywords } from "./lib/tool-keywords.mjs";

const rows = readToolKeywords();
const counts = rows.map(({name, keywords}) => ({name, count: keywords.length}));
const under = counts.filter(({count}) => count < 8);
const high = new Set([
  "get_quote","get_kline","get_capital_flow","get_technical_analysis","get_news",
  "get_financials","get_announcements","screen_risk","get_limit_up_pool","get_dragon_tiger",
  "get_market_stats","get_market_review","search_stock_news","search_comprehensive_intel",
  "get_sector_rankings","get_sector_constituents","get_dividends","get_earnings_calendar",
  "get_valuation_history","get_market_indices",
]);
const highUnder = counts.filter(({name, count}) => high.has(name) && count < 12);
const duplicates = rows
  .map(({name, keywords}) => ({name, dup: keywords.filter((v, i) => keywords.findIndex(x => x.toLowerCase() === v.toLowerCase()) !== i)}))
  .filter(({dup}) => dup.length);
const shared = new Map();
for (const {name, keywords} of rows) {
  for (const keyword of keywords) {
    const key = keyword.toLowerCase();
    if (!shared.has(key)) shared.set(key, []);
    shared.get(key).push(name);
  }
}
const wide = [...shared].filter(([, tools]) => tools.length > 3).map(([keyword, tools]) => ({keyword, tools}));

const sorted = [...counts].sort((a, b) => a.count - b.count);
console.log(`tools: ${rows.length}`);
console.log(`min/median/max: ${sorted[0].count}/${sorted[Math.floor(sorted.length / 2)].count}/${sorted[sorted.length - 1].count}`);
console.log(`under 8: ${under.map(x => `${x.name}(${x.count})`).join(", ") || "none"}`);
console.log(`high-frequency under 12: ${highUnder.map(x => `${x.name}(${x.count})`).join(", ") || "none"}`);
console.log(`duplicates: ${duplicates.map(x => `${x.name}:${x.dup.join("/")}`).join(", ") || "none"}`);
console.log(`shared by >3 tools: ${wide.map(x => `${x.keyword}(${x.tools.length})`).join(", ") || "none"}`);

if (process.argv.includes("--check")) {
  if (under.length || highUnder.length || duplicates.length) process.exit(1);
}
