import { createPluginRuntimeStore } from "chappie/plugin-sdk/compat";
import type { PluginRuntime } from "chappie/plugin-sdk/line";

const { setRuntime: setLineRuntime, getRuntime: getLineRuntime } =
  createPluginRuntimeStore<PluginRuntime>("LINE runtime not initialized - plugin not registered");
export { getLineRuntime, setLineRuntime };
