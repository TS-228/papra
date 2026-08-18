#!/usr/bin/env python3
"""Drive Temporal crate builds from a wrapper that emits host and target libs."""

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
          '<(PRODUCT_DIR)/libnode_crates.a',
        ],
      },
      'actions': [
        {
          'action_name': 'cargo_build',
          'inputs': [
            '<@(_sources)'
          ],
          'outputs': [
            '<(PRODUCT_DIR)/libnode_crates.a',
            '<(PRODUCT_DIR)/libnode_crates_host.a',
            '<(PRODUCT_DIR)/libnode_crates_target.a',
          ],
          'action': [
            '/usr/local/bin/build-node-crates.sh',
            '<(PRODUCT_DIR)',
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
    print(f"patched {path} to emit host and target Temporal staticlibs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
