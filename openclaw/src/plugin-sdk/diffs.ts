// Narrow plugin-sdk surface for the bundled diffs plugin.
// Keep this list additive and scoped to symbols used under extensions/diffs.

export type { ChappieConfig } from "../config/config.js";
export { resolvePreferredChappieTmpDir } from "../infra/tmp-chappie-dir.js";
export type {
  AnyAgentTool,
  ChappiePluginApi,
  ChappiePluginConfigSchema,
  PluginLogger,
} from "../plugins/types.js";
