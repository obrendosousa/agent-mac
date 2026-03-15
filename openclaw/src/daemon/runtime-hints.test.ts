import { describe, expect, it } from "vitest";
import { buildPlatformRuntimeLogHints, buildPlatformServiceStartHints } from "./runtime-hints.js";

describe("buildPlatformRuntimeLogHints", () => {
  it("renders launchd log hints on darwin", () => {
    expect(
      buildPlatformRuntimeLogHints({
        platform: "darwin",
        env: {
          CHAPPIE_STATE_DIR: "/tmp/chappie-state",
          CHAPPIE_LOG_PREFIX: "gateway",
        },
        systemdServiceName: "chappie-gateway",
        windowsTaskName: "Chappie Gateway",
      }),
    ).toEqual([
      "Launchd stdout (if installed): /tmp/chappie-state/logs/gateway.log",
      "Launchd stderr (if installed): /tmp/chappie-state/logs/gateway.err.log",
    ]);
  });

  it("renders systemd and windows hints by platform", () => {
    expect(
      buildPlatformRuntimeLogHints({
        platform: "linux",
        systemdServiceName: "chappie-gateway",
        windowsTaskName: "Chappie Gateway",
      }),
    ).toEqual(["Logs: journalctl --user -u chappie-gateway.service -n 200 --no-pager"]);
    expect(
      buildPlatformRuntimeLogHints({
        platform: "win32",
        systemdServiceName: "chappie-gateway",
        windowsTaskName: "Chappie Gateway",
      }),
    ).toEqual(['Logs: schtasks /Query /TN "Chappie Gateway" /V /FO LIST']);
  });
});

describe("buildPlatformServiceStartHints", () => {
  it("builds platform-specific service start hints", () => {
    expect(
      buildPlatformServiceStartHints({
        platform: "darwin",
        installCommand: "chappie gateway install",
        startCommand: "chappie gateway",
        launchAgentPlistPath: "~/Library/LaunchAgents/com.chappie.gateway.plist",
        systemdServiceName: "chappie-gateway",
        windowsTaskName: "Chappie Gateway",
      }),
    ).toEqual([
      "chappie gateway install",
      "chappie gateway",
      "launchctl bootstrap gui/$UID ~/Library/LaunchAgents/com.chappie.gateway.plist",
    ]);
    expect(
      buildPlatformServiceStartHints({
        platform: "linux",
        installCommand: "chappie gateway install",
        startCommand: "chappie gateway",
        launchAgentPlistPath: "~/Library/LaunchAgents/com.chappie.gateway.plist",
        systemdServiceName: "chappie-gateway",
        windowsTaskName: "Chappie Gateway",
      }),
    ).toEqual([
      "chappie gateway install",
      "chappie gateway",
      "systemctl --user start chappie-gateway.service",
    ]);
  });
});
