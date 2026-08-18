#!/usr/bin/env python3
"""Point GYP host vs target link lines at matching Temporal staticlibs.

A single none-target cannot give mksnapshot.host an i686 archive while Node
gets armhf. After configure, rewrite .mk files so host toolsets link
libnode_crates_host.a and target toolsets link libnode_crates_target.a.
"""

from __future__ import annotations

from pathlib import Path
import sys

HOST_LIB = "libnode_crates_host.a"
TARGET_LIB = "libnode_crates_target.a"
GENERIC_LIB = "libnode_crates.a"


def is_host_makefile(path: Path) -> bool:
    name = path.name
    text = str(path)
    return ".host.mk" in name or name.endswith("_host.mk") or "/obj.host/" in text


def rewrite(text: str, lib: str) -> str:
    for old in (
        "obj/gen/release/" + GENERIC_LIB,
        "obj.host/gen/release/" + GENERIC_LIB,
        GENERIC_LIB,
        HOST_LIB,
        TARGET_LIB,
    ):
        text = text.replace(old, lib)
    return text


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("out")
    changed = 0
    for path in root.rglob("*.mk"):
        original = path.read_text()
        if GENERIC_LIB not in original and HOST_LIB not in original and TARGET_LIB not in original:
            if "node_crates" not in original:
                continue
        lib = HOST_LIB if is_host_makefile(path) else TARGET_LIB
        updated = rewrite(original, lib)
        if updated != original:
            path.write_text(updated)
            changed += 1
            print(f"crates link: {path} -> {lib}")
    print(f"rewrote {changed} makefiles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
