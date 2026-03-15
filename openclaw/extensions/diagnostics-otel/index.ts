import type { ChappiePluginApi } from "chappie/plugin-sdk/diagnostics-otel";
import { emptyPluginConfigSchema } from "chappie/plugin-sdk/diagnostics-otel";
import { createDiagnosticsOtelService } from "./src/service.js";

const plugin = {
  id: "diagnostics-otel",
  name: "Diagnostics OpenTelemetry",
  description: "Export diagnostics events to OpenTelemetry",
  configSchema: emptyPluginConfigSchema(),
  register(api: ChappiePluginApi) {
    api.registerService(createDiagnosticsOtelService());
  },
};

export default plugin;
