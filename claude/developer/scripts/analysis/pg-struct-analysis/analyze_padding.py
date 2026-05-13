#!/usr/bin/env python3
"""
Analyze C struct field ordering for padding waste in INAV PG structs.

Uses pahole on a compiled ELF to get accurate layout, then reports:
- Struct size, padding bytes, and percentage wasted
- Fields that cause padding
- Optimized field order to minimize padding
- Estimated flash savings

Usage:
  python3 analyze_padding.py <elf_file> [--top N]

Requires: pahole (apt install dwarves)
"""

import subprocess
import sys
import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FieldInfo:
    name: str
    type_str: str
    offset: int       # byte offset in struct
    size: int         # byte size
    bit_offset: Optional[int] = None   # for bitfields
    bit_size: Optional[int] = None


@dataclass
class StructInfo:
    name: str
    size: int
    fields: list = field(default_factory=list)
    padding_bytes: int = 0
    holes: list = field(default_factory=list)   # list of (offset, size) padding gaps
    tail_padding: int = 0


def run_pahole(elf_file: str, struct_name: str = None) -> str:
    """Run pahole and return output."""
    cmd = ["pahole", "--recursive"]
    if struct_name:
        cmd += ["--class_name", struct_name]
    cmd.append(elf_file)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.stdout
    except subprocess.TimeoutExpired:
        return ""
    except FileNotFoundError:
        print("Error: pahole not found. Install with: apt install dwarves")
        sys.exit(1)


def parse_pahole_output(output: str) -> list[StructInfo]:
    """Parse pahole output into StructInfo objects."""
    structs = []
    current_struct = None
    size_pattern = re.compile(r'/\*\s+size:\s+(\d+),\s+cachelines.*?padding:\s+(\d+)')
    hole_pattern = re.compile(r'/\*\s+(\d+) bytes? hole')
    tail_padding_pattern = re.compile(r'/\*\s+(\d+) bytes? tail padding')
    member_pattern = re.compile(
        r'^\s+(\S.*?\S)\s+(\w+);\s+/\*\s+(\d+)\s+(\d+)\s*\*/'
    )
    struct_start = re.compile(r'^(struct|union)\s+(\w+)\s*\{')
    struct_end = re.compile(r'^\}')

    for line in output.splitlines():
        # Check for struct start
        m = struct_start.match(line)
        if m:
            current_struct = StructInfo(name=m.group(2), size=0)
            continue

        if current_struct is None:
            continue

        # Check for size/padding summary
        m = size_pattern.search(line)
        if m:
            current_struct.size = int(m.group(1))
            current_struct.padding_bytes = int(m.group(2))
            structs.append(current_struct)
            current_struct = None
            continue

        # Check for hole (internal padding)
        m = hole_pattern.search(line)
        if m and current_struct:
            current_struct.holes.append(int(m.group(1)))
            continue

        # Check for tail padding
        m = tail_padding_pattern.search(line)
        if m and current_struct:
            current_struct.tail_padding = int(m.group(1))
            continue

        # Check for member field
        m = member_pattern.match(line)
        if m and current_struct:
            finfo = FieldInfo(
                name=m.group(2),
                type_str=m.group(1).strip(),
                offset=int(m.group(3)),
                size=int(m.group(4)),
            )
            current_struct.fields.append(finfo)

    return structs


def estimate_optimized_size(struct: StructInfo) -> tuple[int, int]:
    """
    Estimate the minimum possible struct size after optimal field reordering.
    Returns (optimized_size, bytes_saved).

    This is a simplistic estimate: sum field sizes, round up to largest alignment.
    """
    if not struct.fields:
        return struct.size, 0

    # Sum of actual field data (no padding)
    data_bytes = sum(f.size for f in struct.fields if f.size > 0)

    # Largest alignment requirement (assume largest field size = alignment)
    max_field_size = max(f.size for f in struct.fields if f.size > 0)
    # Clamp alignment to max 4 bytes (ARM typically doesn't need 8-byte alignment
    # for struct fields unless explicitly 64-bit)
    alignment = min(max_field_size, 4)

    # Round up to alignment
    remainder = data_bytes % alignment
    optimized = data_bytes if remainder == 0 else data_bytes + (alignment - remainder)

    bytes_saved = struct.size - optimized
    return optimized, max(0, bytes_saved)


def suggest_field_order(struct: StructInfo) -> list[FieldInfo]:
    """Return fields sorted largest-to-smallest to minimize padding."""
    return sorted(struct.fields, key=lambda f: (-f.size, f.name))


def print_report(structs: list[StructInfo], top_n: int = 30):
    """Print analysis report."""
    # Filter to structs with padding
    with_padding = [s for s in structs if s.padding_bytes > 0 and s.size > 4]

    # Sort by: internal holes (actual saveable padding), descending
    def internal_holes(s):
        return s.padding_bytes - s.tail_padding

    with_padding.sort(key=lambda s: -internal_holes(s))

    total_internal_padding = sum(internal_holes(s) for s in with_padding)
    total_tail_padding = sum(s.tail_padding for s in with_padding)

    print(f"\n{'='*80}")
    print(f"PG STRUCT PADDING ANALYSIS")
    print(f"{'='*80}")
    print(f"Structs with padding: {len(with_padding)}")
    print(f"Total internal padding (saveable): {total_internal_padding} bytes")
    print(f"Total tail padding (cannot save):  {total_tail_padding} bytes")
    print(f"{'='*80}\n")

    print(f"{'Struct':<45} {'Size':>6} {'Holes':>6} {'Tail':>5} {'Save?':>6}")
    print(f"{'-'*45} {'-'*6} {'-'*6} {'-'*5} {'-'*6}")

    shown = 0
    for s in with_padding:
        holes = internal_holes(s)
        if holes == 0:
            continue  # Only tail padding, can't save

        _, saveable = estimate_optimized_size(s)
        flag = f"~{saveable}B" if saveable > 0 else ""
        print(f"{s.name:<45} {s.size:>6} {holes:>6} {s.tail_padding:>5} {flag:>6}")
        shown += 1
        if shown >= top_n:
            break

    print(f"\n{'='*80}")
    print("DETAILED VIEW: Top structs by internal padding")
    print(f"{'='*80}")

    for s in with_padding[:15]:
        holes = internal_holes(s)
        if holes == 0:
            continue

        _, saveable = estimate_optimized_size(s)
        print(f"\n--- {s.name} (size={s.size}, internal_holes={holes}, tail={s.tail_padding}) ---")

        if s.fields:
            print(f"  {'Offset':>7} {'Size':>5}  {'Field'}")
            prev_end = 0
            for f in s.fields:
                if f.offset > prev_end:
                    gap = f.offset - prev_end
                    print(f"  {'':>7} {gap:>5}  [PADDING {gap} bytes]")
                print(f"  {f.offset:>7} {f.size:>5}  {f.name} ({f.type_str})")
                prev_end = f.offset + f.size

            if s.tail_padding > 0:
                print(f"  {'':>7} {s.tail_padding:>5}  [TAIL PADDING {s.tail_padding} bytes]")

        if saveable > 0:
            print(f"\n  Suggested reorder (largest first):")
            sorted_fields = suggest_field_order(s)
            offset = 0
            for f in sorted_fields:
                # Align offset to field size (capped at 4)
                align = min(f.size, 4)
                if align > 0 and offset % align != 0:
                    pad = align - (offset % align)
                    print(f"    {offset:>7} {pad:>5}  [padding]")
                    offset += pad
                print(f"    {offset:>7} {f.size:>5}  {f.name} ({f.type_str})")
                offset += f.size
            print(f"  Estimated optimized size: ~{offset} bytes (saves ~{s.size - offset} bytes)")


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <elf_file> [--top N]")
        sys.exit(1)

    elf_file = sys.argv[1]
    top_n = 30
    if "--top" in sys.argv:
        idx = sys.argv.index("--top")
        top_n = int(sys.argv[idx + 1])

    print(f"Running pahole on {elf_file}...")
    output = run_pahole(elf_file)

    if not output:
        print("No pahole output. Check that the ELF has debug symbols.")
        sys.exit(1)

    structs = parse_pahole_output(output)
    print(f"Parsed {len(structs)} structs")

    print_report(structs, top_n=top_n)


if __name__ == "__main__":
    main()
