import { describe, expect, it } from "vitest";
import {
  ensureChappieExecMarkerOnProcess,
  markChappieExecEnv,
  CHAPPIE_CLI_ENV_VALUE,
  CHAPPIE_CLI_ENV_VAR,
} from "./chappie-exec-env.js";

describe("markChappieExecEnv", () => {
  it("returns a cloned env object with the exec marker set", () => {
    const env = { PATH: "/usr/bin", CHAPPIE_CLI: "0" };
    const marked = markChappieExecEnv(env);

    expect(marked).toEqual({
      PATH: "/usr/bin",
      CHAPPIE_CLI: CHAPPIE_CLI_ENV_VALUE,
    });
    expect(marked).not.toBe(env);
    expect(env.CHAPPIE_CLI).toBe("0");
  });
});

describe("ensureChappieExecMarkerOnProcess", () => {
  it("mutates and returns the provided process env", () => {
    const env: NodeJS.ProcessEnv = { PATH: "/usr/bin" };

    expect(ensureChappieExecMarkerOnProcess(env)).toBe(env);
    expect(env[CHAPPIE_CLI_ENV_VAR]).toBe(CHAPPIE_CLI_ENV_VALUE);
  });

  it("defaults to mutating process.env when no env object is provided", () => {
    const previous = process.env[CHAPPIE_CLI_ENV_VAR];
    delete process.env[CHAPPIE_CLI_ENV_VAR];

    try {
      expect(ensureChappieExecMarkerOnProcess()).toBe(process.env);
      expect(process.env[CHAPPIE_CLI_ENV_VAR]).toBe(CHAPPIE_CLI_ENV_VALUE);
    } finally {
      if (previous === undefined) {
        delete process.env[CHAPPIE_CLI_ENV_VAR];
      } else {
        process.env[CHAPPIE_CLI_ENV_VAR] = previous;
      }
    }
  });
});
