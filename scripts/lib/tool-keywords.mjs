// Parse inline keyword arrays from dsh/index.ts. Read-only helper for docs/audit.
import { readFileSync } from "node:fs";

export function readToolKeywords() {
  const src = readFileSync("dsh/index.ts", "utf8");
  const names = [...src.matchAll(/name:\s*"([a-z0-9_]+)"/g)].map(m => ({name: m[1], index: m.index}));
  const arrays = [...src.matchAll(/keywords:\s*(\[[\s\S]*?\])/g)].map(m => ({values: m[1], index: m.index}));
  const rows = [];
  for (let i = 0; i < names.length; i++) {
    const start = names[i].index;
    const end = names[i + 1]?.index ?? src.length;
    let found = arrays.find(item => item.index > start && item.index < end);
    if (!found) {
      // Render tools pass keywords as the second argument of keyworded(defineTool(...), [...]).
      const wrapped = src.slice(start, end).match(/\}\),\s*(\[[\s\S]*?\])\s*\)/);
      if (wrapped) found = {values: wrapped[1], index: start + wrapped.index};
    }
    if (!found) throw new Error(`missing keywords for ${names[i].name}`);
    rows.push({name: names[i].name, keywords: JSON.parse(found.values)});
  }
  return rows.sort((a, b) => a.name.localeCompare(b.name));
}
