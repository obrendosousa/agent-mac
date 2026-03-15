import { execFileSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, describe, expect, it } from "vitest";

function withFakeCli(versionOutput: string): { root: string; cliPath: string } {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "chappie-install-sh-"));
  const cliPath = path.join(root, "chappie");
  const escapedOutput = versionOutput.replace(/'/g, "'\\''");
  fs.writeFileSync(
    cliPath,
    `#!/usr/bin/env bash
printf '%s\n' '${escapedOutput}'
`,
    "utf-8",
  );
  fs.chmodSync(cliPath, 0o755);
  return { root, cliPath };
}

function resolveVersionFromInstaller(cliPath: string): string {
  const installerPath = path.join(process.cwd(), "scripts", "install.sh");
  const output = execFileSync(
    "bash",
    [
      "-lc",
      `source "${installerPath}" >/dev/null 2>&1
CHAPPIE_BIN="$FAKE_CHAPPIE_BIN"
resolve_chappie_version`,
    ],
    {
      cwd: process.cwd(),
      encoding: "utf-8",
      env: {
        ...process.env,
        FAKE_CHAPPIE_BIN: cliPath,
        CHAPPIE_INSTALL_SH_NO_RUN: "1",
      },
    },
  );
  return output.trim();
}

function resolveVersionFromInstallerViaStdin(cliPath: string, cwd: string): string {
  const installerPath = path.join(process.cwd(), "scripts", "install.sh");
  const installerSource = fs.readFileSync(installerPath, "utf-8");
  const output = execFileSync("bash", [], {
    cwd,
    encoding: "utf-8",
    input: `${installerSource}
CHAPPIE_BIN="$FAKE_CHAPPIE_BIN"
resolve_chappie_version
`,
    env: {
      ...process.env,
      FAKE_CHAPPIE_BIN: cliPath,
      CHAPPIE_INSTALL_SH_NO_RUN: "1",
    },
  });
  return output.trim();
}

describe("install.sh version resolution", () => {
  const tempRoots: string[] = [];

  afterEach(() => {
    for (const root of tempRoots.splice(0)) {
      fs.rmSync(root, { recursive: true, force: true });
    }
  });

  it.runIf(process.platform !== "win32")(
    "extracts the semantic version from decorated CLI output",
    () => {
      const fixture = withFakeCli("Chappie 2026.3.10 (abcdef0)");
      tempRoots.push(fixture.root);

      expect(resolveVersionFromInstaller(fixture.cliPath)).toBe("2026.3.10");
    },
  );

  it.runIf(process.platform !== "win32")(
    "falls back to raw output when no semantic version is present",
    () => {
      const fixture = withFakeCli("Chappie dev's build");
      tempRoots.push(fixture.root);

      expect(resolveVersionFromInstaller(fixture.cliPath)).toBe("Chappie dev's build");
    },
  );

  it.runIf(process.platform !== "win32")(
    "does not source version helpers from cwd when installer runs via stdin",
    () => {
      const fixture = withFakeCli("Chappie 2026.3.10 (abcdef0)");
      tempRoots.push(fixture.root);

      const hostileCwd = fs.mkdtempSync(path.join(os.tmpdir(), "chappie-install-stdin-"));
      tempRoots.push(hostileCwd);
      const hostileHelper = path.join(
        hostileCwd,
        "docker",
        "install-sh-common",
        "version-parse.sh",
      );
      fs.mkdirSync(path.dirname(hostileHelper), { recursive: true });
      fs.writeFileSync(
        hostileHelper,
        `#!/usr/bin/env bash
extract_chappie_semver() {
  printf '%s' 'poisoned'
}
`,
        "utf-8",
      );

      expect(resolveVersionFromInstallerViaStdin(fixture.cliPath, hostileCwd)).toBe("2026.3.10");
    },
  );
});
