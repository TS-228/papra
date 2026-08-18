#!/usr/bin/env python3
"""Split Temporal crate builds so host mksnapshot links i686, Node links armhf.

A single GYP none-target with both toolsets collapsed to one library path
(obj/gen/release/libnode_crates.a). Host ld then tried to link the armhf
archive (ELF EM:40) into i686 mksnapshot.
"""

from __future__ import annotations

from pathlib import Path
import sys

REPLACEMENT = r"""
    {
      'target_name': 'node_crates_i686',
      'type': 'none',
      'toolsets': ['host'],
      'hard_dependency': 1,
      'sources': [
        'Cargo.toml',
        'Cargo.lock',
        'src/lib.rs',
      ],
      'link_settings': {
        'libraries': [
          '<(PRODUCT_DIR)/libnode_crates_host.a',
        ],
      },
      'actions': [
        {
          'action_name': 'cargo_build_i686',
          'inputs': [
            '<@(_sources)'
          ],
          'outputs': [
            '<(PRODUCT_DIR)/libnode_crates_host.a',
          ],
          'action': [
            '/usr/local/bin/build-node-crates.sh',
            'i686-unknown-linux-gnu',
            '<(PRODUCT_DIR)/libnode_crates_host.a',
          ],
        }
      ],
    },
    {
      'target_name': 'node_crates_armhf',
      'type': 'none',
      'toolsets': ['target'],
      'hard_dependency': 1,
      'sources': [
        'Cargo.toml',
        'Cargo.lock',
        'src/lib.rs',
      ],
      'link_settings': {
        'libraries': [
          '<(PRODUCT_DIR)/libnode_crates_target.a',
        ],
      },
      'actions': [
        {
          'action_name': 'cargo_build_armhf',
          'inputs': [
            '<@(_sources)'
          ],
          'outputs': [
            '<(PRODUCT_DIR)/libnode_crates_target.a',
          ],
          'action': [
            '/usr/local/bin/build-node-crates.sh',
            'arm-unknown-linux-gnueabihf',
            '<(PRODUCT_DIR)/libnode_crates_target.a',
          ],
        }
      ],
    },
    {
      'target_name': 'node_crates',
      'type': 'none',
      'toolsets': ['host', 'target'],
      'hard_dependency': 1,
      'sources': [],
      'target_conditions': [
        ['_toolset=="host"', {
          'dependencies': [
            'node_crates_i686',
          ],
        }],
        ['_toolset=="target"', {
          'dependencies': [
            'node_crates_armhf',
          ],
        }],
      ],
    },
    {
      'target_name': 'temporal_capi',
"""


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("deps/crates/crates.gyp")
    text = path.read_text()
    start = text.find("    {\n      'target_name': 'node_crates',")
    end = text.find("    {\n      'target_name': 'temporal_capi',")
    if start < 0 or end < 0:
        raise SystemExit(f"could not find node_crates/temporal_capi targets in {path}")
    path.write_text(text[:start] + REPLACEMENT.lstrip("\n") + text[end + len("    {\n      'target_name': 'temporal_capi',"):])
    print(f"patched {path} with separate i686 host and armhf target crate targets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
