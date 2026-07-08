#!/usr/bin/env python3
"""
check_pin_conflicts.py -- flags a single physical MCU pin assigned to more
than one peripheral macro in the same target's target.h -- e.g. UART8_RX_PIN
and SPI4_MISO_PIN both set to PE0. A compiler cannot catch this (each macro is
just an independent #define, with no cross-checking against any other macro's
value); the collision only ever shows up as one of the two peripherals
mysteriously not working on real hardware, exactly the kind of failure mode
that motivated this whole script family (see check_dma_conflicts.py's
docstring for the AEDROXH7/DAKEFPVH743PRO DMA-collision incidents this is a
sibling check to).

Usage: ./check_pin_conflicts.py <inav_checkout_root> [options]
Example: ./check_pin_conflicts.py ~/Documents/planes/inavflight/inav --target AXISFLYINGH743PRO

Options:
  --target NAME   only report findings for this target directory name

Findings are a checklist to verify by hand, not a pass/fail gate. One
particularly common, usually-benign pattern: a single CS pin assigned to two
alternate chip macros (e.g. MPU6000_CS_PIN and ICM42605_CS_PIN both on the
same pin) -- boards routinely support either of two IMU/flash/OSD chip
variants on one footprint, detected at runtime, so the shared CS pin is by
design, not a mistake. Other rarer legitimate cases exist too (a pin reused
via a physical strap, or a build-time option that disables one of the two
conflicting features) -- confirm each finding against the schematic/feature
set before treating it as a bug. See the target-developer README's
"Patterns" section for why a pin appearing to be reused is not, by itself,
proof that either use is wrong -- only that the two macros need to be
checked against each other and against the real board.
"""
import argparse
from collections import defaultdict
from pathlib import Path
import re

PIN_DEFINE_RE = re.compile(
    r'^\s*#\s*define\s+([A-Za-z_][A-Za-z0-9_]*)\s+(P[A-K]\d{1,2})\b'
)


def collect_pin_defines(target_h: Path):
    """pin value -> list of *distinct* macro names assigned to it, in file
    order. Some targets redefine the same bus macro (e.g. SPI1_NSS_PIN)
    identically inside multiple #ifdef board-revision blocks -- that's
    repeated boilerplate, not a conflict, so the same name is only kept
    once per pin."""
    pins = defaultdict(list)
    try:
        text = target_h.read_text(errors="ignore")
    except OSError:
        return pins
    for line in text.splitlines():
        if line.strip().startswith("//"):
            continue
        m = PIN_DEFINE_RE.match(line)
        if m:
            name, pin = m.groups()
            if name not in pins[pin]:
                pins[pin].append(name)
    return pins


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
    if args.target:
        targets = [d for d in targets if d.name == args.target]
        if not targets:
            raise SystemExit(f"No target named {args.target} under {target_root}")

    total_findings = 0
    for target_dir in targets:
        pins = collect_pin_defines(target_dir / "target.h")
        conflicts = {pin: names for pin, names in pins.items() if len(names) > 1}
        if not conflicts:
            continue
        total_findings += len(conflicts)
        print(f"\n{target_dir.name}:")
        for pin, names in sorted(conflicts.items()):
            print(f"  {pin} assigned to {len(names)} macros: {', '.join(names)}")

    print()
    if total_findings == 0:
        print(f"No pins assigned to more than one macro found ({len(targets)} target(s) checked).")
    else:
        print(
            f"{total_findings} pin-reuse finding(s) across {len(targets)} target(s) checked. "
            "Verify each by hand -- rare legitimate shared-pin designs are expected."
        )


if __name__ == "__main__":
    main()
