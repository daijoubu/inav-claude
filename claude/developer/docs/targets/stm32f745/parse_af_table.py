#!/usr/bin/env python3
"""
Extract Table 12 "Alternate function mapping" from the STM32F745/F746 datasheet
using pdfplumber for accurate table extraction.

Reads pages 78-90 of stm32f745ie.pdf and produces three output files:

  alternate-functions.tsv   — tab-separated: Pin, AF0, AF1, ..., AF15
  alternate-functions.md    — Markdown reference table by port
  af-by-function.txt        — Inverted index: function → PIN(AFn) list

Usage:
    python3 parse_af_table.py

Requires:
    pip install pdfplumber
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
PDF = HERE / "stm32f745ie.pdf"
TSV_OUT = HERE / "alternate-functions.tsv"
MD_OUT = HERE / "alternate-functions.md"
INV_OUT = HERE / "af-by-function.txt"

# Table 12 spans PDF pages 78-90 (0-indexed: 77-89)
TABLE_PAGES = range(77, 90)

AF_GROUPS = {
    0:  "SYS",
    1:  "TIM1/2",
    2:  "TIM3/4/5",
    3:  "TIM8/9/10/11/LPTIM1/CEC",
    4:  "I2C1/2/3/4/CEC",
    5:  "SPI1/2/3/4/5/6/I2S",
    6:  "SPI3/SAI1",
    7:  "USART1/2/3/UART5/SPDIFRX",
    8:  "SAI2/USART6/UART4/5/7/8/SPDIFRX",
    9:  "CAN1/2/TIM12/13/14/QUADSPI/LCD",
    10: "SAI2/QUADSPI/OTG2_HS/OTG1_FS",
    11: "ETH/OTG1_FS",
    12: "FMC/SDMMC1/OTG2_FS",
    13: "DCMI",
    14: "LCD",
    15: "EVENTOUT",
}

PIN_RE = re.compile(r'^P[A-K]\d{1,2}$')


def clean_cell(val: str | None) -> str:
    """Normalize a table cell value."""
    if val is None:
        return "-"

    parts = [p.strip() for p in val.split('\n')]
    parts = [p for p in parts if p and p != '-']
    if not parts:
        return "-"

    result = parts[0]
    for part in parts[1:]:
        if result.endswith(('_', '-', '/')):
            result = result + part
        elif part.startswith(('_', '/')):
            result = result + part
        else:
            result = result + '/' + part

    result = re.sub(
        r'\b(TIM|SPI|I2C|UART|USART|OTG|ETH|FMC|SDMMC|DCMI|CAN|ADC|DAC|SAI|QUADSPI|RNG|RTC|LPTIM|LCD)\s+',
        r'\1',
        result,
    )
    result = re.sub(r'_\s+', '_', result)
    result = re.sub(r'\s+_', '_', result)
    result = re.sub(r'\s+', ' ', result).strip()
    result = result.rstrip('/')

    # Fix line-wrap artifacts: the F745 PDF has narrow columns so identifiers
    # sometimes wrap mid-word, producing e.g. "SPI1_SC/K/I2S1_CK" instead of
    # "SPI1_SCK/I2S1_CK".  Pattern: PERIPHERAL_PARTIAL/SHORT/ where SHORT is
    # 1-3 chars with no underscore — treat as continuation, not a new function.
    result = re.sub(
        r'([A-Z][A-Z0-9_]*_[A-Z0-9]+)/([A-Z0-9]{1,3})(?=[_/]|$)',
        lambda m: m.group(1) + m.group(2),
        result,
    )

    # Fix specific known split artifacts
    result = result.replace('EVEN/TOUT', 'EVENTOUT')

    return result if result else "-"


def parse_pdf() -> dict[str, dict[int, str]]:
    """Extract all pin AF data from the PDF using pdfplumber."""
    try:
        import pdfplumber
    except ImportError:
        sys.exit("pdfplumber not installed. Run: pip install pdfplumber")

    all_pins: dict[str, dict[int, str]] = {}

    with pdfplumber.open(PDF) as pdf:
        for page_idx in TABLE_PAGES:
            if page_idx >= len(pdf.pages):
                break
            page = pdf.pages[page_idx]
            tables = page.find_tables()
            if not tables:
                print(f"  Page {page_idx + 1}: no table found", file=sys.stderr)
                continue

            table = max(tables, key=lambda t: len(t.extract()))
            rows = table.extract()

            col_map: dict[int, int] = {}
            for row in rows[:4]:
                for col_idx, cell in enumerate(row):
                    if cell is None:
                        continue
                    m = re.match(r'^AF(\d+)$', cell.strip())
                    if m:
                        col_map[int(m.group(1))] = col_idx

            if len(col_map) < 14:
                print(f"  Page {page_idx + 1}: only found {len(col_map)} AF columns", file=sys.stderr)
                continue

            pin_col = None
            for row in rows[2:6]:
                for col_idx, cell in enumerate(row):
                    if cell and PIN_RE.match(cell.strip()):
                        pin_col = col_idx
                        break
                if pin_col is not None:
                    break

            if pin_col is None:
                pin_col = 1

            for row in rows[2:]:
                if pin_col >= len(row):
                    continue
                cell_val = row[pin_col]
                if not cell_val:
                    continue
                pin = cell_val.strip()
                if not PIN_RE.match(pin):
                    continue

                pin_afs: dict[int, str] = {}
                for af_num, col_idx in col_map.items():
                    if col_idx < len(row):
                        val = clean_cell(row[col_idx])
                        if val and val != "-":
                            pin_afs[af_num] = val

                if pin not in all_pins:
                    all_pins[pin] = pin_afs
                else:
                    for af_num, val in pin_afs.items():
                        if af_num not in all_pins[pin]:
                            all_pins[pin][af_num] = val

    return all_pins


def sort_pin(pin: str) -> tuple[int, int]:
    m = re.match(r'P([A-K])(\d+)', pin)
    return (ord(m.group(1)), int(m.group(2))) if m else (0, 0)


def main() -> None:
    if not PDF.exists():
        sys.exit(f"PDF not found: {PDF}")

    print(f"Reading {PDF.name} (pages 78-90)...")
    all_pins = parse_pdf()
    sorted_pins = sorted(all_pins.keys(), key=sort_pin)
    print(f"Found {len(sorted_pins)} pins")

    af_nums = list(range(16))

    # --- TSV ---
    with TSV_OUT.open("w") as f:
        f.write("Pin\t" + "\t".join(f"AF{n}" for n in af_nums) + "\n")
        for pin in sorted_pins:
            afs = all_pins[pin]
            row = pin + "\t" + "\t".join(afs.get(n, "-") for n in af_nums)
            f.write(row + "\n")
    print(f"Written: {TSV_OUT.name}")

    # --- Markdown ---
    with MD_OUT.open("w") as f:
        f.write("# STM32F745/F746 Alternate Function Mapping (Table 12)\n\n")
        f.write("Source: STM32F745xx/STM32F746xx Datasheet DS10916, pages 78–90\n\n")
        f.write("## AF Group Reference\n\n")
        f.write("| AF# | Peripheral Group |\n|-----|------------------|\n")
        for n, grp in AF_GROUPS.items():
            f.write(f"| AF{n:>2} | {grp} |\n")
        f.write("\n---\n\n## Pin Alternate Functions\n\n")

        current_port = None
        for pin in sorted_pins:
            port = pin[:2]
            if port != current_port:
                current_port = port
                f.write(f"\n### Port {port[1]}\n\n")
                f.write("| Pin |")
                for n in af_nums:
                    f.write(f" AF{n} |")
                f.write("\n|-----|")
                for _ in af_nums:
                    f.write("----|")
                f.write("\n")

            afs = all_pins[pin]
            row = f"| **{pin}** |"
            for n in af_nums:
                val = afs.get(n, "-")
                row += f" {val} |"
            f.write(row + "\n")
    print(f"Written: {MD_OUT.name}")

    # --- Inverted index ---
    inverted: dict[str, list[str]] = {}
    for pin in sorted_pins:
        for af_num, func in all_pins[pin].items():
            if func and func != "-":
                inverted.setdefault(func, []).append(f"{pin}(AF{af_num})")

    with INV_OUT.open("w") as f:
        f.write("# STM32F745/F746 — Alternate Function to Pin Mapping\n")
        f.write("# Source: Table 12, DS10916 pages 78-90\n\n")
        f.write(f"{'Function':<35} Pins\n")
        f.write("-" * 80 + "\n")
        for func in sorted(inverted.keys()):
            pins_str = ", ".join(inverted[func])
            f.write(f"{func:<35} {pins_str}\n")
    print(f"Written: {INV_OUT.name}")


if __name__ == "__main__":
    main()
