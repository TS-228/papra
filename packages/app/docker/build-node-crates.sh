#!/bin/bash
# Build Node Temporal staticlibs for host snapshot tools (i686) and armhf Node.
# Arg: PRODUCT_DIR (e.g. /tmp/node/out/Release)
set -euo pipefail

product_dir="${1:?PRODUCT_DIR required}"

if [[ -f /tmp/node/deps/crates/Cargo.toml ]]; then
  cd /tmp/node/deps/crates
elif [[ -f Cargo.toml ]]; then
  :
else
  echo "node crates Cargo.toml not found" >&2
  exit 1
fi

build_one() {
  local rust_target="$1"
  local output="$2"
  local target_dir="${product_dir}/cargo-${rust_target}"
  echo "building node_crates for ${rust_target} -> ${output}"
  cargo rustc \
    --release \
    --target "$rust_target" \
    --frozen \
    --target-dir "$target_dir"
  mkdir -p "$(dirname "$output")"
  cp -a "${target_dir}/${rust_target}/release/libnode_crates.a" "$output"
  test -f "$output"
}

build_one i686-unknown-linux-gnu "${product_dir}/libnode_crates_host.a"
build_one arm-unknown-linux-gnueabihf "${product_dir}/libnode_crates_target.a"
ln -sfn libnode_crates_target.a "${product_dir}/libnode_crates.a"
