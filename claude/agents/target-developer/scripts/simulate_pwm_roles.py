#!/usr/bin/env python3
"""
simulate_pwm_roles.py -- deterministic simulation of INAV's motor/servo timer
role-resolution algorithm (pwmClaimTimer / pwmEnsureEnoughtMotors /
pwmBuildTimerOutputList in drivers/pwm_mapping.c), plus the DMA availability
and DMA-stream-collision checks that ride on top of it.

WHY THIS EXISTS
================
The role-resolution algorithm is genuinely hard to hand-trace correctly, and
getting it wrong has real consequences: pwmClaimTimer() unconditionally
overwrites usageFlags on EVERY timerHardware[] entry sharing a physical
timer, so a channel's OWN declared usage flag (TIM_USE_SERVO,
TIM_USE_OUTPUT_AUTO, ...) does NOT protect it from being forced into MOTOR
or SERVO role by a sibling channel on the same physical timer -- the final
role is decided by array declaration order + the mixer's live motor count
(getMotorCount(), NOT a target.h setting) + which channels share a timer.
This script was written after a session hand-traced this algorithm for
DAKEFPVF405WING and got it wrong on a late verification pass, having gotten
it wrong once already earlier in the same session -- see the
target-developer README's lessons for the incident. A deterministic port of
the actual C algorithm is the only reliable way to answer "what role does
output N resolve to at motor count M", and this script is that port.

Two additional hazards are checked, both invisible at compile time and at
boot:

1. SILENT_DEAD_MOTOR -- a channel that resolves to MOTOR and is genuinely
   initialized this build (its position within the resolved motor list is
   < the configured motor count) can still have NO DMA request line at all
   for that specific (timer, channel) pair on this MCU (e.g. TIM12 on
   STM32F405 -- see DEF_TIM_DMA__BTCH_TIM12_CH1/CH2 = NONE in
   timer_def_stm32f4xx.h). motorConfigDshot() silently fails to arm DMA in
   this case, but pwmMotorConfig()/pwmMotorAndServoInit() still report
   success -- see drivers/pwm_output.c. The motor output is dead, but
   nothing in the boot log or OSD says so.

2. DMA_STREAM_COLLISION -- two channels that both actually claim a DMA
   stream (i.e. both are genuinely initialized this build, not just
   sitting in the resolved-but-uninitialized tail of the motor/servo list)
   and whose only available DMA option resolves to the same
   (DMA controller, stream) pair will silently fight over that stream --
   whichever initializes last wins, the other's DSHOT/LED output just never
   works. Only entries that ACTUALLY claim DMA count for this check: pure
   SERVO-resolved channels never touch DMA at all (pwm_output.c only calls
   timerPWMConfigChannelDMA/DMABurst from the DSHOT motor path), and a
   MOTOR-resolved channel whose bucket position is >= the configured motor
   count is never initialized either, so it can't collide with anything.
   Under USE_DSHOT_DMAR this per-channel model is WRONG for motor-vs-motor
   groups sharing one physical timer -- see BURST_STREAM_COLLISION below,
   which supersedes it for that specific case; DMA_STREAM_COLLISION is
   still correct and still reported for a DMAR target's LED-vs-motor
   groups (LED strip never goes through the burst path) and for any group
   spanning >=2 distinct physical timers.

3. BURST_STREAM_COLLISION (USE_DSHOT_DMAR targets only) -- burst mode
   (impl_timerPWMConfigDMABurst(), timer_impl_stdperiph.c) claims one DMA
   stream per PHYSICAL TIMER, not per channel: `tch->timCtx->dmaBurstRef`
   lives on the timer-shared context (timCtx is one struct shared by all 4
   channels of a timer -- timer.c timerGetTCH()), so only the first
   channel of a timer to run (in pwmInitMotors()'s strict position order)
   ever calls dmaGetByTag()/does a real DMA_Init using ITS OWN
   dmavar-resolved stream; every later channel of the SAME timer sees
   dmaBurstRef already set and rides along for free, never touching its
   own dmavar at all. Consequences that invalidate a naive per-channel
   DMA_STREAM_COLLISION scan under DMAR:
     - Multiple channels of ONE physical timer resolving (by their own,
       individually-considered dmavar) to the same shared "combined
       request line" stream -- the classic F4/F7 TIM1/TIM8 CH1/CH2/CH3
       pattern SHARED_TIMER_DMA_REQUEST already flags for the non-burst
       case -- is NOT a bug under DMAR: that sharing is the whole point of
       burst mode. This script drops these from DMA_STREAM_COLLISION
       (see the dshot_dmar branch there) and does not flag them at all.
     - A cross-timer collision is real, but its blast radius and even
       which channel actually fails can differ from the naive model: if
       timer A's first channel locks in a stream before timer B's first
       channel is reached, and B's first channel's OWN dmavar resolves to
       that same stream, B's first channel fails (not necessarily whatever
       channel the naive grouping happened to flag) -- and per-timer
       retry means a LATER channel of B might still succeed with a
       different dmavar, so "the whole timer is dead" is not guaranteed
       either. This script walks the real per-timer/per-channel ownership
       cascade (see the BURST_STREAM_COLLISION block in simulate()) rather
       than grouping by final resolved stream, to get the winner/loser and
       blast radius right.
   Severity (CERTAIN/NOTICE) uses the same "loser position < 4" rule as
   DMA_STREAM_COLLISION (classify_collisions.py), since by construction
   the walk processes strictly ascending position and only reports a
   channel that actually, individually failed its own attempt.

WHAT THIS SCRIPT DOES NOT MODEL (documented limitations, not bugs)
====================================================================
- checkPwmTimerConflicts()'s UART/softserial pin-sharing skip is gated on
  the LIVE runtime serial port configuration (doesConfigurationUsePort(),
  feature(FEATURE_SOFTSERIAL)), not anything visible in target.c/target.h.
  This is not statically knowable from a target checkout, so it is not
  modeled -- a channel that happens to double as an in-use UART TX/RX pin
  will be reported as available for motor/servo role assignment even though
  a live UART on that port would make pwm_mapping.c skip it entirely.
- checkPwmTimerConflicts()'s LED-strip-shares-timer skip (any OTHER channel
  on the same physical timer as a TIM_USE_LED entry gets permanently
  excluded from role assignment whenever FEATURE_LED_STRIP is active) IS
  modeled, but conservatively: it's treated as active whenever target.h
  defines USE_LED_STRIP at all, regardless of whether FEATURE_LED_STRIP is
  actually in DEFAULT_FEATURES. This matches check_dma_conflicts.py's
  existing convention for the same reason -- LED strip is commonly toggled
  on by users regardless of shipped default, so treating it as "always
  potentially active" is the safe assumption for hazard-finding. Pass
  --no-led-strip to disable this if you specifically want the
  LED-strip-off picture.
- (RESOLVED, see below) timerOverrides()/CLI `timer_output_mode` per-timer
  runtime overrides ARE modeled via --timer-output-mode, added specifically
  to answer whether forcing a shared-channel timer (e.g. TIM3, whose two
  channels S2/S3 on DAKEFPVF405WING cannot be split -- pwmClaimTimer()
  force-syncs usageFlags across every timerHardware[] entry on one physical
  timer) to OUTPUT_MODE_SERVOS keeps BOTH its channels out of the MOTOR
  bucket entirely (and therefore off DMA) even though the mixer's live
  motor count would otherwise have pulled the first channel in. Without
  --timer-output-mode, default is OUTPUT_MODE_AUTO for every timer (no
  override), matching a freshly flashed board. IMPORTANT history: prior to
  the fix-pwm-motor-double-counting fix (2026-08-17, release/9.1), pass 1 of
  pwmEnsureEnoughtMotors() had NO guard (unlike pass 2's explicit
  `!TIM_IS_MOTOR_ONLY(...)` check) against re-visiting a sibling on the same
  physical timer that an earlier pwmClaimTimer() broadcast had already
  promoted -- timerHardwareOverride() runs INSIDE pass 1, per-entry, lazily
  as the loop reaches each index, so the first channel of a timer forced to
  OUTPUT_MODE_MOTORS (or a target.c-declared motor-only group of 2+ channels)
  would count itself AND its siblings via the claim's return value, and then
  each sibling would independently re-satisfy TIM_IS_MOTOR_ONLY on its own
  turn later in the same pass and get counted again -- an n-channel group
  inflated motorOnlyOutputs by 2n-1 instead of n, which could silently demote
  a LATER (in declaration order) unrelated AUTO output from MOTOR to SERVO.
  The fix adds a per-physical-timer `timerCounted[]` dedup guard to pass 1
  (mirrored here as `counted_timers`, see pwm_ensure_enough_motors()) so each
  physical timer's motor-only group is only ever counted once, regardless of
  how many of its channels are compile-time-declared vs. override-forced.
  This script now models the FIXED algorithm unconditionally -- there is no
  flag to reproduce the old buggy counting; see git history if you need it.
- DSHOT vs plain PWM/Oneshot/Multishot motor protocol is a runtime
  motor_pwm_protocol CLI setting, not a target.c/target.h fact. This script
  defaults to assuming DSHOT (by far the common case, and the case the
  SILENT_DEAD_MOTOR/DMA_STREAM_COLLISION hazards are about -- plain PWM
  motors never touch DMA at all) -- pass --no-dshot to model a plain-PWM
  motor build instead, which suppresses both hazard classes for the motor
  bucket (LED still claims DMA either way, since led_strip.c always uses
  DMA when active).
- ADC's *conflict* check (checkPwmTimerConflicts skipping any timer pin
  that's also wired to an ADC_CHANNEL_n_PIN) IS modeled, since that one is
  fully static (gated only on USE_ADC being compiled, not a runtime
  feature() bit). ADC's *own* DMA stream (STM32H7 only, hardwired in
  adc_stm32h7xx.c, not read from target.h) is also modeled by reusing
  check_dma_conflicts.py's ADC_RESERVED_DMAOPT table.
- Servo count: pwmInitServos() only initializes the first
  min(servoCount, maxTimServoCount) entries of the resolved servo bucket,
  exactly mirroring the motor count truncation. This script accepts an
  optional --servo-count; if omitted, every resolved-SERVO entry is treated
  as "driven" (i.e. assumes the mixer wants at least as many servos as the
  target exposes) since under-provisioning servos is a far less common
  real-world gotcha than the motor case this script was built to catch.

MCU FAMILY SUPPORT
===================
F4/F7/AT32 share one DMA addressing scheme: DEF_TIM_DMA__BTCH_<TIM>_<CH> in
the family's timer_def_*.h expands to either NONE or a comma list of
D(dma,stream,channel) tuples, and target.c's DEF_TIM(...) trailing numeric
arg ("dmavar") is a 0-based index into that list. AT32 additionally has a
DMAMUX indirection (DEF_TIM_DMA_FULL -- 14 interchangeable options, same
list for nearly every channel) which is resolved the same way; per the
target-developer lessons, AT32 conflict analysis really just becomes "did
two entries pick the same literal dmavar index", since the list itself
doesn't distinguish channels.

H7 uses a different, flatter scheme (already implemented by
check_dma_conflicts.py, imported here rather than re-implemented): dmaopt
is a flat 0-15 index directly addressing DMA1 Stream0-7 / DMA2 Stream0-7,
with a fixed small set of (timer, channel) pairs that have NO DMA request
line at all (NO_DMA_CHANNELS) plus the USE_DSHOT_DMAR-conditional TIM4_CH4
special case.

Usage
=====
  ./simulate_pwm_roles.py <inav_root> --target NAME --motor-count N
      Print the fully resolved per-output table for exactly this motor
      count: bucket (MOTOR/SERVO/LED/none), position within that bucket,
      whether it's actually driven this build, whether it claims DMA, and
      which (controller, stream) it claims if so.

  ./simulate_pwm_roles.py <inav_root> --target NAME
  ./simulate_pwm_roles.py <inav_root> --target NAME --sweep 1:8
      Sweep every motor count in range (default: 1..total DEF_TIM entries)
      and report only the hazards found at each count -- this is the "find
      the safe motorCount values" mode that motivated this script.

  ./simulate_pwm_roles.py --selftest <inav_root>
      Run the built-in regression cases (see SELFTEST_CASES below) and
      print PASS/FAIL. Run this after touching the simulation logic.

Options:
  --servo-count N   cap the servo bucket the same way --motor-count caps
                     the motor bucket (default: unlimited, see above)
  --no-dshot         assume plain PWM/Oneshot/Multishot motors (suppresses
                     motor-side DMA hazards; LED still claims DMA)
  --no-led-strip     assume FEATURE_LED_STRIP is never enabled, even though
                     USE_LED_STRIP is compiled in (see limitations above)
  --timer-output-mode TIMn=MODE
                     Simulate a timerOverridesMutable(timer2id(TIMn))
                     ->outputMode = OUTPUT_MODE_MODE override (as set via
                     CLI `timer_output_mode` or in a target's config.c),
                     WITHOUT editing any file on disk. MODE is one of AUTO,
                     MOTORS, SERVOS, LED. Repeatable, e.g.
                     --timer-output-mode TIM3=SERVOS. TIMn must match a
                     `tim` token used in this target's DEF_TIM(...) entries
                     (e.g. TIM3, TIM8) -- every entry on that physical timer
                     is affected identically, matching pwmClaimTimer()'s
                     force-sync behavior. See the "not modeled" section
                     above for the pass-1 double-counting caveat this
                     interacts with when MODE=MOTORS on a multi-channel
                     timer.
  --verbose          show the full per-output table even in --sweep mode
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_dma_conflicts as _h7  # reuse NO_DMA_CHANNELS / ADC_RESERVED_DMAOPT

# ---------------------------------------------------------------------------
# usage-flag bit values, copied from drivers/timer.h
# ---------------------------------------------------------------------------
TIM_USE_ANY = 0
TIM_USE_PPM = 1 << 0
TIM_USE_PWM = 1 << 1
TIM_USE_MOTOR = 1 << 2
TIM_USE_SERVO = 1 << 3
TIM_USE_MC_CHNFW = 1 << 4  # deprecated, never set by any live target
TIM_USE_LED = 1 << 24
TIM_USE_BEEPER = 1 << 25
TIM_USE_OUTPUT_AUTO = TIM_USE_MOTOR | TIM_USE_SERVO

USAGE_TOKENS = {
    "TIM_USE_ANY": TIM_USE_ANY,
    "TIM_USE_PPM": TIM_USE_PPM,
    "TIM_USE_PWM": TIM_USE_PWM,
    "TIM_USE_MOTOR": TIM_USE_MOTOR,
    "TIM_USE_SERVO": TIM_USE_SERVO,
    "TIM_USE_MC_CHNFW": TIM_USE_MC_CHNFW,
    "TIM_USE_LED": TIM_USE_LED,
    "TIM_USE_BEEPER": TIM_USE_BEEPER,
    "TIM_USE_OUTPUT_AUTO": TIM_USE_OUTPUT_AUTO,
}


def is_motor(flags):
    return bool(flags & TIM_USE_MOTOR)


def is_servo(flags):
    return bool(flags & TIM_USE_SERVO)


def is_led(flags):
    return bool(flags & TIM_USE_LED)


def is_motor_only(flags):
    return is_motor(flags) and not is_servo(flags)


# ---------------------------------------------------------------------------
# timer_output_mode overrides (timerHardwareOverride() in pwm_mapping.c) --
# a per-PHYSICAL-TIMER runtime override (CLI `timer_output_mode` / a
# target's config.c timerOverridesMutable(...)->outputMode), applied to
# EVERY timerHardware[] entry on that timer identically, regardless of that
# entry's own declared usage flags. OUTPUT_MODE_AUTO (the default, value 0)
# is a deliberate no-op -- see the switch in timerHardwareOverride() itself,
# which has no `case OUTPUT_MODE_AUTO`.
# ---------------------------------------------------------------------------
OUTPUT_MODE_TOKENS = ("AUTO", "MOTORS", "SERVOS", "LED")


def apply_timer_output_mode_override(entry, mode):
    """Mirrors timerHardwareOverride() in pwm_mapping.c exactly, including
    leaving flags untouched for AUTO/None (no case in the real switch)."""
    if not mode or mode == "AUTO":
        return
    if mode == "MOTORS":
        entry.flags &= ~(TIM_USE_SERVO | TIM_USE_LED)
        entry.flags |= TIM_USE_MOTOR
    elif mode == "SERVOS":
        entry.flags &= ~(TIM_USE_MOTOR | TIM_USE_LED)
        entry.flags |= TIM_USE_SERVO
    elif mode == "LED":
        entry.flags &= ~(TIM_USE_MOTOR | TIM_USE_SERVO)
        entry.flags |= TIM_USE_LED


def parse_usage(usage_text, warn_prefix=""):
    flags = 0
    for tok in usage_text.split("|"):
        tok = tok.strip()
        if not tok:
            continue
        if tok not in USAGE_TOKENS:
            print(f"{warn_prefix}warning: unknown usage token {tok!r}, treating as 0",
                  file=sys.stderr)
            continue
        flags |= USAGE_TOKENS[tok]
    return flags


# ---------------------------------------------------------------------------
# target.c parsing
# ---------------------------------------------------------------------------
DEF_TIM_RE = re.compile(
    r'DEF_TIM\(\s*([A-Za-z0-9_]+)\s*,\s*([A-Za-z0-9_]+)\s*,\s*([A-Za-z0-9_]+)\s*,'
    r'\s*([^,]+?)\s*,\s*([^,]+?)\s*,\s*(\d+)\s*\)'
)
COMMENT_RE = re.compile(r'//\s*(.+?)\s*$')


class Entry:
    __slots__ = ("index", "tim", "ch", "pin", "flags", "orig_flags", "dmavar",
                 "label", "line")

    def __init__(self, index, tim, ch, pin, flags, dmavar, label, line):
        self.index = index
        self.tim = tim
        self.ch = ch
        self.pin = pin
        self.flags = flags
        self.orig_flags = flags
        self.dmavar = dmavar
        self.label = label
        self.line = line

    def usage_str(self):
        parts = []
        if self.flags & TIM_USE_MOTOR:
            parts.append("MOTOR")
        if self.flags & TIM_USE_SERVO:
            parts.append("SERVO")
        if self.flags & TIM_USE_LED:
            parts.append("LED")
        if self.flags & TIM_USE_BEEPER:
            parts.append("BEEPER")
        if self.flags & TIM_USE_PWM:
            parts.append("PWM")
        if self.flags & TIM_USE_PPM:
            parts.append("PPM")
        return "|".join(parts) if parts else "ANY(0)"

    def __repr__(self):
        return f"{self.tim}_{self.ch}({self.label})"


def parse_target_c(text):
    entries = []
    for i, line in enumerate(text.splitlines()):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        m = DEF_TIM_RE.search(line)
        if not m:
            continue
        tim, ch, pin, usage_text, _flags_field, dmavar = m.groups()
        cm = COMMENT_RE.search(line)
        if cm:
            # Comments are often "S4 - long explanation ..." -- take just the
            # leading token (the S-number / short name) as the label so
            # tables stay compact; the full comment is still in entry.line.
            label = cm.group(1).split()[0].rstrip(",;")
        else:
            label = f"{tim}_{ch}"
        flags = parse_usage(usage_text, warn_prefix=f"line {i+1}: ")
        entries.append(Entry(len(entries), tim, ch, pin, flags, int(dmavar),
                              label, stripped))
    return entries


def apply_dmavar_overrides(entries, overrides):
    """Mutate entries in place, setting entry.dmavar for each label in
    `overrides` (a dict of label -> new dmavar int). Raises SystemExit if a
    label doesn't match any parsed entry, so a typo'd --dmavar-override
    fails loudly instead of silently simulating the unmodified board.
    Returns the list of (label, old, new) changes actually applied, in
    override-argument order, for print-back/audit purposes."""
    by_label = {e.label: e for e in entries}
    applied = []
    for label, new_val in overrides.items():
        if label not in by_label:
            known = ", ".join(sorted(by_label))
            raise SystemExit(
                f"--dmavar-override: no DEF_TIM entry labeled {label!r}. "
                f"Known labels: {known}"
            )
        e = by_label[label]
        applied.append((label, e.dmavar, new_val))
        e.dmavar = new_val
    return applied


def clone_entries(entries):
    out = []
    for e in entries:
        ne = Entry(e.index, e.tim, e.ch, e.pin, e.orig_flags, e.dmavar, e.label, e.line)
        out.append(ne)
    return out


# ---------------------------------------------------------------------------
# target.h parsing (ADC conflict pins + USE_LED_STRIP + USE_DSHOT_DMAR + family)
# ---------------------------------------------------------------------------
ADC_PIN_RE = re.compile(r'^\s*#\s*define\s+ADC_CHANNEL_\d+_PIN\s+(\w+)', re.M)


def parse_target_h(text):
    adc_pins = set()
    if "USE_ADC" in text:
        adc_pins = set(ADC_PIN_RE.findall(text))
    led_strip = "USE_LED_STRIP" in text
    dshot_dmar = "USE_DSHOT_DMAR" in text
    return adc_pins, led_strip, dshot_dmar


FAMILY_RE = {
    "F4": re.compile(r'target_stm32f4\w*\('),
    "F7": re.compile(r'target_stm32f7\w*\('),
    "H7": re.compile(r'target_stm32h7\w*\('),
    "AT32": re.compile(r'target_at32f43x\w*\(', re.IGNORECASE),
}


def detect_family(cmake_text):
    for family, rx in FAMILY_RE.items():
        if rx.search(cmake_text):
            return family
    return None


# ---------------------------------------------------------------------------
# DMA option tables, F4/F7/AT32 (list-of-options addressed by dmavar index)
# ---------------------------------------------------------------------------
BTCH_DEFINE_RE = re.compile(
    r'#\s*define\s+(DEF_TIM_DMA__BTCH_[A-Za-z0-9]+_(?:CH\d N?|CH\dN|CH\d))\s+(.+)'
)
# The channel-suffix alternation above is fiddly to get exactly right with
# regex; simpler and robust: just capture the macro name greedily up to
# whitespace, then split off the CH-suffix separately.
BTCH_DEFINE_RE = re.compile(r'#\s*define\s+(DEF_TIM_DMA__BTCH_\S+)\s+(.+)')
DMA_FULL_RE = re.compile(r'#\s*define\s+(DEF_TIM_DMA_FULL)\s+(.+)')
D_TUPLE_RE = re.compile(r'D\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)')


def load_option_table(header_text):
    """Returns {(TIM, CH): [(dma, stream, chan), ...]} for F4/F7/AT32-style
    headers. Empty list means NONE (no DMA request line at all)."""
    collapsed = re.sub(r'\\\r?\n', ' ', header_text)
    macros = {}
    for m in BTCH_DEFINE_RE.finditer(collapsed):
        name, body = m.group(1), m.group(2)
        body = body.split("//")[0].strip()
        macros[name] = body
    full_m = DMA_FULL_RE.search(collapsed)
    full_body = full_m.group(2).split("//")[0].strip() if full_m else ""

    table = {}
    for name, body in macros.items():
        if body == "DEF_TIM_DMA_FULL":
            body = full_body
        if body == "NONE":
            options = []
        else:
            options = [(int(d), int(s), int(c)) for d, s, c in D_TUPLE_RE.findall(body)]
        # name looks like DEF_TIM_DMA__BTCH_TIM3_CH4 or ..._BTCH_TMR3_CH4
        rest = name[len("DEF_TIM_DMA__BTCH_"):]
        # split off trailing _CHx / _CHxN / _UP
        cm = re.match(r'(.+)_(CH\d N?|CH\d|UP)$', rest)
        cm = re.match(r'(.+)_(CH\dN?|UP)$', rest)
        if not cm:
            continue
        tim_tok, ch_tok = cm.group(1), cm.group(2)
        table[(tim_tok, ch_tok)] = options
    return table


def stream_label_f4(dma, stream):
    return f"DMA{dma} Stream{stream}"


# ---------------------------------------------------------------------------
# H7: flat dmaopt addressing (delegates to check_dma_conflicts.py's tables)
# ---------------------------------------------------------------------------
def h7_dma_options(tim_tok, ch_tok, dmaopt, dshot_dmar):
    if (tim_tok, ch_tok) == ("TIM4", "CH4"):
        if not dshot_dmar:
            return []
    elif (tim_tok, ch_tok) in _h7.NO_DMA_CHANNELS:
        return []
    dma = 1 if dmaopt < 8 else 2
    stream = dmaopt if dmaopt < 8 else dmaopt - 8
    return [(dma, stream, 0)]


def stream_label_h7(dma, stream):
    return _h7.stream_label(stream + (0 if dma == 1 else 8))


# ---------------------------------------------------------------------------
# DMA resolver: given family + entry, return list of (dma,stream,chan)
# options and which one dmavar actually picks (or None if index invalid /
# channel has no DMA at all).
# ---------------------------------------------------------------------------
class DmaResolver:
    def __init__(self, family, target_dir, target_h_text, dshot_dmar):
        self.family = family
        self.dshot_dmar = dshot_dmar
        self.table = None
        if family in ("F4", "F7", "AT32"):
            header_name = {
                "F4": "timer_def_stm32f4xx.h",
                "F7": "timer_def_stm32f7xx.h",
                "AT32": "timer_def_at32f43x.h",
            }[family]
            header_path = target_dir.parents[1] / "drivers" / header_name
            self.table = load_option_table(header_path.read_text(errors="ignore"))

    def _lookup(self, tim, ch):
        """F4/F7/AT32 option-list lookup, with the CHxN -> CHx alias that
        timer_def.h applies before the DEF_TIM_DMA__ prefix is concatenated
        on (see BTCH_TIM1_CH1N -> BTCH_TIM1_CH1 etc there): an N-channel
        (complementary output, e.g. TIM1_CH1N) shares its base channel's DMA
        request line, since DMA is driven by the timer's compare-match event
        which is the same for CHx and CHxN. Returns None if truly not found
        after trying both the exact key and its de-N'd fallback."""
        if (tim, ch) in self.table:
            return self.table[(tim, ch)]
        if ch.endswith("N") and (tim, ch[:-1]) in self.table:
            return self.table[(tim, ch[:-1])]
        return None

    def options_for(self, entry):
        """Returns list of (dma, stream, chan) options for this entry's
        (tim, ch); empty list means no DMA request line exists at all."""
        if self.family == "H7":
            return h7_dma_options(entry.tim, entry.ch, entry.dmavar, self.dshot_dmar)
        return self._lookup(entry.tim, entry.ch)  # None = unknown (tim/ch not found)

    def claimed_stream(self, entry):
        """Returns (dma, stream) the entry actually claims given its dmavar,
        or None if it has no DMA at all. Returns ('?', dmavar) sentinel if
        the (tim,ch) pair wasn't found in the header table (parser gap --
        report, don't silently treat as safe)."""
        if self.family == "H7":
            opts = h7_dma_options(entry.tim, entry.ch, entry.dmavar, self.dshot_dmar)
            return (opts[0][0], opts[0][1]) if opts else None
        opts = self._lookup(entry.tim, entry.ch)
        if opts is None:
            return ("?", entry.dmavar)  # unknown channel -- flagged separately
        if not opts:
            return None
        if entry.dmavar >= len(opts):
            return ("?", entry.dmavar)  # dmavar out of range -- shouldn't happen
        d, s, _c = opts[entry.dmavar]
        return (d, s)

    def stream_label(self, dma, stream):
        if dma == "?":
            return f"<unresolved dmavar={stream}>"
        if self.family == "H7":
            return stream_label_h7(dma, stream)
        return stream_label_f4(dma, stream)

    def is_shared_multichannel_request(self, entry):
        """True if this entry's chosen dmavar resolves to a (dma,stream,chan)
        tuple that is ALSO listed as an option for a DIFFERENT channel of the
        same physical timer. That exact-tuple-reuse is the generic fingerprint
        of an F4-family "combined" DMA request line -- e.g. DMA2 Stream6
        channel 0 is listed as an option for TIM1_CH1, TIM1_CH2, AND TIM1_CH3
        alike (DEF_TIM_DMA__BTCH_TIM1_CH1/CH2/CH3 in timer_def_stm32f4xx.h all
        include D(2,6,0)). Firing that request only tells the DMA controller
        "one of this timer's channels compare-matched", not which one, so it
        is not a valid substitute for a real per-channel CCx DMA request
        unless the timer is driven in USE_DSHOT_DMAR burst mode (which reads
        all channels' CCRs together off the timer's *update* event instead,
        a completely different mechanism). Confirmed via upstream commit
        ab07785fa9 ("Fix channel selection for DMA2 Stream6"), which changed
        exactly this -- TIM1_CH3 dmavar 0 -> 1 -- on 4 real boards
        (DALRCF405, FLYWOOF411, HAKRCF405V2, HAKRCF722V2) after the dmavar=0
        option produced no signal. Only meaningful for F4/F7/AT32 (self.table
        is None on H7, which has no such shared-request-line quirk)."""
        if self.table is None:
            return False
        if self.family == "AT32":
            # AT32F435 is DMAMUX-based: DEF_TIM_DMA__BTCH_* for every single
            # channel of every timer expands to the literal same macro
            # (DEF_TIM_DMA_FULL, a ~14-entry list of generic DMAMUX channel
            # numbers -- see timer_def_at32f43x.h). Since that identical list
            # is repeated verbatim for every (tim,ch), "this tuple also
            # appears in a sibling channel's list" is true for nearly any
            # dmavar and carries no meaning -- there is no F4-style
            # hardwired "combined CH1/CH2/CH3 request line" concept on a
            # DMAMUX part; each DMA channel's request source is independently
            # muxed. Real AT32 conflict analysis is "too many concurrent
            # users of the 14 DMAMUX channels", not this.
            return False
        opts = self._lookup(entry.tim, entry.ch)
        if not opts or entry.dmavar >= len(opts):
            return False
        chosen = opts[entry.dmavar]
        # Restrict to channel-selector 0: that's the specific slot F4/F8-style
        # advanced-timer tables in this codebase consistently use for the
        # combined CH1/CH2/CH3 request (see TIM1_CH1/CH2/CH3 and
        # TIM8_CH1/CH2/CH3 in timer_def_stm32f4xx.h, all listing D(dma,stream,0)
        # as their FIRST/dmavar-0 option). Sibling channels can legitimately
        # share a physical (dma,stream,chan!=0) tuple as plain alternate
        # routing options (e.g. TIM2_CH2 and TIM2_CH4 both list D(1,6,3)) --
        # that's an ordinary DMA_STREAM_COLLISION risk only if BOTH are
        # actually chosen simultaneously, not this "unusable in isolation"
        # defect class, so don't flag chan!=0 here to avoid false positives.
        if chosen[2] != 0:
            return False
        for (tim_tok, ch_tok), other_opts in self.table.items():
            if tim_tok != entry.tim or ch_tok == entry.ch:
                continue
            if chosen in other_opts:
                return True
        return False


# ---------------------------------------------------------------------------
# Faithful port of pwm_mapping.c
# ---------------------------------------------------------------------------
def check_pwm_timer_conflicts(entry, entries, adc_pins, led_strip_active):
    if entry.pin in adc_pins:
        return True
    if led_strip_active:
        for e in entries:
            if e.tim == entry.tim and is_led(e.flags):
                return True
    return False


def pwm_claim_timer(entries, tim, usage_flags):
    changed = 0
    for e in entries:
        if e.tim == tim and e.flags != usage_flags:
            e.flags = usage_flags
            changed += 1
    return changed


def pwm_ensure_enough_motors(entries, motor_count, adc_pins, led_strip_active,
                              timer_output_modes=None):
    timer_output_modes = timer_output_modes or {}
    motor_only_outputs = 0
    # Fixed in pwm_mapping.c (fix-pwm-motor-double-counting, 2026-08-17): pass 1
    # now dedups per physical timer via a timerCounted[] guard, so a sibling
    # promoted by an earlier pwm_claim_timer() broadcast is not re-counted when
    # the loop later reaches its own index. Mirrored here with a plain set --
    # e.tim is a hashable per-physical-timer token, same role as the C fix's
    # timer2id(timHw->tim) index into timerCounted[].
    counted_timers = set()
    for e in entries:
        # timerHardwareOverride(): applied per-entry, lazily, exactly here --
        # BEFORE any sibling on the same physical timer has necessarily been
        # visited yet.
        apply_timer_output_mode_override(e, timer_output_modes.get(e.tim))
        if check_pwm_timer_conflicts(e, entries, adc_pins, led_strip_active):
            continue
        if is_motor_only(e.flags) and e.tim not in counted_timers:
            counted_timers.add(e.tim)
            motor_only_outputs += 1
            motor_only_outputs += pwm_claim_timer(entries, e.tim, e.flags)

    for e in entries:
        if check_pwm_timer_conflicts(e, entries, adc_pins, led_strip_active):
            continue
        if is_motor(e.flags) and not is_motor_only(e.flags):
            if motor_only_outputs < motor_count:
                e.flags = (e.flags & ~TIM_USE_SERVO) | TIM_USE_MOTOR
                motor_only_outputs += 1
                motor_only_outputs += pwm_claim_timer(entries, e.tim, e.flags)
            else:
                e.flags = e.flags & ~TIM_USE_MOTOR
                pwm_claim_timer(entries, e.tim, e.flags)


def pwm_build_timer_output_list(entries, motor_count, adc_pins, led_strip_active,
                                 timer_output_modes=None):
    pwm_ensure_enough_motors(entries, motor_count, adc_pins, led_strip_active,
                              timer_output_modes)

    motor_idx = 0
    tim_motors = []
    tim_servos = []
    bucket = {}       # entry.index -> "MOTOR" | "SERVO" | "LED" | None
    skipped = set()   # entry.index that hit checkPwmTimerConflicts here

    for e in entries:
        if check_pwm_timer_conflicts(e, entries, adc_pins, led_strip_active):
            skipped.add(e.index)
            continue

        if is_motor(e.flags) and motor_idx < motor_count:
            e.flags &= ~TIM_USE_SERVO
            pwm_claim_timer(entries, e.tim, e.flags)
            motor_idx += 1

        has_motor_on_tim = any(m.tim == e.tim for m in tim_motors)
        has_servo_on_tim = any(s.tim == e.tim for s in tim_servos)

        typ = None
        if is_servo(e.flags) and not has_motor_on_tim:
            typ = "SERVO"
        elif is_motor(e.flags) and not has_servo_on_tim:
            typ = "MOTOR"
        elif is_led(e.flags) and not has_motor_on_tim and not has_servo_on_tim:
            typ = "LED"

        if typ == "MOTOR":
            e.flags &= TIM_USE_MOTOR
            tim_motors.append(e)
            pwm_claim_timer(entries, e.tim, e.flags)
        elif typ == "SERVO":
            e.flags &= TIM_USE_SERVO
            tim_servos.append(e)
            pwm_claim_timer(entries, e.tim, e.flags)
        elif typ == "LED":
            e.flags &= TIM_USE_LED
            pwm_claim_timer(entries, e.tim, e.flags)

        bucket[e.index] = typ

    return tim_motors, tim_servos, bucket, skipped


class SimResult:
    def __init__(self):
        self.rows = []       # list of dicts, one per entry, in declaration order
        self.hazards = []    # list of strings


def simulate(entries_orig, motor_count, servo_count, adc_pins, led_strip_active,
             dma_resolver, dshot, timer_output_modes=None):
    entries = clone_entries(entries_orig)
    tim_motors, tim_servos, bucket, skipped = pwm_build_timer_output_list(
        entries, motor_count, adc_pins, led_strip_active, timer_output_modes)

    motor_pos = {e.index: i for i, e in enumerate(tim_motors)}
    servo_pos = {e.index: i for i, e in enumerate(tim_servos)}

    # LED strip is NOT driven through pwmBuildTimerOutputList's bucket system
    # at all -- light_ws2811strip.c's ws2811LedStripInit() does its own
    # timerGetByTag/timerGetByUsageFlag(TIM_USE_LED) lookup directly against
    # the ORIGINAL (as-declared) timerHardware[] entry, independent of
    # whatever pwm_mapping.c did with it. In fact checkPwmTimerConflicts()
    # makes the LED entry match itself (same tim, TIM_USE_LED flag) whenever
    # led_strip_active, so pwm_build_timer_output_list() always SKIPs it --
    # this is by design, not a modeling gap: it keeps pwm_mapping.c from also
    # handing that channel out as a servo/motor, while led_strip.c claims it
    # through its own separate path. So LED DMA-claim status is computed
    # here from the entry's ORIGINAL declared flags, not the resolved bucket.
    led_entry_indices = {e.index for e in entries_orig if e.orig_flags & TIM_USE_LED}

    result = SimResult()
    dma_claims = {}  # (dma,stream) -> list of entry describing string

    for e in entries:
        b = bucket.get(e.index)
        is_led_entry = e.index in led_entry_indices
        if is_led_entry and led_strip_active:
            b_display = "LED (own path in light_ws2811strip.c, bypasses pwm_mapping bucket)"
        elif e.index in skipped:
            b_display = "SKIPPED(ADC/LED-timer conflict)"
        elif b is None:
            b_display = "unclaimed"
        else:
            b_display = b

        driven = False
        pos = None
        if is_led_entry and led_strip_active:
            driven = True
        elif b == "MOTOR":
            pos = motor_pos[e.index]
            driven = pos < motor_count
        elif b == "SERVO":
            pos = servo_pos[e.index]
            driven = True if servo_count is None else pos < servo_count

        claims_dma = False
        stream = None
        no_dma_at_all = False
        if is_led_entry and led_strip_active:
            claims_dma = True
        elif driven and b == "MOTOR" and dshot:
            claims_dma = True

        if claims_dma:
            resolved = dma_resolver.claimed_stream(e)
            if resolved is None:
                no_dma_at_all = True
                claims_dma = False
            else:
                stream = resolved
                dma_claims.setdefault(resolved, []).append(e)

        row = {
            "entry": e, "bucket": b_display, "position": pos, "driven": driven,
            "claims_dma": claims_dma, "stream": stream, "no_dma_at_all": no_dma_at_all,
        }
        result.rows.append(row)

        if no_dma_at_all and b == "MOTOR" and driven and dshot:
            result.hazards.append(
                f"SILENT_DEAD_MOTOR: {e.tim}_{e.ch} ({e.label}) resolves to MOTOR "
                f"and IS initialized at motorCount={motor_count} (bucket position "
                f"{pos}), but this (timer,channel) has NO DMA request line at all "
                f"on this MCU -- motorConfigDshot() will silently fail to arm DMA "
                f"while pwmMotorConfig() still reports success. This output will "
                f"not spin under DSHOT despite no boot-time error."
            )

        if (claims_dma and b == "MOTOR" and driven and dshot
                and not dma_resolver.dshot_dmar
                and dma_resolver.is_shared_multichannel_request(e)):
            result.hazards.append(
                f"SHARED_TIMER_DMA_REQUEST: {e.tim}_{e.ch} ({e.label}) dmavar="
                f"{e.dmavar} resolves to a DMA request line ALSO shared with "
                f"another channel of {e.tim} (a combined multi-channel "
                f"compare-event request, not one dedicated to this channel). "
                f"Without USE_DSHOT_DMAR this typically means the DMA transfer "
                f"never fires specifically for this channel's own compare "
                f"events and the output stays silent even though "
                f"pwmMotorConfig() reports success -- see upstream commit "
                f"ab07785fa9 (\"Fix channel selection for DMA2 Stream6\"), "
                f"which hit exactly this on 4 real boards. Try a different "
                f"dmavar for this channel."
            )

    # DMA_STREAM_COLLISION (naive per-channel model): every entry's OWN
    # dmavar-resolved (dma,stream) is treated as an independent claim, and
    # any group of >=2 claimers on the same physical stream is a hazard.
    # This is CORRECT for the non-burst path (impl_timerPWMConfigChannelDMA
    # claims a stream per CHANNEL, timer_impl_stdperiph.c ~line 300) but
    # WRONG under USE_DSHOT_DMAR: impl_timerPWMConfigDMABurst() claims a
    # stream once per PHYSICAL TIMER (tch->timCtx->dmaBurstRef, where
    # timCtx is shared by all 4 channels of one timer -- see timer.c
    # timerGetTCH(), `timerCtx[timerIndex]->ch[0..3].timCtx = timerCtx[...]`).
    # Every claimer here reflects ITS OWN dmavar in isolation, but under
    # burst mode a channel only ever gets to make that real claim attempt
    # if it's the first channel of its physical timer still needing one
    # (dmaBurstRef unset) -- any later channel of a timer that already
    # locked in a stream rides along for free and never touches its own
    # dmavar at all, so grouping by "final resolved stream" over-counts:
    # a same-timer group is (almost always) the intended combined-request
    # sharing, not a bug, and even a cross-timer group can be a false
    # positive if the earlier-processed timer's OWN winning channel isn't
    # the one this naive grouping happened to pick. So under dshot_dmar we
    # suppress ALL-motor groups entirely here and let the BURST_STREAM_
    # COLLISION walk below (which faithfully replays the per-timer/
    # per-channel ownership cascade) be authoritative instead. We keep
    # flagging DMA_STREAM_COLLISION for any group that still includes a
    # non-motor claimer (LED strip, which never goes through the burst
    # path -- light_ws2811strip.c does its own DMA config, so LED-vs-motor
    # collisions are unaffected by DMAR and still modeled correctly here).
    for stream, claimers in dma_claims.items():
        if len(claimers) < 2:
            continue
        if dma_resolver.dshot_dmar:
            all_motor = all(bucket.get(c.index) == "MOTOR" for c in claimers)
            if all_motor:
                continue  # handled by the BURST_STREAM_COLLISION walk instead
        dma, s = stream
        label = dma_resolver.stream_label(dma, s)
        names = ", ".join(f"{c.tim}_{c.ch}({c.label})" for c in claimers)
        result.hazards.append(
            f"DMA_STREAM_COLLISION: {label} claimed by {len(claimers)} live DMA "
            f"users at motorCount={motor_count}: {names} -- whichever initializes "
            f"last silently wins; the other's output never works."
        )

    # BURST_STREAM_COLLISION (USE_DSHOT_DMAR-aware model): faithfully walks
    # impl_timerPWMConfigDMABurst()'s actual per-timer/per-channel ownership
    # cascade instead of the naive per-channel grouping above. Processes
    # live DMA-claiming MOTOR rows in position order (== pwmInitMotors()'s
    # strict idx=0..motorCount-1 init order, since tim_motors/`result.rows`
    # preserve declaration order and position was assigned by that same
    # walk). For each physical timer: the FIRST channel of that timer to be
    # reached (dmaBurstRef still unset) makes the one real claim attempt,
    # using ITS OWN dmavar-resolved stream -- if it succeeds, the timer
    # locks onto that stream and EVERY LATER channel of the SAME timer
    # rides along for free without ever touching its own dmavar (mirrors
    # `if (!tch->timCtx->dmaBurstRef) { ... } ... return true;`). If the
    # first channel's attempt instead hits a stream some OTHER (earlier,
    # lower-position) timer already locked, dmaBurstRef stays unset and the
    # NEXT channel of the SAME timer gets its own independent attempt
    # (mirrors the ownership check's early `return false` leaving
    # dmaBurstRef untouched) -- so a multi-channel timer isn't necessarily
    # ALL dead just because its first channel loses; only the channel(s)
    # whose own attempt is actually reached and fails go dark, up until
    # some channel of that timer eventually succeeds (or none do).
    if dma_resolver.dshot_dmar:
        stream_owner = {}   # (dma,stream) -> winning entry
        timer_locked = {}   # tim token -> (dma,stream) once locked in
        for row in result.rows:
            if not (row["claims_dma"] and row["bucket"] == "MOTOR"):
                continue
            e = row["entry"]
            tim = e.tim
            if tim in timer_locked:
                continue  # rides along on this timer's already-locked stream
            resolved = row["stream"]
            if resolved is None or resolved[0] == "?":
                continue  # SILENT_DEAD_MOTOR / PARSER_GAP, handled elsewhere
            if resolved not in stream_owner:
                stream_owner[resolved] = e
                timer_locked[tim] = resolved
            else:
                winner = stream_owner[resolved]
                dma, s = resolved
                label = dma_resolver.stream_label(dma, s)
                loser_pos = row["position"]
                result.hazards.append(
                    f"BURST_STREAM_COLLISION: {label} locked in first by "
                    f"{winner.tim} (via {winner.tim}_{winner.ch}({winner.label})); "
                    f"{e.tim}_{e.ch}({e.label}) at position {loser_pos} is on a "
                    f"DIFFERENT physical timer ({e.tim}) and its own DMAR burst "
                    f"claim attempt to the same stream fails at motorCount="
                    f"{motor_count} -- under USE_DSHOT_DMAR a stream is claimed "
                    f"once per PHYSICAL TIMER (impl_timerPWMConfigDMABurst, "
                    f"timer_impl_stdperiph.c), not per channel: this channel's "
                    f"own dmaGetByTag()/ownership check fails, and this output "
                    f"stays silent even though pwmMotorConfig() reports success. "
                    f"Any LATER channel of {e.tim} not yet reached would get its "
                    f"own independent retry (dmaBurstRef stays unset on "
                    f"failure); this is the specific channel actually affected, "
                    f"not necessarily every channel of {e.tim}."
                )
                # timer_locked[tim] intentionally left unset -- the next
                # channel of this SAME timer (if any) gets its own attempt.

    for row in result.rows:
        if row["stream"] == ("?", row["entry"].dmavar) or (
            row["claims_dma"] and row["stream"] and row["stream"][0] == "?"
        ):
            e = row["entry"]
            result.hazards.append(
                f"PARSER_GAP: could not resolve DMA option table for "
                f"{e.tim}_{e.ch} ({e.label}) -- verify manually against "
                f"timer_def_*.h, this script's header parsing didn't find it."
            )

    return result


def print_table(result, motor_count, servo_count):
    print(f"\n--- motorCount={motor_count}"
          f"{'' if servo_count is None else f', servoCount={servo_count}'} ---")
    hdr = f'{"pos":>3}  {"tim_ch":<12} {"label":<10} {"bucket":<28} {"driven":<7} {"dma":<20}'
    print(hdr)
    print("-" * len(hdr))
    for row in result.rows:
        e = row["entry"]
        dma_str = "-"
        if row["claims_dma"]:
            d, s = row["stream"]
            dma_str = f"DMA{d} Stream{s}" if d != "?" else f"<unresolved:{s}>"
        elif row["no_dma_at_all"]:
            dma_str = "NONE (hazard!)"
        print(f'{e.index:>3}  {e.tim + "_" + e.ch:<12} {e.label:<10} '
              f'{row["bucket"]:<28} {str(row["driven"]):<7} {dma_str:<20}')
    if result.hazards:
        print("\nHazards:")
        for h in result.hazards:
            print(f"  - {h}")
    else:
        print("\nNo hazards found at this motor count.")


def run_target(inav_root, target_name, motor_count, servo_count, sweep_range,
               dshot, led_strip_override, verbose, dmavar_overrides=None,
               timer_output_modes=None):
    target_dir = inav_root / "src" / "main" / "target" / target_name
    target_c = target_dir / "target.c"
    target_h = target_dir / "target.h"
    cmake = target_dir / "CMakeLists.txt"
    if not target_c.is_file():
        raise SystemExit(f"No target.c under {target_dir}")

    family = detect_family(cmake.read_text(errors="ignore")) if cmake.is_file() else None
    if family is None:
        raise SystemExit(
            f"Could not detect MCU family from {cmake}. Supported: F4, F7, H7, AT32."
        )

    entries = parse_target_c(target_c.read_text(errors="ignore"))
    if not entries:
        raise SystemExit(f"No DEF_TIM(...) entries parsed from {target_c}")

    if dmavar_overrides:
        applied = apply_dmavar_overrides(entries, dmavar_overrides)
        print("Applying --dmavar-override (simulated only, target.c on disk "
              "is NOT modified):")
        for label, old_val, new_val in applied:
            print(f"  {label}: dmavar {old_val} -> {new_val}")

    timer_output_modes = timer_output_modes or {}
    if timer_output_modes:
        known_tims = {e.tim for e in entries}
        unknown = sorted(set(timer_output_modes) - known_tims)
        if unknown:
            raise SystemExit(
                f"--timer-output-mode: no DEF_TIM entry uses timer(s) "
                f"{unknown} in {target_c}. Known timers: {sorted(known_tims)}"
            )
        print("Applying --timer-output-mode (simulated only, no file on disk "
              "is modified):")
        for tim, mode in timer_output_modes.items():
            affected = sorted(e.label for e in entries if e.tim == tim)
            print(f"  {tim} -> OUTPUT_MODE_{mode} (affects: {', '.join(affected)})")

    adc_pins, led_strip, dshot_dmar = (set(), False, False)
    if target_h.is_file():
        adc_pins, led_strip, dshot_dmar = parse_target_h(target_h.read_text(errors="ignore"))
    if led_strip_override is not None:
        led_strip = led_strip_override

    dma_resolver = DmaResolver(family, target_dir, target_h.read_text(errors="ignore")
                                if target_h.is_file() else "", dshot_dmar)

    print(f"Target: {target_name}  MCU family: {family}  "
          f"USE_LED_STRIP: {led_strip}  DSHOT assumed: {dshot}")
    print(f"Parsed {len(entries)} DEF_TIM entries; ADC-conflict pins: "
          f"{sorted(adc_pins) if adc_pins else 'none'}")

    if motor_count is not None:
        result = simulate(entries, motor_count, servo_count, adc_pins, led_strip,
                           dma_resolver, dshot, timer_output_modes)
        print_table(result, motor_count, servo_count)
        return

    lo, hi = sweep_range
    print(f"\nSweeping motorCount {lo}..{hi}:")
    any_hazard = False
    for mc in range(lo, hi + 1):
        result = simulate(entries, mc, servo_count, adc_pins, led_strip,
                           dma_resolver, dshot, timer_output_modes)
        if verbose:
            print_table(result, mc, servo_count)
        elif result.hazards:
            any_hazard = True
            print(f"\nmotorCount={mc}:")
            for h in result.hazards:
                print(f"  - {h}")
        else:
            print(f"motorCount={mc}: clean")
    if not any_hazard and not verbose:
        print("\nNo hazards found across the swept range.")


# ---------------------------------------------------------------------------
# Self-test / regression cases (see the email that spawned this script for
# the full derivation of each reference point -- reproduced here so future
# edits to the simulation logic can be checked against known-correct answers
# without re-deriving them by hand).
# ---------------------------------------------------------------------------
DAKEFPVF405WING_ORIGINAL_TARGET_C = '''
timerHardware_t timerHardware[] = {
    DEF_TIM(TIM2,   CH2, PA1,  TIM_USE_OUTPUT_AUTO,   1, 0), // S1
    DEF_TIM(TIM3,   CH3, PB0,  TIM_USE_OUTPUT_AUTO,   1, 0), // S2
    DEF_TIM(TIM3,   CH4, PB1,  TIM_USE_OUTPUT_AUTO,   1, 0), // S3
    DEF_TIM(TIM12,  CH1, PB14, TIM_USE_OUTPUT_AUTO,   1, 0), // S4
    DEF_TIM(TIM12,  CH2, PB15, TIM_USE_OUTPUT_AUTO,   1, 0), // S5
    DEF_TIM(TIM8,   CH3, PC8,  TIM_USE_OUTPUT_AUTO,   1, 0), // S6
    DEF_TIM(TIM8,   CH4, PC9,  TIM_USE_OUTPUT_AUTO,   1, 0), // S7
    DEF_TIM(TIM1,   CH1, PA8,  TIM_USE_OUTPUT_AUTO,   0, 0), // S8
    DEF_TIM(TIM1,   CH2, PA9,  TIM_USE_OUTPUT_AUTO,   0, 0), // S9
    DEF_TIM(TIM1,   CH3, PA10, TIM_USE_OUTPUT_AUTO,   0, 0), // S10
    DEF_TIM(TIM5,   CH1, PA0,  TIM_USE_LED,   1, 0), // 2812LED
    DEF_TIM(TIM5,   CH3, PA2,  TIM_USE_ANY,   0, 0), // TX2  softserial1_Tx
};
'''


def _selftest(inav_root):
    ok = True

    def check(desc, cond):
        nonlocal ok
        mark = "PASS" if cond else "FAIL"
        if not cond:
            ok = False
        print(f"[{mark}] {desc}")

    # F4 header parsing sanity
    header = (inav_root / "src/main/drivers/timer_def_stm32f4xx.h").read_text()
    table = load_option_table(header)
    check("TIM3_CH4 has exactly one DMA option (DMA1 Stream2)",
          table.get(("TIM3", "CH4")) == [(1, 2, 5)])
    check("TIM5_CH1 has exactly one DMA option (DMA1 Stream2)",
          table.get(("TIM5", "CH1")) == [(1, 2, 6)])
    check("TIM12_CH1 has NO DMA option", table.get(("TIM12", "CH1")) == [])
    check("TIM12_CH2 has NO DMA option", table.get(("TIM12", "CH2")) == [])

    dma_resolver = DmaResolver("F4", inav_root / "src/main/target/DAKEFPVF405WING",
                                "", False)

    # --- Reference point 1: original (pre-edit) target.c, motorCount=2 ---
    entries = parse_target_c(DAKEFPVF405WING_ORIGINAL_TARGET_C)
    result = simulate(entries, motor_count=2, servo_count=None, adc_pins=set(),
                       led_strip_active=False, dma_resolver=dma_resolver, dshot=True)
    by_label = {r["entry"].label: r for r in result.rows}
    check("original target.c, mc=2: S1 is a driven MOTOR",
          by_label["S1"]["bucket"] == "MOTOR" and by_label["S1"]["driven"])
    check("original target.c, mc=2: S2 is a driven MOTOR",
          by_label["S2"]["bucket"] == "MOTOR" and by_label["S2"]["driven"])
    check("original target.c, mc=2: S3 resolves MOTOR but is NOT driven (dead)",
          by_label["S3"]["bucket"] == "MOTOR" and not by_label["S3"]["driven"])
    for s in ("S4", "S5", "S6", "S7", "S8", "S9", "S10"):
        check(f"original target.c, mc=2: {s} force-demoted to SERVO",
              by_label[s]["bucket"] == "SERVO")

    # --- Reference point 2: current (edited) target.c, S3 cascade ---
    target_c_path = inav_root / "src/main/target/DAKEFPVF405WING/target.c"
    entries2 = parse_target_c(target_c_path.read_text())
    for mc in (2, 3, 5):
        r = simulate(entries2, motor_count=mc, servo_count=None, adc_pins=set(),
                     led_strip_active=False, dma_resolver=dma_resolver, dshot=True)
        s3 = {row["entry"].label: row for row in r.rows}["S3"]
        check(f"edited target.c, mc={mc}: S3 still resolves MOTOR (never SERVO, "
              f"despite S4/S5 explicit TIM_USE_SERVO not protecting it)",
              s3["bucket"] == "MOTOR")

    # S4/S5 themselves should now genuinely be usable SERVOs regardless of mc
    for mc in (2, 3):
        r = simulate(entries2, motor_count=mc, servo_count=None, adc_pins=set(),
                     led_strip_active=False, dma_resolver=dma_resolver, dshot=True)
        rows = {row["entry"].label: row for row in r.rows}
        check(f"edited target.c, mc={mc}: S4 resolves SERVO and is driven",
              rows["S4"]["bucket"] == "SERVO" and rows["S4"]["driven"])
        check(f"edited target.c, mc={mc}: S5 resolves SERVO and is driven",
              rows["S5"]["bucket"] == "SERVO" and rows["S5"]["driven"])

    # --- Reference point 3: S3 vs LED DMA1 Stream2 collision when S3 is live ---
    r_mc2 = simulate(entries2, motor_count=2, servo_count=None, adc_pins=set(),
                      led_strip_active=True, dma_resolver=dma_resolver, dshot=True)
    check("edited target.c, mc=2, LED active: NO collision yet (S3 not driven)",
          not any("DMA_STREAM_COLLISION" in h for h in r_mc2.hazards))

    r_mc3 = simulate(entries2, motor_count=3, servo_count=None, adc_pins=set(),
                      led_strip_active=True, dma_resolver=dma_resolver, dshot=True)
    check("edited target.c, mc=3, LED active: S3 vs LED DMA1 Stream2 COLLISION found",
          any("DMA_STREAM_COLLISION" in h and "Stream2" in h for h in r_mc3.hazards))

    # --- Reference point 4: dedup fix verification for --timer-output-mode
    # TIMn=MOTORS on a shared multi-channel timer. Layout: TIM_A has 2
    # channels (A1, A2), forced to OUTPUT_MODE_MOTORS; TIM_B has 1 channel
    # (B1), left AUTO. Pre-fix, this reproduced the 2n-1 inflation bug
    # (motor_only_outputs went to 3 instead of 2 for the n=2 TIM_A group,
    # silently demoting B1 to SERVO at motorCount=3). Post-fix (the
    # `counted_timers` dedup guard in pwm_ensure_enough_motors()), the group
    # correctly counts as exactly 2, so B1 promotes to MOTOR at the naively
    # expected motorCount=3 -- same as the no-override control case.
    SYNTHETIC_INFLATION_TARGET_C = """
timerHardware_t timerHardware[] = {
    DEF_TIM(TIM_A,  CH1, PA1,  TIM_USE_OUTPUT_AUTO,   1, 0), // A1
    DEF_TIM(TIM_A,  CH2, PA2,  TIM_USE_OUTPUT_AUTO,   1, 0), // A2
    DEF_TIM(TIM_B,  CH1, PA3,  TIM_USE_OUTPUT_AUTO,   1, 0), // B1
};
"""
    synth_entries = parse_target_c(SYNTHETIC_INFLATION_TARGET_C)
    synth_resolver = DmaResolver("F4", inav_root / "src/main/target/DAKEFPVF405WING",
                                  "", False)
    modes = {"TIM_A": "MOTORS"}

    r2 = simulate(synth_entries, motor_count=2, servo_count=None, adc_pins=set(),
                  led_strip_active=False, dma_resolver=synth_resolver, dshot=False,
                  timer_output_modes=modes)
    rows2 = {row["entry"].label: row for row in r2.rows}
    check("dedup fix, motorCount=2: A1 and A2 (the TIM_A group) are MOTOR and "
          "driven, filling both slots",
          rows2["A1"]["bucket"] == "MOTOR" and rows2["A1"]["driven"] and
          rows2["A2"]["bucket"] == "MOTOR" and rows2["A2"]["driven"])
    check("dedup fix, motorCount=2: B1 is NOT promoted (both slots correctly "
          "consumed by the n=2 TIM_A group -- confirms the guard doesn't "
          "UNDER-count either)",
          rows2["B1"]["bucket"] == "SERVO")

    r3 = simulate(synth_entries, motor_count=3, servo_count=None, adc_pins=set(),
                  led_strip_active=False, dma_resolver=synth_resolver, dshot=False,
                  timer_output_modes=modes)
    rows3 = {row["entry"].label: row for row in r3.rows}
    check("dedup fix, motorCount=3: A1 and A2 are MOTOR and driven",
          rows3["A1"]["bucket"] == "MOTOR" and rows3["A1"]["driven"] and
          rows3["A2"]["bucket"] == "MOTOR" and rows3["A2"]["driven"])
    check("dedup fix, motorCount=3: B1 IS now promoted to MOTOR and driven "
          "(the TIM_A group correctly counts as 2, not the pre-fix inflated "
          "3 -- this is the bug fix; pre-fix, B1 stayed SERVO here)",
          rows3["B1"]["bucket"] == "MOTOR" and rows3["B1"]["driven"])

    # Control: same layout, but TIM_A left at AUTO (no override) -- matches
    # the override case exactly now that both are dedup'd correctly.
    r3_noverride = simulate(synth_entries, motor_count=3, servo_count=None,
                             adc_pins=set(), led_strip_active=False,
                             dma_resolver=synth_resolver, dshot=False)
    rows3n = {row["entry"].label: row for row in r3_noverride.rows}
    check("dedup fix control (no override): motorCount=3 gives B1 as "
          "MOTOR+driven, same as the MOTORS-override case above",
          rows3n["B1"]["bucket"] == "MOTOR" and rows3n["B1"]["driven"])

    # --- Reference point 5: DAKEFPVF405WING LED-preserving multi-motor
    # config -- TIM3 forced to OUTPUT_MODE_SERVOS protects BOTH S2 and S3
    # (pwmClaimTimer force-syncs them) from ever entering the MOTOR bucket,
    # so S3 can never claim DMA1 Stream2 and collide with the LED strip
    # (also DMA1 Stream2), at ANY motor count. ---
    dak_modes = {"TIM3": "SERVOS"}
    any_collision = False
    for mc in range(1, 9):
        r = simulate(entries2, motor_count=mc, servo_count=None, adc_pins=set(),
                     led_strip_active=True, dma_resolver=dma_resolver, dshot=True,
                     timer_output_modes=dak_modes)
        if any("DMA_STREAM_COLLISION" in h for h in r.hazards):
            any_collision = True
    check("DAKEFPVF405WING, TIM3=SERVOS override: NO DMA_STREAM_COLLISION "
          "at any motorCount 1..8 (LED preserved unconditionally)",
          not any_collision)

    r_mc6 = simulate(entries2, motor_count=6, servo_count=None, adc_pins=set(),
                      led_strip_active=True, dma_resolver=dma_resolver, dshot=True,
                      timer_output_modes=dak_modes)
    rows6 = {row["entry"].label: row for row in r_mc6.rows}
    check("DAKEFPVF405WING, TIM3=SERVOS, motorCount=6: S1,S6,S7,S8,S9,S10 all "
          "driven MOTOR (the max LED-preserving motor count)",
          all(rows6[s]["bucket"] == "MOTOR" and rows6[s]["driven"]
              for s in ("S1", "S6", "S7", "S8", "S9", "S10")))
    check("DAKEFPVF405WING, TIM3=SERVOS, motorCount=6: S2 and S3 are SERVO "
          "(never MOTOR), confirming both channels of the forced timer are "
          "protected, not just the one a naive per-channel fix would target",
          rows6["S2"]["bucket"] == "SERVO" and rows6["S3"]["bucket"] == "SERVO")

    # --- Real-world regression: 2026-08-14 bench report. Board flashed with
    # S1/S6/S7/S8/S9/S10 all resolving to driven MOTOR (matches the table
    # above) reported NO SIGNAL on S10 specifically, while S8/S9 worked.
    # pwmClaimTimer's cross-channel cascade makes a split MOTOR/SERVO outcome
    # within one shared-timer group (S8/S9/S10 all share TIM1) structurally
    # impossible -- confirmed above, all three always move together -- so the
    # role-resolution layer this script already modeled was never the cause.
    # Root cause (confirmed against upstream commit ab07785fa9, "Fix channel
    # selection for DMA2 Stream6", which made this exact change to 4 other
    # real boards): target.c's S10 used dmavar=0, i.e. D(2,6,0), which
    # timer_def_stm32f4xx.h also lists as an option for TIM1_CH1 and
    # TIM1_CH2 -- the combined/shared multi-channel request line, not a
    # request dedicated to CH3's own compare event. dmavar=1 (D(2,6,6)) is
    # the CH3-specific line and is what every other real F4-family INAV
    # target uses. This is the SHARED_TIMER_DMA_REQUEST hazard.
    #
    # UPDATE 2026-08-15 (dakefpvf405wing-hardware-bringup, unrelated to this
    # fix): target.c's S10 dmavar was changed 0 -> 1 as part of that task, so
    # the hazard this reference point exists to catch no longer reproduces
    # against the current file -- that's the fix working as intended, not a
    # regression in this script. Assertion updated to match; kept as a
    # regression guard against the dmavar reverting to 0.
    check("DAKEFPVF405WING, TIM3=SERVOS, motorCount=6: S10 (TIM1_CH3) no "
          "longer triggers SHARED_TIMER_DMA_REQUEST now that target.c uses "
          "dmavar=1 (the CH3-dedicated line) -- confirms the dakefpvf405wing "
          "-hardware-bringup fix is still in place",
          not any("SHARED_TIMER_DMA_REQUEST" in h and "TIM1_CH3" in h
                  for h in r_mc6.hazards))

    r_mc3 = simulate(entries2, motor_count=3, servo_count=None, adc_pins=set(),
                      led_strip_active=True, dma_resolver=dma_resolver, dshot=True,
                      timer_output_modes=dak_modes)
    rows3d = {row["entry"].label: row for row in r_mc3.rows}
    check("DAKEFPVF405WING, TIM3=SERVOS, motorCount=3: exactly S1,S6,S7 are "
          "live MOTORs (no inflation at this config -- no MOTORS override is "
          "used, only SERVOS on TIM3, which never triggers pass 1's "
          "double-count since SERVOS-forced entries never satisfy "
          "TIM_IS_MOTOR_ONLY); S8/S9/S10 fall back to SERVO as a group "
          "(the whole TIM1 group demotes together, all-or-nothing, since "
          "motor_only_outputs(3) < motorCount(3) is false at S8)",
          rows3d["S1"]["bucket"] == "MOTOR" and rows3d["S1"]["driven"]
          and rows3d["S6"]["bucket"] == "MOTOR" and rows3d["S6"]["driven"]
          and rows3d["S7"]["bucket"] == "MOTOR" and rows3d["S7"]["driven"]
          and rows3d["S8"]["bucket"] == "SERVO"
          and rows3d["S9"]["bucket"] == "SERVO"
          and rows3d["S10"]["bucket"] == "SERVO")

    print()
    print("SELFTEST " + ("PASSED" if ok else "FAILED"))
    return ok


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("inav_root", help="Path to an INAV checkout")
    ap.add_argument("--target", help="Target directory name (required unless --selftest)")
    ap.add_argument("--motor-count", type=int, help="Simulate exactly this motor count")
    ap.add_argument("--servo-count", type=int, default=None,
                     help="Cap the servo bucket the same way --motor-count caps the "
                          "motor bucket (default: unlimited)")
    ap.add_argument("--sweep", default=None,
                     help="MIN:MAX motor count range to sweep (default: 1..entry count)")
    ap.add_argument("--no-dshot", action="store_true",
                     help="Assume plain PWM/Oneshot/Multishot motors, not DSHOT")
    ap.add_argument("--no-led-strip", action="store_true",
                     help="Assume FEATURE_LED_STRIP is never enabled")
    ap.add_argument("--force-led-strip", action="store_true",
                     help="Assume FEATURE_LED_STRIP is active even if not obviously so")
    ap.add_argument("--verbose", action="store_true",
                     help="Print the full per-output table for every swept motor count")
    ap.add_argument("--selftest", action="store_true",
                     help="Run built-in regression cases instead of checking a target")
    ap.add_argument("--dmavar-override", action="append", default=[],
                     metavar="LABEL=N",
                     help="Simulate changing an entry's dmavar (the DEF_TIM "
                          "trailing DMA-option index) WITHOUT editing target.c "
                          "on disk. LABEL is the entry's // comment label "
                          "(e.g. S8), N is the new dmavar. Repeatable, e.g. "
                          "--dmavar-override S8=1 --dmavar-override S9=1. "
                          "Use this to answer 'does moving entry X to a "
                          "different DMA option eliminate collision Y across "
                          "a motorCount sweep' before touching the real file.")
    ap.add_argument("--timer-output-mode", action="append", default=[],
                     metavar="TIMn=MODE",
                     help="Simulate a timer_output_mode CLI/config.c override "
                          "(timerOverridesMutable(timer2id(TIMn))->outputMode) "
                          "WITHOUT editing any file on disk. TIMn is the `tim` "
                          "token used in this target's DEF_TIM(...) entries "
                          "(e.g. TIM3); MODE is AUTO, MOTORS, SERVOS, or LED. "
                          "Repeatable, e.g. --timer-output-mode TIM3=SERVOS.")
    args = ap.parse_args()

    inav_root = Path(args.inav_root).expanduser().resolve()

    if args.selftest:
        ok = _selftest(inav_root)
        sys.exit(0 if ok else 1)

    if not args.target:
        raise SystemExit("--target NAME is required (or use --selftest)")

    led_override = None
    if args.no_led_strip:
        led_override = False
    if args.force_led_strip:
        led_override = True

    sweep_range = None
    if args.sweep:
        lo, hi = args.sweep.split(":")
        sweep_range = (int(lo), int(hi))

    target_dir = inav_root / "src" / "main" / "target" / args.target
    if sweep_range is None and args.motor_count is None:
        entry_count = len(parse_target_c((target_dir / "target.c").read_text(errors="ignore")))
        sweep_range = (1, entry_count)

    dmavar_overrides = {}
    for spec in args.dmavar_override:
        if "=" not in spec:
            raise SystemExit(f"--dmavar-override must be LABEL=N, got {spec!r}")
        label, val = spec.split("=", 1)
        label = label.strip()
        try:
            dmavar_overrides[label] = int(val.strip())
        except ValueError:
            raise SystemExit(f"--dmavar-override: N must be an integer, got {spec!r}")

    timer_output_modes = {}
    for spec in args.timer_output_mode:
        if "=" not in spec:
            raise SystemExit(f"--timer-output-mode must be TIMn=MODE, got {spec!r}")
        tim, mode = spec.split("=", 1)
        tim = tim.strip().upper()
        mode = mode.strip().upper()
        if mode not in OUTPUT_MODE_TOKENS:
            raise SystemExit(
                f"--timer-output-mode: MODE must be one of {OUTPUT_MODE_TOKENS}, "
                f"got {mode!r} (from {spec!r})"
            )
        timer_output_modes[tim] = mode

    run_target(inav_root, args.target, args.motor_count, args.servo_count,
               sweep_range, not args.no_dshot, led_override, args.verbose,
               dmavar_overrides=dmavar_overrides,
               timer_output_modes=timer_output_modes)


if __name__ == "__main__":
    main()
