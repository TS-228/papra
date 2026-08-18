#!/bin/bash
# Build Node's vendored temporal_capi staticlib for the current GYP toolset.
# Host snapshot tools are i686; the Node binary is armhf. Infer the Rust triple
# from GYP's SHARED_INTERMEDIATE_DIR (obj.host vs obj).
set -euo pipefail

target_dir="${1:?SHARED_INTERMEDIATE_DIR required}"

if [[ "$target_dir" == *obj.host* ]]; then
  rust_target=i686-unknown-linux-gnu
else
  rust_target=arm-unknown-linux-gnueabihf
fi

echo "building node_crates for ${rust_target} in ${target_dir}"

cargo rustc \
  --release \
  --target "$rust_target" \
  --frozen \
  --target-dir "$target_dir"

mkdir -p "$target_dir/release"
ln -sfn "../${rust_target}/release/libnode_crates.a" "$target_dir/release/libnode_crates.a"
test -f "$target_dir/release/libnode_crates.a"
