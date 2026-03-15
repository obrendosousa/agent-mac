import { beforeEach, describe, expect, it, vi } from "vitest";
import { buildPluginStatusReport } from "./status.js";

const loadConfigMock = vi.fn();
const loadChappiePluginsMock = vi.fn();

vi.mock("../config/config.js", () => ({
  loadConfig: () => loadConfigMock(),
}));

vi.mock("./loader.js", () => ({
  loadChappiePlugins: (...args: unknown[]) => loadChappiePluginsMock(...args),
}));

vi.mock("../agents/agent-scope.js", () => ({
  resolveAgentWorkspaceDir: () => undefined,
  resolveDefaultAgentId: () => "default",
}));

vi.mock("../agents/workspace.js", () => ({
  resolveDefaultAgentWorkspaceDir: () => "/default-workspace",
}));

describe("buildPluginStatusReport", () => {
  beforeEach(() => {
    loadConfigMock.mockReset();
    loadChappiePluginsMock.mockReset();
    loadConfigMock.mockReturnValue({});
    loadChappiePluginsMock.mockReturnValue({
      plugins: [],
      diagnostics: [],
      channels: [],
      providers: [],
      tools: [],
      hooks: [],
      gatewayHandlers: {},
      cliRegistrars: [],
      services: [],
      commands: [],
    });
  });

  it("forwards an explicit env to plugin loading", () => {
    const env = { HOME: "/tmp/chappie-home" } as NodeJS.ProcessEnv;

    buildPluginStatusReport({
      config: {},
      workspaceDir: "/workspace",
      env,
    });

    expect(loadChappiePluginsMock).toHaveBeenCalledWith(
      expect.objectContaining({
        config: {},
        workspaceDir: "/workspace",
        env,
      }),
    );
  });
});
