#!/usr/bin/env python3
"""
Analyze C struct field ordering for padding waste from source code.
Simulates ARM32 struct layout (same alignment rules as x86-32 for basic types).

Parses C header files to extract PG struct definitions, then computes padding
using C alignment rules and suggests optimal field ordering.

Usage:
  python3 source_padding_analyzer.py <inav_src_dir> [--min-holes N]

Example:
  python3 source_padding_analyzer.py ~/Documents/planes/inavflight/inav/src/main
"""

import re
import sys
import os
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


# ARM32 type sizes and alignments (most are same as x86-32)
TYPE_SIZES = {
    # Exact width types
    'uint8_t': (1, 1),
    'int8_t': (1, 1),
    'uint16_t': (2, 2),
    'int16_t': (2, 2),
    'uint32_t': (4, 4),
    'int32_t': (4, 4),
    'uint64_t': (8, 8),
    'int64_t': (8, 8),
    # C basic types (ARM32 / AAPCS)
    'char': (1, 1),
    'signed char': (1, 1),
    'unsigned char': (1, 1),
    'short': (2, 2),
    'unsigned short': (2, 2),
    'int': (4, 4),
    'unsigned int': (4, 4),
    'unsigned': (4, 4),
    'long': (4, 4),
    'unsigned long': (4, 4),
    'float': (4, 4),
    'double': (8, 8),  # 8-byte on AAPCS64, 4-byte alignment on some ARM32 ABIs
    'bool': (1, 1),
    '_Bool': (1, 1),
    # Common enums (treated as int = 4 bytes)
    '__enum__': (4, 4),
}


@dataclass
class Field:
    name: str
    type_str: str
    base_type: str    # resolved type key
    size: int         # in bytes
    alignment: int    # in bytes
    array_count: int = 1  # 1 for non-arrays


@dataclass
class StructAnalysis:
    name: str
    fields: list
    actual_size: int = 0      # simulated size
    padding_bytes: int = 0
    internal_holes: int = 0   # padding bytes NOT at end
    tail_padding: int = 0
    optimized_size: int = 0
    savings: int = 0
    file_path: str = ""


def parse_type_info(type_str: str) -> tuple[int, int]:
    """Return (size, alignment) for a type string. Returns (0, 1) if unknown."""
    t = type_str.strip()

    # Strip 'const', 'volatile', 'signed', etc.
    t = re.sub(r'\b(const|volatile)\b', '', t).strip()

    if t in TYPE_SIZES:
        return TYPE_SIZES[t]

    # Handle common INAV-specific typedefs that are just aliases
    # (enums, other uint types)
    if t.endswith('_e') or t.endswith('_t') and 'Config' not in t:
        # Likely an enum type or typedef uint - assume 4 bytes for enum, 0 for unknown
        pass

    # Try matching patterns
    if re.match(r'u?int\d+_t$', t):
        bits = int(re.search(r'\d+', t).group())
        sz = bits // 8
        return (sz, sz)

    if t.endswith('_e'):
        # Enum - treat as uint8_t if it's likely a small enum
        return TYPE_SIZES['__enum__']

    return (0, 1)   # unknown


def simulate_layout(fields: list[Field]) -> tuple[int, int, int]:
    """
    Simulate C struct layout for given fields.
    Returns (total_size, internal_holes_bytes, tail_padding_bytes).
    """
    if not fields:
        return (0, 0, 0)

    offset = 0
    max_alignment = 1
    internal_holes = 0

    for f in fields:
        if f.alignment == 0 or f.size == 0:
            continue
        # Align current offset to field alignment
        remainder = offset % f.alignment
        if remainder != 0:
            pad = f.alignment - remainder
            internal_holes += pad
            offset += pad
        max_alignment = max(max_alignment, f.alignment)
        offset += f.size * f.array_count

    # End padding: round up to struct alignment
    max_alignment = min(max_alignment, 4)   # ARM32 max natural alignment is 4 for basic types
    remainder = offset % max_alignment
    tail_padding = 0
    if remainder != 0:
        tail_padding = max_alignment - remainder
        offset += tail_padding

    return (offset, internal_holes, tail_padding)


def optimal_layout(fields: list[Field]) -> tuple[int, int, int]:
    """
    Simulate layout with fields sorted largest-to-smallest.
    Returns (size, internal_holes, tail_padding).
    """
    sorted_fields = sorted(
        [f for f in fields if f.size > 0],
        key=lambda f: (-f.alignment, -f.size, f.name)
    )
    return simulate_layout(sorted_fields)


def extract_structs_from_file(filepath: str) -> list[dict]:
    """
    Extract struct definitions from a C file.
    Returns list of {'name': str, 'fields_raw': str}
    """
    with open(filepath, 'r', errors='ignore') as fp:
        content = fp.read()

    # Remove comments
    content = re.sub(r'/\*.*?\*/', ' ', content, flags=re.DOTALL)
    content = re.sub(r'//[^\n]*', ' ', content)
    # Remove preprocessor directives (approximate)
    content = re.sub(r'#[^\n]*', '', content)

    structs = []
    # Match typedef struct { ... } name_t;
    pattern = re.compile(
        r'typedef\s+struct\s*\w*\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\s*(\w+)\s*;',
        re.DOTALL
    )

    for m in pattern.finditer(content):
        body = m.group(1)
        name = m.group(2)
        structs.append({'name': name, 'body': body, 'file': filepath})

    return structs


def parse_fields(body: str, known_types: dict) -> list[Field]:
    """Parse struct body into Field objects."""
    fields = []

    # Find field declarations: type name[array]; or type name;
    field_pattern = re.compile(
        r'^\s*((?:(?:unsigned|signed|const|volatile)\s+)?[\w_]+(?:\s*\*)*)\s+'  # type
        r'([\w_]+)\s*'                                                             # name
        r'(?:\[(\d+)\])?\s*;',                                                    # optional [N]
        re.MULTILINE
    )

    for m in field_pattern.finditer(body):
        type_str = m.group(1).strip()
        field_name = m.group(2).strip()
        array_str = m.group(3)
        array_count = int(array_str) if array_str else 1

        # Skip if field_name is a keyword
        if field_name in ('struct', 'union', 'enum', 'typedef'):
            continue

        size, alignment = parse_type_info(type_str)

        # Check known typedefs/enums
        if size == 0 and type_str in known_types:
            size, alignment = known_types[type_str]

        # Guess enum: ends in _e or enum member
        if size == 0 and (type_str.endswith('_e') or type_str.endswith('_t')):
            # Unknown struct typedef - skip for now
            continue

        if size == 0:
            continue

        fields.append(Field(
            name=field_name,
            type_str=type_str,
            base_type=type_str,
            size=size,
            alignment=alignment,
            array_count=array_count,
        ))

    return fields


def analyze_directory(src_dir: str, min_holes: int = 2) -> list[StructAnalysis]:
    """Walk source directory and analyze all PG-registered structs."""
    src_path = Path(src_dir)

    # Find all header files
    headers = list(src_path.rglob('*.h'))
    c_files = list(src_path.rglob('*.c'))

    # Build known type table from typedef aliases
    known_types = {}

    # Extract all struct defs
    all_structs = []
    for hf in headers:
        try:
            all_structs.extend(extract_structs_from_file(str(hf)))
        except Exception:
            pass

    # Find PG-registered structs
    pg_types = set()
    for cf in c_files + headers:
        try:
            content = open(str(cf), errors='ignore').read()
            # Look for PG_REGISTER...(_type, ...)
            for m in re.finditer(r'PG_(?:REGISTER|DECLARE)[^(]*\(\s*(\w+)', content):
                pg_types.add(m.group(1))
        except Exception:
            pass

    print(f"Found {len(pg_types)} PG-registered types")
    print(f"Parsed {len(all_structs)} struct definitions")

    # Analyze each PG struct
    results = []
    for s in all_structs:
        if s['name'] not in pg_types:
            continue

        fields = parse_fields(s['body'], known_types)
        if not fields:
            continue

        actual_size, internal_holes, tail_padding = simulate_layout(fields)
        opt_size, opt_holes, opt_tail = optimal_layout(fields)

        if actual_size == 0:
            continue

        savings = actual_size - opt_size

        analysis = StructAnalysis(
            name=s['name'],
            fields=fields,
            actual_size=actual_size,
            padding_bytes=internal_holes + tail_padding,
            internal_holes=internal_holes,
            tail_padding=tail_padding,
            optimized_size=opt_size,
            savings=max(0, savings),
            file_path=s['file'],
        )
        results.append(analysis)

    # Filter and sort by savings
    with_savings = [r for r in results if r.internal_holes >= min_holes]
    with_savings.sort(key=lambda r: -r.savings)

    return with_savings


def print_results(results: list[StructAnalysis]):
    total_savings = sum(r.savings for r in results)
    print(f"\n{'='*80}")
    print(f"PG STRUCT PADDING ANALYSIS (from source code)")
    print(f"{'='*80}")
    print(f"Structs with significant internal padding: {len(results)}")
    print(f"Total potential savings: ~{total_savings} bytes")
    print(f"{'='*80}")
    print(f"\n{'Struct':<45} {'Size':>5} {'Holes':>6} {'Tail':>5} {'Save':>5}")
    print(f"{'-'*45} {'-'*5} {'-'*6} {'-'*5} {'-'*5}")

    for r in results:
        relpath = os.path.relpath(r.file_path)
        save_str = f"+{r.savings}B" if r.savings > 0 else ""
        print(f"{r.name:<45} {r.actual_size:>5} {r.internal_holes:>6} {r.tail_padding:>5} {save_str:>5}")

    print(f"\n{'='*80}")
    print("DETAILED ANALYSIS (top structs by savings)")
    print(f"{'='*80}")

    for r in results[:20]:
        if r.savings == 0:
            continue
        print(f"\n=== {r.name} ===")
        print(f"  File: {os.path.relpath(r.file_path)}")
        print(f"  Current size: {r.actual_size} bytes ({r.internal_holes} holes + {r.tail_padding} tail)")
        print(f"  Optimized size: ~{r.optimized_size} bytes (saves ~{r.savings} bytes)")
        print()
        print("  Current layout:")
        offset = 0
        max_align = 1
        for f in r.fields:
            if f.alignment > 0 and f.size > 0:
                rem = offset % f.alignment
                if rem != 0:
                    pad = f.alignment - rem
                    print(f"    @{offset:4d}  [{pad:2d}B PADDING]")
                    offset += pad
                max_align = max(max_align, f.alignment)
                print(f"    @{offset:4d}  {f.size * f.array_count:2d}B  {f.type_str} {f.name}{'['+str(f.array_count)+']' if f.array_count > 1 else ''}")
                offset += f.size * f.array_count
        if r.tail_padding:
            print(f"    @{offset:4d}  [{r.tail_padding:2d}B TAIL PADDING]")
        print()
        print("  Suggested order (largest first):")
        sorted_fields = sorted(
            [f for f in r.fields if f.size > 0],
            key=lambda f: (-f.alignment, -f.size, f.name)
        )
        offset = 0
        for f in sorted_fields:
            rem = offset % f.alignment
            if rem != 0:
                pad = f.alignment - rem
                print(f"    @{offset:4d}  [{pad:2d}B padding]")
                offset += pad
            print(f"    @{offset:4d}  {f.size * f.array_count:2d}B  {f.type_str} {f.name}{'['+str(f.array_count)+']' if f.array_count > 1 else ''}")
            offset += f.size * f.array_count
        # End padding
        max_align = min(max(f.alignment for f in sorted_fields if f.alignment > 0), 4)
        rem = offset % max_align
        if rem != 0:
            tail = max_align - rem
            print(f"    @{offset:4d}  [{tail:2d}B tail padding]")
            offset += tail
        print(f"    Total: {offset} bytes")


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <inav_src_main_dir> [--min-holes N]")
        sys.exit(1)

    src_dir = sys.argv[1]
    min_holes = 2
    if '--min-holes' in sys.argv:
        idx = sys.argv.index('--min-holes')
        min_holes = int(sys.argv[idx + 1])

    results = analyze_directory(src_dir, min_holes=min_holes)
    print_results(results)


if __name__ == '__main__':
    main()
