#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE_NAME="${CHAPPIE_IMAGE:-${CHAPPIEDBOT_IMAGE:-chappie:local}}"
LIVE_IMAGE_NAME="${CHAPPIE_LIVE_IMAGE:-${CHAPPIEDBOT_LIVE_IMAGE:-${IMAGE_NAME}-live}}"
CONFIG_DIR="${CHAPPIE_CONFIG_DIR:-${CHAPPIEDBOT_CONFIG_DIR:-$HOME/.chappie}}"
WORKSPACE_DIR="${CHAPPIE_WORKSPACE_DIR:-${CHAPPIEDBOT_WORKSPACE_DIR:-$HOME/.chappie/workspace}}"
PROFILE_FILE="${CHAPPIE_PROFILE_FILE:-${CHAPPIEDBOT_PROFILE_FILE:-$HOME/.profile}}"

PROFILE_MOUNT=()
if [[ -f "$PROFILE_FILE" ]]; then
  PROFILE_MOUNT=(-v "$PROFILE_FILE":/home/node/.profile:ro)
fi

read -r -d '' LIVE_TEST_CMD <<'EOF' || true
set -euo pipefail
[ -f "$HOME/.profile" ] && source "$HOME/.profile" || true
tmp_dir="$(mktemp -d)"
cleanup() {
  rm -rf "$tmp_dir"
}
trap cleanup EXIT
tar -C /src \
  --exclude=.git \
  --exclude=node_modules \
  --exclude=dist \
  --exclude=ui/dist \
  --exclude=ui/node_modules \
  -cf - . | tar -C "$tmp_dir" -xf -
ln -s /app/node_modules "$tmp_dir/node_modules"
ln -s /app/dist "$tmp_dir/dist"
cd "$tmp_dir"
pnpm test:live
EOF

echo "==> Build live-test image: $LIVE_IMAGE_NAME (target=build)"
docker build --target build -t "$LIVE_IMAGE_NAME" -f "$ROOT_DIR/Dockerfile" "$ROOT_DIR"

echo "==> Run live model tests (profile keys)"
docker run --rm -t \
  --entrypoint bash \
  -e COREPACK_ENABLE_DOWNLOAD_PROMPT=0 \
  -e HOME=/home/node \
  -e NODE_OPTIONS=--disable-warning=ExperimentalWarning \
  -e CHAPPIE_LIVE_TEST=1 \
  -e CHAPPIE_LIVE_MODELS="${CHAPPIE_LIVE_MODELS:-${CHAPPIEDBOT_LIVE_MODELS:-modern}}" \
  -e CHAPPIE_LIVE_PROVIDERS="${CHAPPIE_LIVE_PROVIDERS:-${CHAPPIEDBOT_LIVE_PROVIDERS:-}}" \
  -e CHAPPIE_LIVE_MAX_MODELS="${CHAPPIE_LIVE_MAX_MODELS:-${CHAPPIEDBOT_LIVE_MAX_MODELS:-48}}" \
  -e CHAPPIE_LIVE_MODEL_TIMEOUT_MS="${CHAPPIE_LIVE_MODEL_TIMEOUT_MS:-${CHAPPIEDBOT_LIVE_MODEL_TIMEOUT_MS:-}}" \
  -e CHAPPIE_LIVE_REQUIRE_PROFILE_KEYS="${CHAPPIE_LIVE_REQUIRE_PROFILE_KEYS:-${CHAPPIEDBOT_LIVE_REQUIRE_PROFILE_KEYS:-}}" \
  -v "$ROOT_DIR":/src:ro \
  -v "$CONFIG_DIR":/home/node/.chappie \
  -v "$WORKSPACE_DIR":/home/node/.chappie/workspace \
  "${PROFILE_MOUNT[@]}" \
  "$LIVE_IMAGE_NAME" \
  -lc "$LIVE_TEST_CMD"
