#!/usr/bin/env bash
set -euo pipefail

# Build linux/arm/v7 Papra images using the unofficial Node.js armv7l
# Debian slim image, and optionally push them to GHCR.
#
# Usage:
#   ./packages/app/build-armv7.sh
#   PUSH=1 ./packages/app/build-armv7.sh
#   IMAGE=ghcr.io/ts-228/papra VERSION=26.6.1 ./packages/app/build-armv7.sh
#   NODE_IMAGE=ghcr.io/ts-228/unofficial-builds/node-armv7l:v26.8.1 ./packages/app/build-armv7.sh

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
IMAGE="${IMAGE:-ghcr.io/ts-228/papra}"
VERSION="${VERSION:-$(python3 -c 'import json; print(json.load(open("'"$ROOT"'/packages/app/package.json"))["version"])')}"
NODE_IMAGE="${NODE_IMAGE:-ghcr.io/ts-228/unofficial-builds/node-armv7l:latest}"
PNPM_VERSION="${PNPM_VERSION:-$(python3 -c 'import json; print(json.load(open("'"$ROOT"'/package.json"))["packageManager"].split("@",1)[1])')}"
PUSH="${PUSH:-0}"
GIT_COMMIT="${GIT_COMMIT:-$(git -C "$ROOT" rev-parse HEAD)}"
BUILD_DATE="${BUILD_DATE:-$(git -C "$ROOT" show -s --format=%cI HEAD)}"

BUILD_ARGS=(
  --platform linux/arm/v7
  -f "$ROOT/packages/app/Dockerfile.armv7"
  --build-arg "NODE_IMAGE=${NODE_IMAGE}"
  --build-arg "PNPM_VERSION=${PNPM_VERSION}"
  --build-arg "PAPRA_VERSION=${VERSION}"
  --build-arg "GIT_COMMIT=${GIT_COMMIT}"
  --build-arg "BUILD_DATE=${BUILD_DATE}"
  --provenance=false
)

OUTPUT_FLAGS=(--load)
if [[ "$PUSH" == "1" ]]; then
  OUTPUT_FLAGS=(--push)
fi

echo "Building ${IMAGE}:${VERSION}-rootless-armv7 (Node image ${NODE_IMAGE})"

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
