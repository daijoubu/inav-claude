#!/usr/bin/env python3
"""Classify DMA_STREAM_COLLISION hazards by severity.

Firmware ownership model (confirmed in timer_impl_stdperiph.c +
pwm_mapping.c:pwmInitMotors): motors are initialized strictly in position
order (idx = 0..motorCount-1); the FIRST entry to reach a shared DMA
descriptor claims it (dmaInit -> owner = OWNER_TIMER); every later entry
resolving to the same (dma,stream) tuple hits `owner != OWNER_FREE` and
silently fails to configure. So within one collision group, the LOWEST
position always wins and stays alive; every OTHER (higher) position in the
group is a loser and goes dead.

Severity is therefore about the losers, not the group as a whole:
  CERTAIN - the second-lowest position in the group (the best-case loser)
            is < 4, i.e. an S1-S4 output actually goes dead.
  NOTICE  - all losers are at position >= 4; the S1-S4 member of the group
            (if any) is the winner and keeps working fine.

On USE_DSHOT_DMAR targets, simulate_pwm_roles.py additionally emits
BURST_STREAM_COLLISION instead of (or alongside) DMA_STREAM_COLLISION for
groups affected by burst mode's per-PHYSICAL-TIMER (not per-channel) DMA
claim -- see that script's module docstring for the full model. This
script treats both hazard types identically for severity purposes (same
"loser position < 4" rule, same winner-always-lower-position guarantee),
since simulate_pwm_roles.py's BURST_STREAM_COLLISION text embeds the same
"TIM_CH" substrings this script matches positions against.

Usage: python3 classify_collisions.py <inav-checkout-root> <targets-file>
<targets-file> lists one target name per line, F4/F7/AT32 only. Build it
with simulate_pwm_roles.detect_family() in ("F4","F7","AT32") to exclude
H7 (out of scope -- separate hazard model, handled by check_dma_conflicts.py).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import simulate_pwm_roles as sim  # noqa: E402

ROOT = Path(sys.argv[1])
TARGETS_FILE = Path(sys.argv[2])

def classify(target_name):
    target_dir = ROOT / "src" / "main" / "target" / target_name
    target_c = target_dir / "target.c"
    target_h = target_dir / "target.h"
    cmake = target_dir / "CMakeLists.txt"
    if not target_c.is_file() or not cmake.is_file():
        return None
    family = sim.detect_family(cmake.read_text(errors="ignore"))
    if family is None:
        return None
    entries = sim.parse_target_c(target_c.read_text(errors="ignore"))
    if not entries:
        return None
    adc_pins, led_strip, dshot_dmar = (set(), False, False)
    if target_h.is_file():
        adc_pins, led_strip, dshot_dmar = sim.parse_target_h(target_h.read_text(errors="ignore"))
    dma_resolver = sim.DmaResolver(family, target_dir,
                                    target_h.read_text(errors="ignore") if target_h.is_file() else "",
                                    dshot_dmar)

    max_mc = max(12, len(entries))
    worst = None  # None, "NOTICE", or "CERTAIN"
    detail = []
    for mc in range(4, max_mc + 1):
        result = sim.simulate(entries, mc, None, adc_pins, led_strip, dma_resolver, True, {})
        for h in result.hazards:
            if not (h.startswith("DMA_STREAM_COLLISION") or h.startswith("BURST_STREAM_COLLISION")):
                continue
            positions = {}
            for row in result.rows:
                e = row["entry"]
                if row["claims_dma"]:
                    positions[f"{e.tim}_{e.ch}"] = row["position"]
            involved = sorted((pos, tim_ch) for tim_ch, pos in positions.items() if tim_ch in h and pos is not None)
            if len(involved) < 2:
                continue  # need at least a winner + a loser to say anything
            losers = involved[1:]  # everything but the lowest position (the winner)
            worst_loser_pos = losers[0][0]  # best-case loser = lowest among losers
            sev = "CERTAIN" if worst_loser_pos < 4 else "NOTICE"
            if sev == "CERTAIN":
                worst = "CERTAIN"
            elif worst is None:
                worst = "NOTICE"
            detail.append((mc, sev, involved, dshot_dmar))
    return worst, detail, dshot_dmar

def main():
    certain, notice = [], []
    for line in TARGETS_FILE.read_text().splitlines():
        t = line.strip()
        if not t:
            continue
        try:
            res = classify(t)
        except Exception as ex:
            print(f"ERROR {t}: {ex}", file=sys.stderr)
            continue
        if res is None:
            continue
        worst, detail, dshot_dmar = res
        if worst == "CERTAIN":
            first = next(d for d in detail if d[1] == "CERTAIN")
            certain.append((t, first[0], first[2], dshot_dmar))
        elif worst == "NOTICE":
            first = detail[0]
            notice.append((t, first[0], first[2], dshot_dmar))

    def fmt(pairs):
        return ",".join(f"{tc}@pos{p}" for p, tc in pairs)

    print(f"=== CERTAIN (a loser sits at position < 4 -- a basic-quad output actually goes dead): {len(certain)} targets ===")
    for t, mc, pairs, dmar in certain:
        print(f"  {t}  (first at motorCount={mc})  {fmt(pairs)}{'  [USE_DSHOT_DMAR]' if dmar else ''}")
    print(f"\n=== NOTICE (all losers at position >= 4; any S1-S4 member wins and stays alive): {len(notice)} targets ===")
    for t, mc, pairs, dmar in notice:
        print(f"  {t}  (first at motorCount={mc})  {fmt(pairs)}{'  [USE_DSHOT_DMAR]' if dmar else ''}")

if __name__ == "__main__":
    main()
