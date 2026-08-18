#!/bin/bash
# Build Node's vendored temporal_capi staticlib for one rustc triple.
# Args: <rust-target> <output.a>
set -euo pipefail

rust_target="${1:?rust target triple required}"
output="${2:?output .a path required}"

if [[ -f /tmp/node/deps/crates/Cargo.toml ]]; then
  cd /tmp/node/deps/crates
elif [[ -f Cargo.toml ]]; then
  :
else
  echo "node crates Cargo.toml not found" >&2
  exit 1
fi

target_dir="$(dirname "$output")/cargo-${rust_target}"
echo "building node_crates for ${rust_target} -> ${output}"

cargo rustc \
  --release \
  --target "$rust_target" \
  --frozen \
  --target-dir "$target_dir"

mkdir -p "$(dirname "$output")"
cp -a "${target_dir}/${rust_target}/release/libnode_crates.a" "$output"
test -f "$output"
