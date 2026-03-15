#!/usr/bin/env bash
set -euo pipefail

cd /repo

export CHAPPIE_STATE_DIR="/tmp/chappie-test"
export CHAPPIE_CONFIG_PATH="${CHAPPIE_STATE_DIR}/chappie.json"

echo "==> Build"
pnpm build

echo "==> Seed state"
mkdir -p "${CHAPPIE_STATE_DIR}/credentials"
mkdir -p "${CHAPPIE_STATE_DIR}/agents/main/sessions"
echo '{}' >"${CHAPPIE_CONFIG_PATH}"
echo 'creds' >"${CHAPPIE_STATE_DIR}/credentials/marker.txt"
echo 'session' >"${CHAPPIE_STATE_DIR}/agents/main/sessions/sessions.json"

echo "==> Reset (config+creds+sessions)"
pnpm chappie reset --scope config+creds+sessions --yes --non-interactive

test ! -f "${CHAPPIE_CONFIG_PATH}"
test ! -d "${CHAPPIE_STATE_DIR}/credentials"
test ! -d "${CHAPPIE_STATE_DIR}/agents/main/sessions"

echo "==> Recreate minimal config"
mkdir -p "${CHAPPIE_STATE_DIR}/credentials"
echo '{}' >"${CHAPPIE_CONFIG_PATH}"

echo "==> Uninstall (state only)"
pnpm chappie uninstall --state --yes --non-interactive

test ! -d "${CHAPPIE_STATE_DIR}"

echo "OK"
