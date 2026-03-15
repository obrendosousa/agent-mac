import type { ChappieConfig } from "../../config/config.js";

export function makeModelFallbackCfg(overrides: Partial<ChappieConfig> = {}): ChappieConfig {
  return {
    agents: {
      defaults: {
        model: {
          primary: "openai/gpt-4.1-mini",
          fallbacks: ["anthropic/claude-haiku-3-5"],
        },
      },
    },
    ...overrides,
  } as ChappieConfig;
}
