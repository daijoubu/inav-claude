#!/usr/bin/env python3
"""
Flag target.h #defines that look like typos of a real INAV macro (e.g.
BEEPER_PIN instead of BEEPER) -- a wrong name compiles cleanly but silently
disables whatever feature it was supposed to guard.

Usage: ./check_macro_typos.py <inav_checkout_root> [options]
Example: ./check_macro_typos.py ~/Documents/planes/inavflight/inav --target DAKEFPVH743_SLIM

Options:
  --target NAME        only report findings for this target directory
  --max-distance N     max edit distance to flag as a likely typo (default 2)
  --max-suffix N       max leftover length for a prefix/suffix match, e.g.
                       "_PIN" is 4 (default 5)
  --rebuild-cache      force a full re-scan of core source instead of using
                       the saved known-good cache (do this after a large core
                       refactor, in case a macro that used to be real was
                       removed -- the cache doesn't detect staleness itself)
  --cache PATH         override the cache file location

First run on a checkout does one full scan of core firmware source (~15-30s
on the whole tree) and saves a trimmed known-good list to
data/known_good_macros.txt: every name that's both defined by some target.h
AND actually referenced elsewhere in core source. Later runs reuse that
cache; only names it's never seen get a single targeted grep each, so
repeat runs are fast.

Findings are a checklist to verify by hand, not a pass/fail gate. Written
after DAKEFPVH743_SLIM defined `BEEPER_PIN` instead of `BEEPER` -- the
preprocessor has no opinion about which name "should" exist, so
`#if defined(BEEPER)` in sound_beeper.c just compiled out and left the pin
floating (a scope trace of the floating pin looked like a real, wrong-
frequency signal and cost a long diagnostic session before the typo was
spotted by inspection). The exact same typo was already sitting unnoticed in
two other targets (IFLIGHT_H743_AIO_V2, JHEH7AIO) -- copy-paste propagates a
wrong name just as easily as a right one, so "several targets define this" is
not evidence a name is correct.

Two finding categories, don't treat them the same:
1. Macros a firmware driver tests for by exact name via `#ifdef`/
   `#if defined()` (like `BEEPER`) -- a wrong name here silently disables
   real functionality. This is the dangerous case.
2. Per-board pin/bus/align macros (`_CS_PIN`, `_SPI_BUS`, `_ALIGN`) that a
   board's own target.c defines and consumes locally as literal
   substitution, never gated by `#ifdef` -- a "wrong-looking" name here
   (e.g. `ICM42688_CS_PIN` on ORBITF435, which actually uses `DEVHW_ICM42605`
   since that driver auto-detects both chips via WHO_AM_I) is at most a
   misleading label, not a functional bug: the value is what matters, and
   the board consumes its own name consistently.
Before treating a finding as real, grep whether the name appears inside an
`#ifdef`/`defined()` in core drivers (category 1) or only as a directly-
substituted argument in the board's own target.c (category 2).

"Multiple similar unreferenced names, one real name nearby" can mean dead
cruft, not a distinct chip: AIKONF7/BETAFPVF435/BROTHERHOBBYF405V3/
PRINCIPIOTF7 all define `USE_FLASH_W25M`, `USE_FLASH_W25M512`, and
`USE_FLASH_W25M02G` on the same CS pin as a working `USE_FLASH_W25N01G` --
none of the three W25M-family macros are referenced by any driver in
`src/main/drivers/` (that family was never implemented); they're harmless
only because the real `USE_FLASH_W25N01G` on the same pin still detects the
chip. Check `grep -rl NAME src/main/drivers` for actual driver support before
dismissing a finding as a false positive on the strength of "looks like a
real chip name."
"""
import argparse
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

CACHE_PATH = Path(__file__).resolve().parent.parent / "data" / "known_good_macros.txt"

DEFINE_RE = re.compile(r'^\s*#\s*define\s+([A-Za-z_][A-Za-z0-9_]*)')
USAGE_RE = re.compile(
    r'#\s*(?:ifdef|ifndef)\s+([A-Za-z_][A-Za-z0-9_]*)'
    r'|defined\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)'
)

# Suffixes commonly (and legitimately) appended target-to-target that would
# otherwise dominate the "prefix/suffix relationship" flag with noise.
BENIGN_SUFFIX_HINTS = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")


def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    la, lb = len(a), len(b)
    prev = list(range(lb + 1))
    for i in range(1, la + 1):
        cur = [i] + [0] * lb
        for j in range(1, lb + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost)
        prev = cur
    return prev[lb]


def is_prefix_relation(a: str, b: str, max_extra: int) -> bool:
    """True if the shorter name is a prefix of the longer, with a short-enough
    leftover (catches BEEPER -> BEEPER_PIN, MOTOR1 -> MOTOR1_PIN, etc.),
    while ignoring the very common "board defines the numbered sibling"
    pattern (MOTOR1 vs MOTOR10) by requiring the leftover not be purely a
    digit suffix chain of a *different* base name -- simple heuristic: skip
    if shorter name already ends in a digit (that's the "which motor" case,
    not a typo)."""
    if a == b:
        return False
    shorter, longer = (a, b) if len(a) <= len(b) else (b, a)
    if shorter and shorter[-1] in BENIGN_SUFFIX_HINTS:
        return False
    if not longer.startswith(shorter):
        return False
    extra = len(longer) - len(shorter)
    return 0 < extra <= max_extra


def collect_target_defines(target_root: Path):
    """name -> set of target dir names that define it."""
    defines = defaultdict(set)
    for header in sorted(target_root.glob("*/target.h")):
        target_name = header.parent.name
        try:
            text = header.read_text(errors="ignore")
        except OSError:
            continue
        for line in text.splitlines():
            m = DEFINE_RE.match(line)
            if m:
                defines[m.group(1)].add(target_name)
    return defines


IDENTIFIER_RE = re.compile(r'\b[A-Za-z_][A-Za-z0-9_]{2,}\b')


def collect_source_usage(src_main: Path, target_root: Path):
    """Set of every identifier token appearing anywhere in core firmware
    source, excluding each board's own target.h/target.c/config.c (so we
    only count usage that actually lives in driver/io/flight/fc logic, not
    other boards' own possibly-typo'd defines -- that would be circular).

    Shared files that live directly in src/main/target/ itself (common_pre.h,
    common_post.h, common_hardware.h, etc) are NOT excluded -- they're core
    glue logic that consumes board-level feature macros like USE_MAG_ALL, and
    early versions of this filter threw them out just for living under a path
    containing "target", producing false positives on real macros.

    Deliberately broader than just #ifdef/#ifndef/defined() -- macros are
    also consumed as plain tokens (IO_TAG(BEEPER), struct field defaults,
    etc), and narrowing to only #ifdef-style guards would make every such
    macro look "unreferenced" and flood the report with false positives."""
    used = set()
    for path in src_main.rglob("*.[ch]"):
        try:
            rel = path.relative_to(target_root)
        except ValueError:
            rel = None
        if rel is not None and len(rel.parts) > 1:
            continue  # inside a specific board's own target/ subdirectory
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        used.update(IDENTIFIER_RE.findall(text))
    return used


def load_known_good(cache_path: Path):
    """Returns None if no cache exists yet (caller must bootstrap it)."""
    if not cache_path.exists():
        return None
    return {line.strip() for line in cache_path.read_text().splitlines() if line.strip()}


def save_known_good(cache_path: Path, names) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text("\n".join(sorted(names)) + "\n")


def is_referenced_outside_boards(name: str, src_main: Path, target_root: Path) -> bool:
    """Targeted grep for a single token -- used only for names the cache
    hasn't seen before, so we never re-scan the whole tree just to check
    one new define. A whole-word match anywhere outside a specific board's
    own target/<BOARD>/ subdirectory counts as real (this includes shared
    files that live directly in target/, like common_post.h)."""
    try:
        result = subprocess.run(
            ["grep", "-rlw", "--include=*.c", "--include=*.h", name, str(src_main)],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    for line in result.stdout.splitlines():
        try:
            rel = Path(line).relative_to(target_root)
        except ValueError:
            return True  # match outside target/ entirely
        if len(rel.parts) <= 1:
            return True  # shared file living directly in target/
    return False


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "inav_root", nargs="?", default=".",
        help="Path to an INAV checkout (directory containing src/main)",
    )
    ap.add_argument(
        "--max-distance", type=int, default=2,
        help="Max Levenshtein distance to flag as a likely typo (default: 2)",
    )
    ap.add_argument(
        "--max-suffix", type=int, default=5,
        help="Max leftover length for a prefix/suffix match, e.g. '_PIN' is 4 (default: 5)",
    )
    ap.add_argument("--target", help="Only report findings for this target directory name")
    ap.add_argument(
        "--rebuild-cache", action="store_true",
        help="Force a full re-scan of core source instead of using the saved known-good list "
             "(do this after major refactors, in case previously-real macros were removed)",
    )
    ap.add_argument(
        "--cache", type=Path, default=CACHE_PATH,
        help=f"Path to the known-good macro cache (default: {CACHE_PATH})",
    )
    args = ap.parse_args()

    root = Path(args.inav_root).expanduser().resolve()
    src_main = root / "src" / "main"
    target_root = src_main / "target"
    if not target_root.is_dir():
        raise SystemExit(f"Can't find {target_root} -- pass the INAV checkout root")

    defines = collect_target_defines(target_root)

    known_good = None if args.rebuild_cache else load_known_good(args.cache)
    if known_good is None:
        print(
            "No cached known-good macro list -- doing a one-time full source scan "
            f"({src_main})...",
            file=sys.stderr,
        )
        # collect_source_usage tokenizes every identifier in core source --
        # function names, locals, keywords, comment fragments, all of it.
        # Only the subset that's ALSO a name some target.h actually defines
        # is worth keeping: that's the real "confirmed legitimate target
        # macro" vocabulary, and it's what every future lookup/fuzzy-match
        # will ever query against.
        referenced_anywhere = collect_source_usage(src_main, target_root)
        known_good = {name for name in defines if name in referenced_anywhere}
        save_known_good(args.cache, known_good)
        print(
            f"Cached {len(known_good)} known-good names (of {len(defines)} total "
            f"target defines) to {args.cache}\n",
            file=sys.stderr,
        )

    # Fuzzy-matching against the full known-good set (tens of thousands of
    # identifiers, including every lowercase variable/function name in the
    # tree) is the actual cost center -- a typo of an ALL_CAPS macro will
    # never resemble a lowercase C identifier, so narrow the candidate pool
    # to macro-shaped names once, up front, instead of per name-under-test.
    macro_candidates = [c for c in known_good if re.match(r'^[A-Z_][A-Z0-9_]*$', c)]

    newly_confirmed = set()
    findings = []
    for name, targets in defines.items():
        if args.target and args.target not in targets:
            continue
        if name in known_good:
            continue  # already confirmed real -- fine regardless of target count
        if is_referenced_outside_boards(name, src_main, target_root):
            newly_confirmed.add(name)
            continue
        best = None
        for candidate in macro_candidates:
            if candidate == name:
                continue
            if is_prefix_relation(name, candidate, args.max_suffix):
                d = abs(len(name) - len(candidate))
            else:
                # Edit distance can never be smaller than the length gap --
                # skip the O(len_a * len_b) DP whenever that alone already
                # rules the candidate out.
                if abs(len(name) - len(candidate)) > args.max_distance:
                    continue
                d = levenshtein(name, candidate)
                if d > args.max_distance:
                    continue
            if best is None or d < best[1]:
                best = (candidate, d)
        if best:
            findings.append((name, sorted(targets), best[0], best[1]))

    if newly_confirmed:
        save_known_good(args.cache, known_good | newly_confirmed)

    findings.sort(key=lambda f: (f[3], f[0]))
    if not findings:
        print("No suspicious rare/near-miss defines found.")
        return

    print(f"{'define':32} {'target(s)':30} {'closest known name':25} dist")
    print("-" * 95)
    for name, targets, closest, dist in findings:
        tstr = ",".join(targets[:3]) + ("..." if len(targets) > 3 else "")
        print(f"{name:32} {tstr:30} {closest:25} {dist}")
    print(
        f"\n{len(findings)} finding(s). These are rare defines that resemble a "
        "common/load-bearing name -- verify each by hand; false positives "
        "(legitimate rare board-specific macros) are expected."
    )


if __name__ == "__main__":
    main()
