import type { ChappieConfig } from "./config.js";

export function ensurePluginAllowlisted(cfg: ChappieConfig, pluginId: string): ChappieConfig {
  const allow = cfg.plugins?.allow;
  if (!Array.isArray(allow) || allow.includes(pluginId)) {
    return cfg;
  }
  return {
    ...cfg,
    plugins: {
      ...cfg.plugins,
      allow: [...allow, pluginId],
    },
  };
}
