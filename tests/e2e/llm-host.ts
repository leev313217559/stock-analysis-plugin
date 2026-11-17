import { fileURLToPath } from "node:url";
import { createJiti } from "jiti";

interface ToolResult {
  content: { type: string; text: string }[];
  details?: unknown;
}

export interface RegisteredTool {
  name: string;
  description: string;
  parameters: Record<string, unknown>;
  execute: (id: string, args: Record<string, unknown>) => Promise<ToolResult>;
}

export async function timedStage<T>(stage: string, operation: () => Promise<T>): Promise<T> {
  const started = performance.now();
  try {
    return await operation();
  } finally {
    console.error(`[timing] ${stage} seconds=${((performance.now() - started) / 1000).toFixed(3)} pid=${process.pid}`);
  }
}

export async function loadLLMHost(host: string): Promise<RegisteredTool[]> {
  if (host !== "dsh") throw new Error("Expected dsh");
  type DshTool = Omit<RegisteredTool, "execute"> & {
    execute: (args: Record<string, unknown>, context: unknown) => Promise<string>;
    output: { render: (args: Record<string, unknown>, value: string) => ToolResult["content"] };
  };
  const tools: RegisteredTool[] = [];
  const jiti = createJiti(fileURLToPath(import.meta.url));
  const plugin = await jiti.import("../../dsh/index.ts") as { apply: (ctx: unknown) => void };
  plugin.apply({
    tools: {
      register(tool: DshTool) {
        tools.push({
          name: tool.name, description: tool.description, parameters: tool.parameters,
          async execute(_id, args) {
            const value = await tool.execute(args, {});
            return { content: tool.output.render(args, value) };
          },
        });
      },
    },
    skills: { register() {} },
  });
  return tools;
}
