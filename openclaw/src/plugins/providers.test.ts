import { beforeEach, describe, expect, it, vi } from "vitest";
import { resolvePluginProviders } from "./providers.js";

const loadChappiePluginsMock = vi.fn();

vi.mock("./loader.js", () => ({
  loadChappiePlugins: (...args: unknown[]) => loadChappiePluginsMock(...args),
}));

describe("resolvePluginProviders", () => {
  beforeEach(() => {
    loadChappiePluginsMock.mockReset();
    loadChappiePluginsMock.mockReturnValue({
      providers: [{ provider: { id: "demo-provider" } }],
    });
  });

  it("forwards an explicit env to plugin loading", () => {
    const env = { CHAPPIE_HOME: "/srv/chappie-home" } as NodeJS.ProcessEnv;

    const providers = resolvePluginProviders({
      workspaceDir: "/workspace/explicit",
      env,
    });

    expect(providers).toEqual([{ id: "demo-provider" }]);
    expect(loadChappiePluginsMock).toHaveBeenCalledWith(
      expect.objectContaining({
        workspaceDir: "/workspace/explicit",
        env,
      }),
    );
  });
});
