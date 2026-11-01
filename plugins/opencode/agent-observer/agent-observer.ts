import type { Plugin } from "@opencode-ai/plugin"
import { appendFile, mkdir } from "node:fs/promises"
import { join } from "node:path"

// Registro local de metadatos. Nunca guarda prompts, argumentos ni respuestas.
export const FoundryAgentObserver = (async ({ directory }) => {
  const folder = join(directory, ".opencode", ".foundry");
  const file = join(folder, "events.jsonl");
  async function record(type: string, fields: Record<string, unknown>) {
    try {
      await mkdir(folder, { recursive: true, mode: 0o700 });
      await appendFile(file, JSON.stringify({
        schema: "foundry/event/v1", at: new Date().toISOString(), type,
        ...fields,
      }) + "\n", { encoding: "utf8", mode: 0o600 });
    } catch {
      // Telemetry must not interrupt an agent. A missing log is not an approval.
    }
  }
  return {
    "tool.execute.before": async (input) => {
      const item = input as { tool?: string; sessionID?: string; callID?: string };
      await record("tool.started", {
        session_id: item.sessionID, call_id: item.callID, tool: item.tool,
      });
    },
    "tool.execute.after": async (input) => {
      const item = input as { tool?: string; sessionID?: string; callID?: string };
      await record("tool.finished", {
        session_id: item.sessionID, call_id: item.callID, tool: item.tool,
      });
    },
    event: async ({ event }) => {
      if (!["permission.asked", "permission.replied", "session.idle", "session.error"].includes(event.type)) return;
      const properties = (event as { properties?: Record<string, unknown> }).properties ?? {};
      await record(event.type, {
        session_id: typeof properties.sessionID === "string" ? properties.sessionID : undefined,
        permission_id: typeof properties.id === "string" ? properties.id : undefined,
      });
    },
  };
}) as Plugin;
