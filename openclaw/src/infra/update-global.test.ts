import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { captureEnv } from "../test-utils/env.js";
import {
  cleanupGlobalRenameDirs,
  detectGlobalInstallManagerByPresence,
  detectGlobalInstallManagerForRoot,
  globalInstallArgs,
  globalInstallFallbackArgs,
  resolveGlobalPackageRoot,
  resolveGlobalInstallSpec,
  resolveGlobalRoot,
  type CommandRunner,
} from "./update-global.js";

describe("update global helpers", () => {
  let envSnapshot: ReturnType<typeof captureEnv> | undefined;

  afterEach(() => {
    envSnapshot?.restore();
    envSnapshot = undefined;
  });

  it("prefers explicit package spec overrides", () => {
    envSnapshot = captureEnv(["CHAPPIE_UPDATE_PACKAGE_SPEC"]);
    process.env.CHAPPIE_UPDATE_PACKAGE_SPEC = "file:/tmp/chappie.tgz";

    expect(resolveGlobalInstallSpec({ packageName: "chappie", tag: "latest" })).toBe(
      "file:/tmp/chappie.tgz",
    );
    expect(
      resolveGlobalInstallSpec({
        packageName: "chappie",
        tag: "beta",
        env: { CHAPPIE_UPDATE_PACKAGE_SPEC: "chappie@next" },
      }),
    ).toBe("chappie@next");
  });

  it("resolves global roots and package roots from runner output", async () => {
    const runCommand: CommandRunner = async (argv) => {
      if (argv[0] === "npm") {
        return { stdout: "/tmp/npm-root\n", stderr: "", code: 0 };
      }
      if (argv[0] === "pnpm") {
        return { stdout: "", stderr: "", code: 1 };
      }
      throw new Error(`unexpected command: ${argv.join(" ")}`);
    };

    await expect(resolveGlobalRoot("npm", runCommand, 1000)).resolves.toBe("/tmp/npm-root");
    await expect(resolveGlobalRoot("pnpm", runCommand, 1000)).resolves.toBeNull();
    await expect(resolveGlobalRoot("bun", runCommand, 1000)).resolves.toContain(
      path.join(".bun", "install", "global", "node_modules"),
    );
    await expect(resolveGlobalPackageRoot("npm", runCommand, 1000)).resolves.toBe(
      path.join("/tmp/npm-root", "chappie"),
    );
  });

  it("detects install managers from resolved roots and on-disk presence", async () => {
    const base = await fs.mkdtemp(path.join(os.tmpdir(), "chappie-update-global-"));
    const npmRoot = path.join(base, "npm-root");
    const pnpmRoot = path.join(base, "pnpm-root");
    const bunRoot = path.join(base, ".bun", "install", "global", "node_modules");
    const pkgRoot = path.join(pnpmRoot, "chappie");
    await fs.mkdir(pkgRoot, { recursive: true });
    await fs.mkdir(path.join(npmRoot, "chappie"), { recursive: true });
    await fs.mkdir(path.join(bunRoot, "chappie"), { recursive: true });

    envSnapshot = captureEnv(["BUN_INSTALL"]);
    process.env.BUN_INSTALL = path.join(base, ".bun");

    const runCommand: CommandRunner = async (argv) => {
      if (argv[0] === "npm") {
        return { stdout: `${npmRoot}\n`, stderr: "", code: 0 };
      }
      if (argv[0] === "pnpm") {
        return { stdout: `${pnpmRoot}\n`, stderr: "", code: 0 };
      }
      throw new Error(`unexpected command: ${argv.join(" ")}`);
    };

    await expect(detectGlobalInstallManagerForRoot(runCommand, pkgRoot, 1000)).resolves.toBe(
      "pnpm",
    );
    await expect(detectGlobalInstallManagerByPresence(runCommand, 1000)).resolves.toBe("npm");

    await fs.rm(path.join(npmRoot, "chappie"), { recursive: true, force: true });
    await fs.rm(path.join(pnpmRoot, "chappie"), { recursive: true, force: true });
    await expect(detectGlobalInstallManagerByPresence(runCommand, 1000)).resolves.toBe("bun");
  });

  it("builds install argv and npm fallback argv", () => {
    expect(globalInstallArgs("npm", "chappie@latest")).toEqual([
      "npm",
      "i",
      "-g",
      "chappie@latest",
      "--no-fund",
      "--no-audit",
      "--loglevel=error",
    ]);
    expect(globalInstallArgs("pnpm", "chappie@latest")).toEqual([
      "pnpm",
      "add",
      "-g",
      "chappie@latest",
    ]);
    expect(globalInstallArgs("bun", "chappie@latest")).toEqual([
      "bun",
      "add",
      "-g",
      "chappie@latest",
    ]);

    expect(globalInstallFallbackArgs("npm", "chappie@latest")).toEqual([
      "npm",
      "i",
      "-g",
      "chappie@latest",
      "--omit=optional",
      "--no-fund",
      "--no-audit",
      "--loglevel=error",
    ]);
    expect(globalInstallFallbackArgs("pnpm", "chappie@latest")).toBeNull();
  });

  it("cleans only renamed package directories", async () => {
    const root = await fs.mkdtemp(path.join(os.tmpdir(), "chappie-update-cleanup-"));
    await fs.mkdir(path.join(root, ".chappie-123"), { recursive: true });
    await fs.mkdir(path.join(root, ".chappie-456"), { recursive: true });
    await fs.writeFile(path.join(root, ".chappie-file"), "nope", "utf8");
    await fs.mkdir(path.join(root, "chappie"), { recursive: true });

    await expect(
      cleanupGlobalRenameDirs({
        globalRoot: root,
        packageName: "chappie",
      }),
    ).resolves.toEqual({
      removed: [".chappie-123", ".chappie-456"],
    });
    await expect(fs.stat(path.join(root, "chappie"))).resolves.toBeDefined();
    await expect(fs.stat(path.join(root, ".chappie-file"))).resolves.toBeDefined();
  });
});
