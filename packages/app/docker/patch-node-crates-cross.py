#!/usr/bin/env python3
"""Make Node's Temporal crate build for both GYP toolsets when cross-compiling.

V8 snapshot tools run on the builder (i686 here) while the Node binary is
armhf. crates.gyp uses a single cargo_rust_target, which is empty on Linux, so
cargo would emit a host x86_64 library that cannot link into either toolset.

GYP forbids link_settings inside target_conditions, so only the rust triple and
library path are overridden per toolset.
"""

from __future__ import annotations

from pathlib import Path
import sys

UNIX_NODE_CRATES = """
    {
      'target_name': 'node_crates',
      'type': 'none',
      'toolsets': ['host', 'target'],
      'hard_dependency': 1,
      'sources': [
        'Cargo.toml',
        'Cargo.lock',
        'src/lib.rs',
      ],
      'link_settings': {
        'libraries': [
          '<(node_crates_libpath)',
        ],
      },
      'actions': [
        {
          'action_name': 'cargo_build',
          'inputs': [
            '<@(_sources)'
          ],
          'outputs': [
            '<(node_crates_libpath)'
          ],
          'action': [
            '<(cargo)',
            'rustc',
            '--release',
            '--target',
            '<(cargo_rust_target)',
            '--frozen',
            '--target-dir',
            '<(SHARED_INTERMEDIATE_DIR)',
          ],
        }
      ],
      'target_conditions': [
        ['_toolset=="host"', {
          'variables': {
            'cargo_rust_target': 'i686-unknown-linux-gnu',
            'node_crates_libpath': '<(SHARED_INTERMEDIATE_DIR)/i686-unknown-linux-gnu/release/<(STATIC_LIB_PREFIX)node_crates<(STATIC_LIB_SUFFIX)',
          },
        }],
        ['_toolset=="target"', {
          'variables': {
            'cargo_rust_target': 'arm-unknown-linux-gnueabihf',
            'node_crates_libpath': '<(SHARED_INTERMEDIATE_DIR)/arm-unknown-linux-gnueabihf/release/<(STATIC_LIB_PREFIX)node_crates<(STATIC_LIB_SUFFIX)',
          },
        }],
      ],
    },
"""


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("deps/crates/crates.gyp")
    text = path.read_text()
    start = text.find("    {\n      'target_name': 'node_crates',")
    end = text.find("    {\n      'target_name': 'temporal_capi',")
    if start < 0 or end < 0:
        raise SystemExit(f"could not find node_crates target in {path}")
    path.write_text(text[:start] + UNIX_NODE_CRATES.lstrip("\n") + text[end:])
    print(f"patched {path} for i686 host + armhf target Temporal crates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
