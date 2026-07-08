#!/usr/bin/env python3
"""
check_target_invariants.py -- three small, unrelated target.h/target.c
invariants, each a single hard rule with no interesting judgment call once a
target is flagged. Bundled into one script because each check is a handful of
lines; a full-tree run of every one of these on 2026-07-07 found zero
findings, so treat any hit as a regression, not backlog.

1. BEEPER_PWM_FREQUENCY requires a DEF_TIM(...TIM_USE_BEEPER...) entry in
   target.c. Without one, the beeper pin has no PWM timer to drive it at
   that frequency -- either the define is stale cruft, or a DEF_TIM entry
   was dropped/never added.

2. GYRO_n_EXTI_PIN / USE_GYRO_EXTI in target.h requires a
   BUSDEV_REGISTER_SPI_TAG(...) entry in target.c for that gyro. INAV's
   legacy USE_IMU_xxx gyro driver path (no BUSDEV_REGISTER_SPI_TAG) is
   polled and never reads an EXTI pin -- defining one there is a leftover
   that does nothing, usually from copying a target that used the other
   registration style.

3. AT32 targets (detected via a `target_at32f43x*(...)` call in
   CMakeLists.txt): a UARTn with an RX_PIN defined must also define a
   TX_PIN, even as `NONE`, for an RX-only port. The AT32 UART driver
   dereferences the TX pin macro unconditionally; omitting it entirely (as
   opposed to explicitly defining it `NONE`) is a compile error on this
   platform, unlike STM32.

Usage: ./check_target_invariants.py <inav_checkout_root> [--target NAME]
"""
import argparse
import re
from pathlib import Path

BEEPER_FREQ_RE = re.compile(r'#\s*define\s+BEEPER_PWM_FREQUENCY\b')
DEF_TIM_BEEPER_RE = re.compile(r'DEF_TIM\([^)]*TIM_USE_BEEPER')
GYRO_EXTI_RE = re.compile(r'#\s*define\s+(GYRO_\d+_EXTI_PIN|USE_GYRO_EXTI)\b')
BUSDEV_SPI_TAG_RE = re.compile(r'BUSDEV_REGISTER_SPI_TAG')
AT32_CMAKE_RE = re.compile(r'target_at32f43x\w*\s*\(')
UART_DEFINE_RE = re.compile(r'#\s*define\s+USE_(UART\d+)\b')


def clean_text(path: Path):
    try:
        text = path.read_text(errors="ignore")
    except OSError:
        return ""
    return "\n".join(re.sub(r'//.*$', '', l) for l in text.splitlines())


def check_beeper_timer(h_clean: str, c_text: str):
    if not BEEPER_FREQ_RE.search(h_clean):
        return None
    if DEF_TIM_BEEPER_RE.search(c_text):
        return None
    return "BEEPER_PWM_FREQUENCY defined but no DEF_TIM(...TIM_USE_BEEPER...) entry in target.c"


def check_gyro_exti_legacy(h_clean: str, c_text: str):
    if not GYRO_EXTI_RE.search(h_clean):
        return None
    if BUSDEV_SPI_TAG_RE.search(c_text):
        return None
    return "GYRO_n_EXTI_PIN/USE_GYRO_EXTI defined but no BUSDEV_REGISTER_SPI_TAG in target.c -- legacy IMU path never reads this pin"


def check_at32_uart_tx(h_clean: str, cmakelists_text: str):
    if not AT32_CMAKE_RE.search(cmakelists_text):
        return []
    findings = []
    for uart in sorted(set(UART_DEFINE_RE.findall(h_clean))):
        has_rx = re.search(rf'#\s*define\s+{uart}_RX_PIN\b', h_clean)
        has_tx = re.search(rf'#\s*define\s+{uart}_TX_PIN\b', h_clean)
        if has_rx and not has_tx:
            findings.append(f"{uart}_RX_PIN defined with no {uart}_TX_PIN at all (AT32 needs it explicit, e.g. `NONE`)")
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

    total_findings = 0
    for target_dir in targets:
        h_clean = clean_text(target_dir / "target.h")
        c_text = clean_text(target_dir / "target.c")
        cmakelists_text = clean_text(target_dir / "CMakeLists.txt")

        messages = []
        beeper = check_beeper_timer(h_clean, c_text)
        if beeper:
            messages.append(beeper)
        exti = check_gyro_exti_legacy(h_clean, c_text)
        if exti:
            messages.append(exti)
        messages.extend(check_at32_uart_tx(h_clean, cmakelists_text))

        if messages:
            total_findings += len(messages)
            print(f"\n{target_dir.name}:")
            for m in messages:
                print(f"  [CERTAIN] {m}")

    print()
    if total_findings == 0:
        print(f"No target-invariant findings ({len(targets)} target(s) checked).")
    else:
        print(f"{total_findings} finding(s) across {len(targets)} target(s) checked.")


if __name__ == "__main__":
    main()
