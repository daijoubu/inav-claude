#!/usr/bin/env python3
"""
check_board_identifier.py -- flags a target.h whose TARGET_BOARD_IDENTIFIER is
not exactly 4 characters, or that collides with another target's identifier.

This identifier is a firmware-level runtime board ID (distinct from the
directory/CMake target name) -- INAV's boot/MSP identification code assumes it
is exactly 4 characters, and a collision between two different boards means
tooling that identifies a board by this string (e.g. the configurator, or any
script keyed on it) cannot tell them apart at runtime.

Usage: ./check_board_identifier.py <inav_checkout_root> [--target NAME]

Findings are a checklist, not a pass/fail gate -- a full-tree run on 2026-07-07
found 36 targets with a non-4-char identifier and 15 groups of targets sharing
one identifier, none of which have caused a reported runtime problem yet (the
4-char assumption may be soft in practice). Still worth fixing on sight,
especially for a new target, since a fresh collision is easy to avoid and hard
to debug once it exists.
"""
import argparse
from collections import defaultdict
from pathlib import Path
import re

IDENTIFIER_RE = re.compile(r'^\s*#\s*define\s+TARGET_BOARD_IDENTIFIER\s+"([^"]*)"')


def find_identifier(target_h: Path):
    try:
        text = target_h.read_text(errors="ignore")
    except OSError:
        return None
    for line in text.splitlines():
        if line.strip().startswith("//"):
            continue
        m = IDENTIFIER_RE.match(line)
        if m:
            return m.group(1)
    return None


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("inav_root", nargs="?", default=".", help="Path to an INAV checkout")
    ap.add_argument("--target", help="Only report findings for this target directory name")
    args = ap.parse_args()

    root = Path(args.inav_root).expanduser().resolve()
    target_root = root / "src" / "main" / "target"
    if not target_root.is_dir():
        raise SystemExit(f"Can't find {target_root} -- pass the INAV checkout root")

    targets = sorted(d for d in target_root.iterdir() if d.is_dir() and (d / "target.h").is_file())

    by_identifier = defaultdict(list)
    length_findings = []
    for target_dir in targets:
        ident = find_identifier(target_dir / "target.h")
        if ident is None:
            continue
        by_identifier[ident].append(target_dir.name)
        if len(ident) != 4:
            length_findings.append((target_dir.name, ident))

    dupes = {ident: names for ident, names in by_identifier.items() if len(names) > 1}

    checked_count = len(targets)
    if args.target:
        if not any(d.name == args.target for d in targets):
            raise SystemExit(f"No target named {args.target} under {target_root}")
        length_findings = [f for f in length_findings if f[0] == args.target]
        dupes = {ident: names for ident, names in dupes.items() if args.target in names}
        checked_count = 1

    for name, ident in sorted(length_findings):
        print(f"\n{name}: [CERTAIN] TARGET_BOARD_IDENTIFIER \"{ident}\" is {len(ident)} chars, not 4")

    for ident, names in sorted(dupes.items()):
        print(f"\n\"{ident}\": [CERTAIN] shared by {len(names)} targets: {', '.join(sorted(names))}")

    print()
    if not length_findings and not dupes:
        print(f"No TARGET_BOARD_IDENTIFIER findings ({checked_count} target(s) checked).")
    else:
        print(
            f"{len(length_findings)} wrong-length, {len(dupes)} duplicate-identifier group(s) "
            f"across {checked_count} target(s) checked."
        )


if __name__ == "__main__":
    main()
