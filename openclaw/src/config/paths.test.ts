import fs from "node:fs/promises";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { withTempDir } from "../test-helpers/temp-dir.js";
import {
  resolveDefaultConfigCandidates,
  resolveConfigPathCandidate,
  resolveConfigPath,
  resolveOAuthDir,
  resolveOAuthPath,
  resolveStateDir,
} from "./paths.js";

describe("oauth paths", () => {
  it("prefers CHAPPIE_OAUTH_DIR over CHAPPIE_STATE_DIR", () => {
    const env = {
      CHAPPIE_OAUTH_DIR: "/custom/oauth",
      CHAPPIE_STATE_DIR: "/custom/state",
    } as NodeJS.ProcessEnv;

    expect(resolveOAuthDir(env, "/custom/state")).toBe(path.resolve("/custom/oauth"));
    expect(resolveOAuthPath(env, "/custom/state")).toBe(
      path.join(path.resolve("/custom/oauth"), "oauth.json"),
    );
  });

  it("derives oauth path from CHAPPIE_STATE_DIR when unset", () => {
    const env = {
      CHAPPIE_STATE_DIR: "/custom/state",
    } as NodeJS.ProcessEnv;

    expect(resolveOAuthDir(env, "/custom/state")).toBe(path.join("/custom/state", "credentials"));
    expect(resolveOAuthPath(env, "/custom/state")).toBe(
      path.join("/custom/state", "credentials", "oauth.json"),
    );
  });
});

describe("state + config path candidates", () => {
  function expectChappieHomeDefaults(env: NodeJS.ProcessEnv): void {
    const configuredHome = env.CHAPPIE_HOME;
    if (!configuredHome) {
      throw new Error("CHAPPIE_HOME must be set for this assertion helper");
    }
    const resolvedHome = path.resolve(configuredHome);
    expect(resolveStateDir(env)).toBe(path.join(resolvedHome, ".chappie"));

    const candidates = resolveDefaultConfigCandidates(env);
    expect(candidates[0]).toBe(path.join(resolvedHome, ".chappie", "chappie.json"));
  }

  it("uses CHAPPIE_STATE_DIR when set", () => {
    const env = {
      CHAPPIE_STATE_DIR: "/new/state",
    } as NodeJS.ProcessEnv;

    expect(resolveStateDir(env, () => "/home/test")).toBe(path.resolve("/new/state"));
  });

  it("uses CHAPPIE_HOME for default state/config locations", () => {
    const env = {
      CHAPPIE_HOME: "/srv/chappie-home",
    } as NodeJS.ProcessEnv;
    expectChappieHomeDefaults(env);
  });

  it("prefers CHAPPIE_HOME over HOME for default state/config locations", () => {
    const env = {
      CHAPPIE_HOME: "/srv/chappie-home",
      HOME: "/home/other",
    } as NodeJS.ProcessEnv;
    expectChappieHomeDefaults(env);
  });

  it("orders default config candidates in a stable order", () => {
    const home = "/home/test";
    const resolvedHome = path.resolve(home);
    const candidates = resolveDefaultConfigCandidates({} as NodeJS.ProcessEnv, () => home);
    const expected = [
      path.join(resolvedHome, ".chappie", "chappie.json"),
      path.join(resolvedHome, ".chappie", "chappiedbot.json"),
      path.join(resolvedHome, ".chappie", "moldbot.json"),
      path.join(resolvedHome, ".chappie", "moltbot.json"),
      path.join(resolvedHome, ".chappiedbot", "chappie.json"),
      path.join(resolvedHome, ".chappiedbot", "chappiedbot.json"),
      path.join(resolvedHome, ".chappiedbot", "moldbot.json"),
      path.join(resolvedHome, ".chappiedbot", "moltbot.json"),
      path.join(resolvedHome, ".moldbot", "chappie.json"),
      path.join(resolvedHome, ".moldbot", "chappiedbot.json"),
      path.join(resolvedHome, ".moldbot", "moldbot.json"),
      path.join(resolvedHome, ".moldbot", "moltbot.json"),
      path.join(resolvedHome, ".moltbot", "chappie.json"),
      path.join(resolvedHome, ".moltbot", "chappiedbot.json"),
      path.join(resolvedHome, ".moltbot", "moldbot.json"),
      path.join(resolvedHome, ".moltbot", "moltbot.json"),
    ];
    expect(candidates).toEqual(expected);
  });

  it("prefers ~/.chappie when it exists and legacy dir is missing", async () => {
    await withTempDir({ prefix: "chappie-state-" }, async (root) => {
      const newDir = path.join(root, ".chappie");
      await fs.mkdir(newDir, { recursive: true });
      const resolved = resolveStateDir({} as NodeJS.ProcessEnv, () => root);
      expect(resolved).toBe(newDir);
    });
  });

  it("falls back to existing legacy state dir when ~/.chappie is missing", async () => {
    await withTempDir({ prefix: "chappie-state-legacy-" }, async (root) => {
      const legacyDir = path.join(root, ".chappiedbot");
      await fs.mkdir(legacyDir, { recursive: true });
      const resolved = resolveStateDir({} as NodeJS.ProcessEnv, () => root);
      expect(resolved).toBe(legacyDir);
    });
  });

  it("CONFIG_PATH prefers existing config when present", async () => {
    await withTempDir({ prefix: "chappie-config-" }, async (root) => {
      const legacyDir = path.join(root, ".chappie");
      await fs.mkdir(legacyDir, { recursive: true });
      const legacyPath = path.join(legacyDir, "chappie.json");
      await fs.writeFile(legacyPath, "{}", "utf-8");

      const resolved = resolveConfigPathCandidate({} as NodeJS.ProcessEnv, () => root);
      expect(resolved).toBe(legacyPath);
    });
  });

  it("respects state dir overrides when config is missing", async () => {
    await withTempDir({ prefix: "chappie-config-override-" }, async (root) => {
      const legacyDir = path.join(root, ".chappie");
      await fs.mkdir(legacyDir, { recursive: true });
      const legacyConfig = path.join(legacyDir, "chappie.json");
      await fs.writeFile(legacyConfig, "{}", "utf-8");

      const overrideDir = path.join(root, "override");
      const env = { CHAPPIE_STATE_DIR: overrideDir } as NodeJS.ProcessEnv;
      const resolved = resolveConfigPath(env, overrideDir, () => root);
      expect(resolved).toBe(path.join(overrideDir, "chappie.json"));
    });
  });
});
