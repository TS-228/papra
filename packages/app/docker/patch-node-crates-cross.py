#!/usr/bin/env python3
"""Make Node's Temporal crate build for both GYP toolsets when cross-compiling.

V8 snapshot tools run on the builder (i686 here) while the Node binary is
armhf. crates.gyp leaves cargo_rust_target empty on Linux, so cargo gets
`--target` with no value ("error: target was empty") and writes to
`obj/gen//release`. Drive cargo from a wrapper that picks the rustc triple
from GYP's host vs target output directory.
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
          '<(SHARED_INTERMEDIATE_DIR)/release/<(STATIC_LIB_PREFIX)node_crates<(STATIC_LIB_SUFFIX)',
        ],
      },
      'actions': [
        {
          'action_name': 'cargo_build',
          'inputs': [
            '<@(_sources)'
          ],
          'outputs': [
            '<(SHARED_INTERMEDIATE_DIR)/release/<(STATIC_LIB_PREFIX)node_crates<(STATIC_LIB_SUFFIX)',
          ],
          'action': [
            '/usr/local/bin/build-node-crates.sh',
            '<(SHARED_INTERMEDIATE_DIR)',
          ],
        }
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
    print(f"patched {path} to build Temporal crates via build-node-crates.sh")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
