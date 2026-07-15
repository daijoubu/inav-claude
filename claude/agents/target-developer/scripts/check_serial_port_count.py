#!/usr/bin/env python3
"""
check_serial_port_count.py -- two independent checks against a target.h's
serial-port setup:

1. SERIAL_PORT_COUNT doesn't match the number of serial ports actually
   defined (1 for USE_VCP, plus one per USE_UARTn / USE_SOFTSERIALn). Nothing
   computes this count from the other defines -- it's a hand-maintained
   literal, so it silently drifts out of sync whenever a UART/softserial is
   added or removed without updating it. A wrong count doesn't stop the
   target from building; it just leaves the serial subsystem sized wrong at
   runtime.

   Deliberately skips any target.h with more than one SERIAL_PORT_COUNT
   #define. Several boards (e.g. CLRACINGF4AIR, MATEKF765, ZEEZF7) share one
   target.h across multiple build variants (V2/V3/PINIO/_SE/... selected by a
   CMakeLists -D define) with a different port count per #ifdef branch --
   correctly checking those requires evaluating which branch is actually
   active for a given build, which this script does not attempt. A full-tree
   run on 2026-07-07 found 9 such multi-variant files (all false positives
   under a naive flat scan) and 0 real mismatches among the remaining
   single-definition targets -- treat a finding here as a regression, not
   backlog.

2. DEFAULT_FEATURES includes FEATURE_SOFTSERIAL but target.h defines no
   USE_SOFTSERIALn at all. Confirmed harmless at runtime -- every consumer
   (pwm_mapping.c, serial_softserial.c) gates on `#if defined(USE_SOFTSERIALn)`
   first, so the feature bit is just a dead no-op -- but it's a reliable sign
   of a stale copy-paste in DEFAULT_FEATURES from whatever target this one was
   based on. A full-tree run on 2026-07-07 found 10 such targets: NOTICE, not
   CERTAIN, since nothing actually breaks.

Usage: ./check_serial_port_count.py <inav_checkout_root> [--target NAME]
"""
import argparse
import re
from pathlib import Path

COUNT_RE = re.compile(r'#\s*define\s+SERIAL_PORT_COUNT\s+(\d+)')
VCP_RE = re.compile(r'#\s*define\s+USE_VCP\b')
UART_RE = re.compile(r'#\s*define\s+USE_(UART\d+)\b')
SOFTSERIAL_RE = re.compile(r'#\s*define\s+USE_(SOFTSERIAL\d+)\b')
DEFAULT_FEATURES_RE = re.compile(r'#\s*define\s+DEFAULT_FEATURES\b(.*)$', re.MULTILINE)


def check_target(target_dir: Path):
    """Returns a list of (severity, message) findings."""
    target_h = target_dir / "target.h"
    try:
        text = target_h.read_text(errors="ignore")
    except OSError:
        return []

    text = re.sub(r'\\\r?\n\s*', ' ', text)  # join backslash-continued lines
    lines = [re.sub(r'//.*$', '', l) for l in text.splitlines() if not l.strip().startswith("//")]
    clean = "\n".join(lines)

    findings = []

    counts = COUNT_RE.findall(clean)
    if len(counts) == 1:  # 0 = no macro (not this script's job); >1 = build-variant file, skip
        declared = int(counts[0])
        vcp = 1 if VCP_RE.search(clean) else 0
        uarts = len(set(UART_RE.findall(clean)))
        softserials = len(set(SOFTSERIAL_RE.findall(clean)))
        computed = vcp + uarts + softserials
        if computed != declared:
            findings.append((
                "CERTAIN",
                f"SERIAL_PORT_COUNT is {declared} but VCP({vcp}) + UART({uarts}) + "
                f"SOFTSERIAL({softserials}) = {computed}"
            ))

    df_match = DEFAULT_FEATURES_RE.search(clean)
    if df_match and re.search(r'\bFEATURE_SOFTSERIAL\b', df_match.group(1)):
        if not SOFTSERIAL_RE.search(clean):
            findings.append((
                "NOTICE",
                "DEFAULT_FEATURES includes FEATURE_SOFTSERIAL but no USE_SOFTSERIALn is "
                "defined -- dead feature bit, likely copy-paste leftover"
            ))

    return findings


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

    findings = []
    for target_dir in targets:
        for severity, message in check_target(target_dir):
            findings.append((target_dir.name, severity, message))

    for name, severity, message in findings:
        print(f"\n{name}: [{severity}] {message}")

    print()
    if not findings:
        print(f"No serial-port findings ({len(targets)} target(s) checked).")
    else:
        certain = sum(1 for _, s, _ in findings if s == "CERTAIN")
        notice = len(findings) - certain
        print(
            f"{certain} CERTAIN, {notice} NOTICE across {len(targets)} target(s) checked."
        )


if __name__ == "__main__":
    main()
