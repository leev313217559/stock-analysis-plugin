// Read-only inventory of inline keywords in dsh/index.ts.
// Source of truth is each tool definition; this script must not be used to edit keywords.
import { mkdirSync, writeFileSync } from "node:fs";
import { readToolKeywords } from "./lib/tool-keywords.mjs";

const rows = readToolKeywords();
if (rows.length !== 75) throw new Error(`expected 75 tools, got ${rows.length}`);

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
