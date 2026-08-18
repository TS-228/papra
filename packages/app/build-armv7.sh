#!/usr/bin/env bash
set -euo pipefail

# Build linux/arm/v7 Papra images (Debian Trixie + Node 26 from source)
# and optionally push them to GHCR.
#
# Usage:
#   ./packages/app/build-armv7.sh
#   PUSH=1 ./packages/app/build-armv7.sh
#   IMAGE=ghcr.io/ts-228/papra VERSION=26.6.1 ./packages/app/build-armv7.sh

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
IMAGE="${IMAGE:-ghcr.io/ts-228/papra}"
VERSION="${VERSION:-26.6.1}"
NODE_VERSION="${NODE_VERSION:-26.7.0}"
PUSH="${PUSH:-0}"
GIT_COMMIT="${GIT_COMMIT:-$(git -C "$ROOT" rev-parse HEAD)}"
BUILD_DATE="${BUILD_DATE:-$(git -C "$ROOT" show -s --format=%cI HEAD)}"

BUILD_ARGS=(
  --platform linux/arm/v7
  -f "$ROOT/packages/app/Dockerfile.armv7"
  --build-arg "NODE_VERSION=${NODE_VERSION}"
  --build-arg "PAPRA_VERSION=${VERSION}"
  --build-arg "GIT_COMMIT=${GIT_COMMIT}"
  --build-arg "BUILD_DATE=${BUILD_DATE}"
  --provenance=false
)

OUTPUT_FLAGS=(--load)
if [[ "$PUSH" == "1" ]]; then
  OUTPUT_FLAGS=(--push)
fi

echo "Building ${IMAGE}:${VERSION}-rootless-armv7 (Node ${NODE_VERSION} from source on Debian Trixie)"

docker buildx build "${BUILD_ARGS[@]}" \
  --target papra-rootless \
  -t "${IMAGE}:latest-armv7" \
  -t "${IMAGE}:latest-rootless-armv7" \
  -t "${IMAGE}:${VERSION}-armv7" \
  -t "${IMAGE}:${VERSION}-rootless-armv7" \
  "${OUTPUT_FLAGS[@]}" \
  "$ROOT"

docker buildx build "${BUILD_ARGS[@]}" \
  --target papra-root \
  -t "${IMAGE}:latest-root-armv7" \
  -t "${IMAGE}:${VERSION}-root-armv7" \
  "${OUTPUT_FLAGS[@]}" \
  "$ROOT"
