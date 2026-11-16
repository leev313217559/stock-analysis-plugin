// Read-only inventory of inline keywords in dsh/index.ts.
// Source of truth is each tool definition; this script must not be used to edit keywords.
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";

const src = readFileSync("dsh/index.ts", "utf8");
const names = [...src.matchAll(/name:\s*"([a-z0-9_]+)"/g)].map(m => ({name: m[1], index: m.index}));
const keywordArrays = [...src.matchAll(/keywords:\s*(\[[\s\S]*?\])/g)].map(m => ({values: m[1], index: m.index}));

const rows = [];
for (let i = 0; i < names.length; i++) {
  const start = names[i].index;
  const end = names[i + 1]?.index ?? src.length;
  let found = keywordArrays.find(item => item.index > start && item.index < end);
  if (!found) {
    // Render tools pass keywords as the second argument of keyworded(defineTool(...), [...]).
    const wrapped = src.slice(start, end).match(/\}\),\s*(\[[\s\S]*?\])\s*\)/);
    if (wrapped) found = {values: wrapped[1], index: start + wrapped.index};
  }
  if (!found) throw new Error(`missing keywords for ${names[i].name}`);
  rows.push({name: names[i].name, keywords: JSON.parse(found.values)});
}
if (rows.length !== 73) throw new Error(`expected 73 tools, got ${rows.length}`);
rows.sort((a, b) => a.name.localeCompare(b.name));

const lines = [
  "# 工具关键词清单（生成文件）",
  "",
  "> 此文件由 `node scripts/export-tool-keywords.mjs` 从 `dsh/index.ts` 生成，**不是源数据**。",
  "> 关键词的唯一维护点是每个工具定义中的 `keywords` 字段；不要直接编辑本文件。",
  "",
  `共 ${rows.length} 个工具。`,
  "",
  "| 工具 | 关键词 |",
  "|---|---|",
  ...rows.map(({name, keywords}) => `| \`${name}\` | ${keywords.join("、")} |`),
  "",
];
mkdirSync("docs", {recursive: true});
writeFileSync("docs/tool-keywords.md", lines.join("\n"), "utf8");
console.log(`wrote docs/tool-keywords.md (${rows.length} tools)`);
