#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SMOKE_IMAGE="${CHAPPIE_INSTALL_SMOKE_IMAGE:-${CHAPPIEDBOT_INSTALL_SMOKE_IMAGE:-chappie-install-smoke:local}}"
NONROOT_IMAGE="${CHAPPIE_INSTALL_NONROOT_IMAGE:-${CHAPPIEDBOT_INSTALL_NONROOT_IMAGE:-chappie-install-nonroot:local}}"
INSTALL_URL="${CHAPPIE_INSTALL_URL:-${CHAPPIEDBOT_INSTALL_URL:-https://chappie.bot/install.sh}}"
CLI_INSTALL_URL="${CHAPPIE_INSTALL_CLI_URL:-${CHAPPIEDBOT_INSTALL_CLI_URL:-https://chappie.bot/install-cli.sh}}"
SKIP_NONROOT="${CHAPPIE_INSTALL_SMOKE_SKIP_NONROOT:-${CHAPPIEDBOT_INSTALL_SMOKE_SKIP_NONROOT:-0}}"
SKIP_SMOKE_IMAGE_BUILD="${CHAPPIE_INSTALL_SMOKE_SKIP_IMAGE_BUILD:-${CHAPPIEDBOT_INSTALL_SMOKE_SKIP_IMAGE_BUILD:-0}}"
SKIP_NONROOT_IMAGE_BUILD="${CHAPPIE_INSTALL_NONROOT_SKIP_IMAGE_BUILD:-${CHAPPIEDBOT_INSTALL_NONROOT_SKIP_IMAGE_BUILD:-0}}"
LATEST_DIR="$(mktemp -d)"
LATEST_FILE="${LATEST_DIR}/latest"

if [[ "$SKIP_SMOKE_IMAGE_BUILD" == "1" ]]; then
  echo "==> Reuse prebuilt smoke image: $SMOKE_IMAGE"
else
  echo "==> Build smoke image (upgrade, root): $SMOKE_IMAGE"
  docker build \
    -t "$SMOKE_IMAGE" \
    -f "$ROOT_DIR/scripts/docker/install-sh-smoke/Dockerfile" \
    "$ROOT_DIR/scripts/docker"
fi

echo "==> Run installer smoke test (root): $INSTALL_URL"
docker run --rm -t \
  -v "${LATEST_DIR}:/out" \
  -e CHAPPIE_INSTALL_URL="$INSTALL_URL" \
  -e CHAPPIE_INSTALL_METHOD=npm \
  -e CHAPPIE_INSTALL_LATEST_OUT="/out/latest" \
  -e CHAPPIE_INSTALL_SMOKE_PREVIOUS="${CHAPPIE_INSTALL_SMOKE_PREVIOUS:-${CHAPPIEDBOT_INSTALL_SMOKE_PREVIOUS:-}}" \
  -e CHAPPIE_INSTALL_SMOKE_SKIP_PREVIOUS="${CHAPPIE_INSTALL_SMOKE_SKIP_PREVIOUS:-${CHAPPIEDBOT_INSTALL_SMOKE_SKIP_PREVIOUS:-0}}" \
  -e CHAPPIE_NO_ONBOARD=1 \
  -e DEBIAN_FRONTEND=noninteractive \
  "$SMOKE_IMAGE"

LATEST_VERSION=""
if [[ -f "$LATEST_FILE" ]]; then
  LATEST_VERSION="$(cat "$LATEST_FILE")"
fi

if [[ "$SKIP_NONROOT" == "1" ]]; then
  echo "==> Skip non-root installer smoke (CHAPPIE_INSTALL_SMOKE_SKIP_NONROOT=1)"
else
  if [[ "$SKIP_NONROOT_IMAGE_BUILD" == "1" ]]; then
    echo "==> Reuse prebuilt non-root image: $NONROOT_IMAGE"
  else
    echo "==> Build non-root image: $NONROOT_IMAGE"
    docker build \
      -t "$NONROOT_IMAGE" \
      -f "$ROOT_DIR/scripts/docker/install-sh-nonroot/Dockerfile" \
      "$ROOT_DIR/scripts/docker"
  fi

  echo "==> Run installer non-root test: $INSTALL_URL"
  docker run --rm -t \
    -e CHAPPIE_INSTALL_URL="$INSTALL_URL" \
    -e CHAPPIE_INSTALL_METHOD=npm \
    -e CHAPPIE_INSTALL_EXPECT_VERSION="$LATEST_VERSION" \
    -e CHAPPIE_NO_ONBOARD=1 \
    -e DEBIAN_FRONTEND=noninteractive \
    "$NONROOT_IMAGE"
fi

if [[ "${CHAPPIE_INSTALL_SMOKE_SKIP_CLI:-${CHAPPIEDBOT_INSTALL_SMOKE_SKIP_CLI:-0}}" == "1" ]]; then
  echo "==> Skip CLI installer smoke (CHAPPIE_INSTALL_SMOKE_SKIP_CLI=1)"
  exit 0
fi

if [[ "$SKIP_NONROOT" == "1" ]]; then
  echo "==> Skip CLI installer smoke (non-root image skipped)"
  exit 0
fi

echo "==> Run CLI installer non-root test (same image)"
docker run --rm -t \
  --entrypoint /bin/bash \
  -e CHAPPIE_INSTALL_URL="$INSTALL_URL" \
  -e CHAPPIE_INSTALL_CLI_URL="$CLI_INSTALL_URL" \
  -e CHAPPIE_NO_ONBOARD=1 \
  -e DEBIAN_FRONTEND=noninteractive \
  "$NONROOT_IMAGE" -lc "curl -fsSL \"$CLI_INSTALL_URL\" | bash -s -- --set-npm-prefix --no-onboard"
