import path from "node:path";
import { describe, expect, it } from "vitest";
import { formatCliCommand } from "./command-format.js";
import { applyCliProfileEnv, parseCliProfileArgs } from "./profile.js";

describe("parseCliProfileArgs", () => {
  it("leaves gateway --dev for subcommands", () => {
    const res = parseCliProfileArgs([
      "node",
      "chappie",
      "gateway",
      "--dev",
      "--allow-unconfigured",
    ]);
    if (!res.ok) {
      throw new Error(res.error);
    }
    expect(res.profile).toBeNull();
    expect(res.argv).toEqual(["node", "chappie", "gateway", "--dev", "--allow-unconfigured"]);
  });

  it("still accepts global --dev before subcommand", () => {
    const res = parseCliProfileArgs(["node", "chappie", "--dev", "gateway"]);
    if (!res.ok) {
      throw new Error(res.error);
    }
    expect(res.profile).toBe("dev");
    expect(res.argv).toEqual(["node", "chappie", "gateway"]);
  });

  it("parses --profile value and strips it", () => {
    const res = parseCliProfileArgs(["node", "chappie", "--profile", "work", "status"]);
    if (!res.ok) {
      throw new Error(res.error);
    }
    expect(res.profile).toBe("work");
    expect(res.argv).toEqual(["node", "chappie", "status"]);
  });

  it("rejects missing profile value", () => {
    const res = parseCliProfileArgs(["node", "chappie", "--profile"]);
    expect(res.ok).toBe(false);
  });

  it.each([
    ["--dev first", ["node", "chappie", "--dev", "--profile", "work", "status"]],
    ["--profile first", ["node", "chappie", "--profile", "work", "--dev", "status"]],
  ])("rejects combining --dev with --profile (%s)", (_name, argv) => {
    const res = parseCliProfileArgs(argv);
    expect(res.ok).toBe(false);
  });
});

describe("applyCliProfileEnv", () => {
  it("fills env defaults for dev profile", () => {
    const env: Record<string, string | undefined> = {};
    applyCliProfileEnv({
      profile: "dev",
      env,
      homedir: () => "/home/peter",
    });
    const expectedStateDir = path.join(path.resolve("/home/peter"), ".chappie-dev");
    expect(env.CHAPPIE_PROFILE).toBe("dev");
    expect(env.CHAPPIE_STATE_DIR).toBe(expectedStateDir);
    expect(env.CHAPPIE_CONFIG_PATH).toBe(path.join(expectedStateDir, "chappie.json"));
    expect(env.CHAPPIE_GATEWAY_PORT).toBe("19001");
  });

  it("does not override explicit env values", () => {
    const env: Record<string, string | undefined> = {
      CHAPPIE_STATE_DIR: "/custom",
      CHAPPIE_GATEWAY_PORT: "19099",
    };
    applyCliProfileEnv({
      profile: "dev",
      env,
      homedir: () => "/home/peter",
    });
    expect(env.CHAPPIE_STATE_DIR).toBe("/custom");
    expect(env.CHAPPIE_GATEWAY_PORT).toBe("19099");
    expect(env.CHAPPIE_CONFIG_PATH).toBe(path.join("/custom", "chappie.json"));
  });

  it("uses CHAPPIE_HOME when deriving profile state dir", () => {
    const env: Record<string, string | undefined> = {
      CHAPPIE_HOME: "/srv/chappie-home",
      HOME: "/home/other",
    };
    applyCliProfileEnv({
      profile: "work",
      env,
      homedir: () => "/home/fallback",
    });

    const resolvedHome = path.resolve("/srv/chappie-home");
    expect(env.CHAPPIE_STATE_DIR).toBe(path.join(resolvedHome, ".chappie-work"));
    expect(env.CHAPPIE_CONFIG_PATH).toBe(
      path.join(resolvedHome, ".chappie-work", "chappie.json"),
    );
  });
});

describe("formatCliCommand", () => {
  it.each([
    {
      name: "no profile is set",
      cmd: "chappie doctor --fix",
      env: {},
      expected: "chappie doctor --fix",
    },
    {
      name: "profile is default",
      cmd: "chappie doctor --fix",
      env: { CHAPPIE_PROFILE: "default" },
      expected: "chappie doctor --fix",
    },
    {
      name: "profile is Default (case-insensitive)",
      cmd: "chappie doctor --fix",
      env: { CHAPPIE_PROFILE: "Default" },
      expected: "chappie doctor --fix",
    },
    {
      name: "profile is invalid",
      cmd: "chappie doctor --fix",
      env: { CHAPPIE_PROFILE: "bad profile" },
      expected: "chappie doctor --fix",
    },
    {
      name: "--profile is already present",
      cmd: "chappie --profile work doctor --fix",
      env: { CHAPPIE_PROFILE: "work" },
      expected: "chappie --profile work doctor --fix",
    },
    {
      name: "--dev is already present",
      cmd: "chappie --dev doctor",
      env: { CHAPPIE_PROFILE: "dev" },
      expected: "chappie --dev doctor",
    },
  ])("returns command unchanged when $name", ({ cmd, env, expected }) => {
    expect(formatCliCommand(cmd, env)).toBe(expected);
  });

  it("inserts --profile flag when profile is set", () => {
    expect(formatCliCommand("chappie doctor --fix", { CHAPPIE_PROFILE: "work" })).toBe(
      "chappie --profile work doctor --fix",
    );
  });

  it("trims whitespace from profile", () => {
    expect(formatCliCommand("chappie doctor --fix", { CHAPPIE_PROFILE: "  jbchappie  " })).toBe(
      "chappie --profile jbchappie doctor --fix",
    );
  });

  it("handles command with no args after chappie", () => {
    expect(formatCliCommand("chappie", { CHAPPIE_PROFILE: "test" })).toBe(
      "chappie --profile test",
    );
  });

  it("handles pnpm wrapper", () => {
    expect(formatCliCommand("pnpm chappie doctor", { CHAPPIE_PROFILE: "work" })).toBe(
      "pnpm chappie --profile work doctor",
    );
  });
});
