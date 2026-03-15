export const CHAPPIE_CLI_ENV_VAR = "CHAPPIE_CLI";
export const CHAPPIE_CLI_ENV_VALUE = "1";

export function markChappieExecEnv<T extends Record<string, string | undefined>>(env: T): T {
  return {
    ...env,
    [CHAPPIE_CLI_ENV_VAR]: CHAPPIE_CLI_ENV_VALUE,
  };
}

export function ensureChappieExecMarkerOnProcess(
  env: NodeJS.ProcessEnv = process.env,
): NodeJS.ProcessEnv {
  env[CHAPPIE_CLI_ENV_VAR] = CHAPPIE_CLI_ENV_VALUE;
  return env;
}
