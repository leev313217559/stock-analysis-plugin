// One root for plugin-owned files: $DSH_HOME (fallback ~/.dsh).
// Config: $DSH_HOME/stock-analysis.env; state: $DSH_HOME/stock-analysis/.
import { homedir } from "node:os";
import { join } from "node:path";

export function dshHome(): string {
  return process.env.DSH_HOME || join(homedir(), ".dsh");
}

export function dataDir(): string {
  return join(dshHome(), "stock-analysis");
}

export function configFile(): string {
  return process.env.STOCK_ANALYSIS_ENV_FILE || join(dshHome(), "stock-analysis.env");
}

export function watchlistFile(): string {
  return process.env.STOCK_WATCHLIST_FILE || join(dataDir(), "watchlist.json");
}
