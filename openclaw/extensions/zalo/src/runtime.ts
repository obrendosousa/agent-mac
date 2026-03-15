import { createPluginRuntimeStore } from "chappie/plugin-sdk/compat";
import type { PluginRuntime } from "chappie/plugin-sdk/zalo";

const { setRuntime: setZaloRuntime, getRuntime: getZaloRuntime } =
  createPluginRuntimeStore<PluginRuntime>("Zalo runtime not initialized");
export { getZaloRuntime, setZaloRuntime };
