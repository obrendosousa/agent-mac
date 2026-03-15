import type {
  AnyAgentTool,
  ChappiePluginApi,
  ChappiePluginToolFactory,
} from "chappie/plugin-sdk/lobster";
import { createLobsterTool } from "./src/lobster-tool.js";

export default function register(api: ChappiePluginApi) {
  api.registerTool(
    ((ctx) => {
      if (ctx.sandboxed) {
        return null;
      }
      return createLobsterTool(api) as AnyAgentTool;
    }) as ChappiePluginToolFactory,
    { optional: true },
  );
}
