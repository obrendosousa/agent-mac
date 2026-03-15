import type { ChappiePluginApi } from "chappie/plugin-sdk/synology-chat";
import { emptyPluginConfigSchema } from "chappie/plugin-sdk/synology-chat";
import { createSynologyChatPlugin } from "./src/channel.js";
import { setSynologyRuntime } from "./src/runtime.js";

const plugin = {
  id: "synology-chat",
  name: "Synology Chat",
  description: "Native Synology Chat channel plugin for Chappie",
  configSchema: emptyPluginConfigSchema(),
  register(api: ChappiePluginApi) {
    setSynologyRuntime(api.runtime);
    api.registerChannel({ plugin: createSynologyChatPlugin() });
  },
};

export default plugin;
