#!/usr/bin/env node
/**
 * Real-host smoke QA for the dsh plugin: install the packed bundle into a
 * disposable dsh profile and run one QA turn through the host's agent loop.
 *
 * Usage: node tests/e2e/host_smoke.mjs dsh
 *
 * Env:
 *   OPENAI_BASE_URL, OPENAI_API_KEY, OPENAI_MODEL  (required)
 *   SMOKE_WORKDIR                                  (optional scratch dir)
 */
import { execFileSync } from "node:child_process";
import { existsSync, mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..", "..");
const host = process.argv[2];
if (host !== "dsh") {
  console.error("usage: host_smoke.mjs dsh");
  process.exit(2);
}

const API_KEY = process.env.OPENAI_API_KEY || "";
const BASE_URL = process.env.OPENAI_BASE_URL || "";
const MODEL = process.env.OPENAI_MODEL || "";
if (!API_KEY || !BASE_URL || !MODEL) {
  console.error("OPENAI_BASE_URL, OPENAI_API_KEY, and OPENAI_MODEL are required");
  process.exit(2);
}

const WORK = process.env.SMOKE_WORKDIR || mkdtempSync(join(tmpdir(), "dsh-host-smoke-"));
const QUESTION = "Use the get_quote tool to check AAPL's latest price. Reply with only the price number.";
const MAX_ATTEMPTS = 2;

function sh(cmd, args, opts = {}) {
  console.log(`+ ${cmd} (${args.length} args)`);
  return execFileSync(cmd, args, {
    maxBuffer: 64 * 1024 * 1024,
    stdio: ["ignore", "pipe", "pipe"],
    ...opts,
  }).toString();
}

function assertCond(cond, msg) {
  if (!cond) throw new Error(`assert failed: ${msg}`);
}

function retryQA(label, run) {
  let tail = "";
  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
    const result = run(attempt);
    tail = result.tail;
    console.log(`attempt ${attempt}: ${result.log}`);
    if (result.ok) return;
  }
  throw new Error(`${label} smoke failed; last output:\n${tail.slice(-800)}`);
}

function smokeDsh() {
  // Replicate the publish payload: stage shared dirs, build dist, pack.
  for (const d of ["tools", "skills", "schemas", "templates", "strategies", "scripts"]) {
    sh("rm", ["-rf", join(repoRoot, "dsh", d)]);
    sh("cp", ["-R", join(repoRoot, d), join(repoRoot, "dsh", d)]);
  }
  sh("npm", ["run", "build:dsh"], { cwd: repoRoot });
  const packOut = sh("npm", ["pack"], { cwd: join(repoRoot, "dsh") });
  const tgz = join(repoRoot, "dsh", packOut.trim().split("\n").pop());
  const pkgName = JSON.parse(readFileSync(join(repoRoot, "dsh/package.json"), "utf8")).name;

  const dshHome = join(WORK, "dsh-home");
  const env = { ...process.env, DSH_HOME: dshHome };
  const dsh = (args, opts = {}) => sh("dsh", args, { env, ...opts });

  dsh(["plugin", "--profile", "headless", "add", tgz]);
  const pkgDir = join(dshHome, "profiles", "headless", "node_modules", ...pkgName.split("/"));
  assertCond(existsSync(join(pkgDir, "dist", "index.js")), "installed plugin has dist/index.js");
  assertCond(existsSync(join(pkgDir, "tools", "stock_data.py")), "installed plugin has tools/");

  // pnpm skips dependency lifecycle scripts; set up Python the documented way.
  sh("node", [join(pkgDir, "scripts", "setup-python.mjs")], { cwd: pkgDir, env });

  const calledToolsLog = join(WORK, "dsh-called-tools.log");
  const spyPlugin = join(repoRoot, "tests", "e2e", "dsh_tool_spy.mjs");
  const overlay =
    `- insert:\n` +
    `    - id: smoke-tool-spy\n` +
    `      name: "${spyPlugin}"\n` +
    `      config:\n` +
    `        logFile: "${calledToolsLog}"\n` +
    `- id: tool-web\n` +
    `  disabled: true\n` +
    `- id: llm-pi-ai\n` +
    `  config:\n` +
    `    providers:\n` +
    `      smokellm:\n` +
    `        apiKeyEnv: OPENAI_API_KEY\n` +
    `        api: openai-completions\n` +
    `        baseURL: ${JSON.stringify(BASE_URL)}\n` +
    `        models:\n` +
    `          - id: ${JSON.stringify(MODEL)}\n` +
    `- id: agent-default-model\n` +
    `  config:\n` +
    `    provider: smokellm\n` +
    `    model: ${JSON.stringify(MODEL)}\n`;
  const overlayPath = join(WORK, "dsh-smoke-overlay.yml");
  writeFileSync(overlayPath, overlay);
  const bootArgs = ["--profile", "headless", "--patch", overlayPath];

  retryQA("dsh", () => {
    let out = "";
    try {
      out = dsh([...bootArgs, QUESTION], { timeout: 480_000 });
    } catch (err) {
      const tail = String(err.stdout ?? "") + String(err.stderr ?? "");
      return { ok: false, log: `exit=${err.status ?? "?"}`, tail: tail.slice(-800) };
    }
    const calledTools = existsSync(calledToolsLog) ? readFileSync(calledToolsLog, "utf8") : "";
    const calledGetQuote = calledTools.split("\n").includes("get_quote");
    return {
      ok: calledGetQuote && /\d/.test(out),
      log: `toolCalled=${calledGetQuote} tools=[${calledTools.trim().replaceAll("\n", ",")}] final=${out.trim().slice(0, 80)}`,
      tail: out,
    };
  });
}

try {
  smokeDsh();
  console.log("\nOK: dsh real-host smoke passed");
} catch (err) {
  console.error(`\nFAIL: dsh real-host smoke: ${err.message}`);
  process.exit(1);
}
