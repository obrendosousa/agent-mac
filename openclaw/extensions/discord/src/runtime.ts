import { createPluginRuntimeStore } from "chappie/plugin-sdk/compat";
import type { PluginRuntime } from "chappie/plugin-sdk/discord";

const { setRuntime: setDiscordRuntime, getRuntime: getDiscordRuntime } =
  createPluginRuntimeStore<PluginRuntime>("Discord runtime not initialized");
export { getDiscordRuntime, setDiscordRuntime };
