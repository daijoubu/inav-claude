#!/usr/bin/env python3
"""
check_default_features.py -- flags a target.h with no DEFAULT_FEATURES macro
at all, or one whose value looks suspiciously thin.

INAV's core fallback (fc/config.c) is:
    #ifndef DEFAULT_FEATURES
    #define DEFAULT_FEATURES 0
    #endif
So a target that never defines DEFAULT_FEATURES silently boots with EVERY
feature off -- VBAT, CURRENT_METER, OSD, TELEMETRY, etc. all disabled by
default, even when the pins/wiring for all of them are otherwise correct.
This is not a typo (check_macro_typos.py can't catch it -- there's no wrong
name to flag, the line is just missing) and it doesn't stop the target from
building or matching another board's pin map -- it only ever shows up as
"the feature doesn't work" on real hardware. Written after the
AXISFLYINGH743PRO incident (see target-developer README/lessons): ADC and
OSD both looked hardware-broken but were actually just never turned on by
default because target.h had no DEFAULT_FEATURES line at all.

A DEFAULT_FEATURES line that exists but is unusually short is the same bug
in a milder form -- almost always a sign that most of the normal feature
set (OSD | TELEMETRY | CURRENT_METER | VBAT | ...) got dropped/forgotten
during a copy-paste port, not a deliberate minimal board.

Usage: ./check_default_features.py <inav_checkout_root> [--target NAME]

Findings are a checklist, not a pass/fail gate -- a handful of genuinely
minimal targets (e.g. no battery monitoring hardware at all) may legitimately
have a short DEFAULT_FEATURES value. Verify against the target's actual
hardware before treating a NOTICE as a bug.
"""
import argparse
import re
from pathlib import Path

MIN_VALUE_LENGTH = 80

DEFAULT_FEATURES_RE = re.compile(r'^\s*#\s*define\s+DEFAULT_FEATURES\b(.*)$')


def check_target(target_dir: Path):
    """Returns (severity, message) or None if no finding."""
    target_h = target_dir / "target.h"
    try:
        text = target_h.read_text(errors="ignore")
    except OSError:
        return None

    # Join backslash-continued lines
    text = re.sub(r'\\\r?\n\s*', ' ', text)

    for line in text.splitlines():
        if line.strip().startswith("//"):
            continue
        m = DEFAULT_FEATURES_RE.match(line)
        if m:
            value = re.sub(r'//.*$', '', m.group(1)).strip()
            if len(value) < MIN_VALUE_LENGTH:
                return (
                    "NOTICE",
                    f"DEFAULT_FEATURES present but only {len(value)} chars "
                    f"('{value}') -- confirm this is deliberately minimal, "
                    f"not a dropped feature set"
                )
            return None  # present and long enough -- no finding

    return (
        "CERTAIN",
        "no DEFAULT_FEATURES macro at all -- falls back to 0 (every feature "
        "off) per fc/config.c's #ifndef default"
    )


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
        result = check_target(target_dir)
        if result:
            severity, message = result
            findings.append((severity, target_dir.name, message))

    findings.sort(key=lambda f: (f[0] != "CERTAIN", f[1]))

    certain_count = sum(1 for f in findings if f[0] == "CERTAIN")
    notice_count = len(findings) - certain_count

    for severity, name, message in findings:
        print(f"\n{name}: [{severity}] {message}")

    print()
    if not findings:
        print(f"No DEFAULT_FEATURES findings ({len(targets)} target(s) checked).")
    else:
        print(
            f"{certain_count} CERTAIN (missing entirely), {notice_count} NOTICE "
            f"(present but thin) across {len(targets)} target(s) checked. "
            "Verify each by hand -- a genuinely minimal board is possible."
        )


if __name__ == "__main__":
    main()
