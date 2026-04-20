#!/usr/bin/env python3
"""
Extract alternate function / MUX mapping for AT32F435/437 series.

Two data sources are combined:
  1. INAV's timer_def_at32f43x.h  — exact MUX numbers for every timer pin
  2. AT32F437VGT7-datasheet.pdf   — pin definitions with IOMUX function lists
     (Section 3, "Table 8. AT32F435/437 series pin definitions")
     Extracted via pdfplumber table mode for accurate multi-line cell handling.

Output files (written next to this script):
  alternate-functions.tsv    Tab-separated: Pin, MUX0..MUX15 (full table)
  alternate-functions.md     Markdown reference table by port
  af-by-function.txt         Inverted index: function → PIN(MUXn) list
  mux-groups.md              Reference: MUX number → peripheral group

Usage:
    pip install pdfplumber
    python3 parse_af_table.py

Notes:
- AT32F435 uses "IOMUX" (GPIOx_MUXx registers) with MUX0-MUX15 per pin,
  equivalent to STM32's AF0-AF15 naming.
- Timer MUX numbers come from INAV's timer_def_at32f43x.h (authoritative).
- SPI/UART/I2C MUX numbers come from known peripheral→MUX-group assignments
  confirmed in INAV driver source (bus_spi_at32f43x.c, serial_uart_at32f43x.c,
  bus_i2c_at32f43x.c).
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
PDF = (HERE / "datasheets_application_notes/AT32F437VGT7-datasheet.pdf").resolve()

# Find INAV repo root by walking up
_here = HERE
INAV_TIMER_DEF = None
for _ in range(8):
    candidate = _here / "inav/src/main/drivers/timer_def_at32f43x.h"
    if candidate.exists():
        INAV_TIMER_DEF = candidate
        break
    _here = _here.parent
if INAV_TIMER_DEF is None:
    INAV_TIMER_DEF = Path("/home/raymorris/Documents/planes/inavflight/inav/src/main/drivers/timer_def_at32f43x.h")

TSV_OUT  = HERE / "alternate-functions.tsv"
MD_OUT   = HERE / "alternate-functions.md"
INV_OUT  = HERE / "af-by-function.txt"
MUX_OUT  = HERE / "mux-groups.md"

# ─────────────────────────────────────────────────────────────────────────────
# Known AT32F435/437 MUX group → peripheral mapping
# Source: AT32F435/437 Reference Manual + INAV driver source
# ─────────────────────────────────────────────────────────────────────────────
MUX_GROUPS = {
    0:  "SYS (SWD/JTAG, TRACE, MCO, CLKOUT)",
    1:  "TMR1 / TMR2",
    2:  "TMR3 / TMR4 / TMR5 / TMR20 (partial)",
    3:  "TMR8 / TMR9 / TMR10 / TMR11",
    4:  "I2C1 / I2C2 / I2C3",
    5:  "SPI1 / SPI2 / I2S1 / I2S2",
    6:  "SPI3 / SPI4 / I2S3 / I2S4 / TMR20 (partial)",
    7:  "USART1 / USART2 / USART3",
    8:  "UART4 / UART5 / USART6 / UART7 / UART8",
    9:  "CAN1 / CAN2 / TMR12 / TMR13 / TMR14",
    10: "OTGFS1 / OTGFS2",
    11: "EMAC (Ethernet MII/RMII)",
    12: "SDIO1 / XMC (external memory)",
    13: "DVP (digital video) / SDIO2",
    14: "QSPI1 / QSPI2",
    15: "EVENTOUT",
}

# ─────────────────────────────────────────────────────────────────────────────
# Peripheral signal → MUX number mapping (confirmed from INAV driver source)
# ─────────────────────────────────────────────────────────────────────────────
SIGNAL_TO_MUX = {
    # SPI1/SPI2 (MUX5) — from bus_spi_at32f43x.c
    "SPI1": 5, "SPI2": 5, "I2S1": 5, "I2S2": 5,
    # SPI3/SPI4 (MUX6) — from bus_spi_at32f43x.c
    "SPI3": 6, "SPI4": 6, "I2S3": 6, "I2S4": 6,
    # I2C (MUX4) — from bus_i2c_at32f43x.c
    "I2C1": 4, "I2C2": 4, "I2C3": 4,
    # USART1/2/3 (MUX7) — from serial_uart_at32f43x.c
    "USART1": 7, "USART2": 7, "USART3": 7,
    # UART4/5 + USART6 + UART7/8 (MUX8)
    "UART4": 8, "UART5": 8, "USART6": 8, "UART7": 8, "UART8": 8,
    # CAN1/2 (MUX9)
    "CAN1": 9, "CAN2": 9,
    # USB OTG (MUX10)
    "OTGFS1": 10, "OTGFS2": 10,
    # Ethernet (MUX11)
    "EMAC": 11,
    # SDIO1 / XMC (MUX12)
    "SDIO1": 12, "XMC": 12,
    # DVP / SDIO2 (MUX13)
    "DVP": 13, "SDIO2": 13,
    # QSPI (MUX14)
    "QSPI1": 14, "QSPI2": 14,
    # System (MUX0)
    "JTMS": 0, "JTCK": 0, "JTDI": 0, "JTDO": 0, "JTRST": 0,
    "SWDIO": 0, "SWCLK": 0, "SWO": 0,
    "CLKOUT1": 0, "CLKOUT2": 0, "IR_OUT": 0,
    # EVENTOUT (MUX15)
    "EVENTOUT": 15,
}

PIN_RE = re.compile(r'^P([A-I]\d{1,2})$')
FUNC_PAT = re.compile(
    r'\b(TMR\d+[_\w]*|SPI\d+[_\w]*|I2S\d+[_\w]*|I2C\d+[_\w]*|'
    r'USART\d+[_\w]*|UART\d+[_\w]*|CAN\d+[_\w]*|'
    r'OTGFS\d+[_\w]*|EMAC[_\w]+|SDIO\d+[_\w]*|'
    r'QSPI\d+[_\w]*|DVP[_\w]+|ADC\w+|DAC\w+|'
    r'ERTC[_\w]*|CLKOUT\d*|IR_OUT|WKUP\d*|'
    r'JTMS|JTCK|JTDI|JTDO|JTRST|SWDIO|SWCLK)\b'
)


def lookup_mux(func_token: str) -> int | None:
    """Return MUX number for a function token, using peripheral prefix matching."""
    if func_token in SIGNAL_TO_MUX:
        return SIGNAL_TO_MUX[func_token]
    # Match by peripheral prefix (e.g. "SPI1_SCK" → "SPI1" → 5)
    for prefix, mux in SIGNAL_TO_MUX.items():
        if func_token.startswith(prefix + "_") or func_token.startswith(prefix + "/"):
            return mux
    return None


def parse_timer_def(path: Path) -> dict:
    """
    Parse timer_def_at32f43x.h to get exact timer MUX assignments.
    Returns: { 'PA5': {'TMR2_CH1': 1, 'TMR8_CH1N': 3, ...}, ... }
    """
    if not path.exists():
        print(f"  WARNING: timer_def not found at {path}", file=sys.stderr)
        return {}

    result = {}
    pat = re.compile(
        r'#define\s+DEF_TIM_AF__P([A-I]\d{1,2})__TCH_(TMR\w+)\s+D\((\d+),\s*\d+\)'
    )
    for line in path.read_text().splitlines():
        m = pat.match(line.strip())
        if not m:
            continue
        pin_suf, func, mux_n = m.group(1), m.group(2), int(m.group(3))
        pin = f"P{pin_suf}"
        result.setdefault(pin, {})[func] = mux_n
        # Also add the _CH1C alias (complementary — datasheet uses CHxC, INAV uses CHxN)
        func_ds = func.replace('CH1N', 'CH1C').replace('CH2N', 'CH2C').replace('CH3N', 'CH3C')
        if func_ds != func:
            result[pin][func_ds] = mux_n
    return result


def parse_pdf_pins() -> dict:
    """
    Extract pin IOMUX function lists from Table 8 in the datasheet PDF.
    Uses pdfplumber table extraction for accurate multi-line cell handling.
    Returns: { 'PA5': ['SPI1_SCK', 'TMR2_CH1', ...], ... }
    """
    try:
        import pdfplumber
    except ImportError:
        sys.exit("pdfplumber not installed. Run: pip install pdfplumber")

    result: dict[str, list[str]] = {}
    # Table 8 spans PDF pages 34-44 (0-indexed: 33-43)
    TABLE_PAGES = range(33, 44)

    print(f"  Extracting pin table from PDF pages 34–44 using pdfplumber table mode...")
    with pdfplumber.open(PDF) as pdf:
        for page_idx in TABLE_PAGES:
            if page_idx >= len(pdf.pages):
                break
            page = pdf.pages[page_idx]
            tables = page.find_tables()
            if not tables:
                continue
            tbl = max(tables, key=lambda t: len(t.extract()))
            rows = tbl.extract()

            for row in rows:
                # Find the pin name cell
                pin = None
                pin_col = None
                for col_idx, cell in enumerate(row):
                    if not cell:
                        continue
                    for word in re.split(r'[\s/\n(]+', str(cell)):
                        if PIN_RE.match(word):
                            pin = word
                            pin_col = col_idx
                            break
                    if pin:
                        break

                if not pin or pin_col is None:
                    continue

                # Collect all function tokens from cells after pin name
                result.setdefault(pin, [])
                for col_offset in range(1, min(5, len(row) - pin_col)):
                    cell = row[pin_col + col_offset]
                    if not cell:
                        continue
                    cell_text = re.sub(r'\s+', ' ', str(cell)).strip()
                    for m in FUNC_PAT.finditer(cell_text):
                        tok = m.group(0)
                        if tok not in result[pin]:
                            result[pin].append(tok)

    return {p: funcs for p, funcs in result.items() if funcs}


def build_pin_table(timer_data: dict, pdf_data: dict) -> dict:
    """
    Merge timer MUX data and PDF IOMUX function lists into:
    { 'PA5': {0: ['CLKOUT1'], 1: ['TMR2_CH1'], 5: ['SPI1_SCK','I2S1_CK'], ...}, ... }
    """
    all_pins: dict[str, dict[int, set]] = {}

    # Timer data (authoritative MUX numbers)
    for pin, funcs in timer_data.items():
        for func, mux_n in funcs.items():
            all_pins.setdefault(pin, {}).setdefault(mux_n, set()).add(func)

    # PDF data with MUX lookup
    for pin, funcs in pdf_data.items():
        for func_token in funcs:
            mux_n = lookup_mux(func_token)
            if mux_n is not None:
                all_pins.setdefault(pin, {}).setdefault(mux_n, set()).add(func_token)

    # Convert sets to sorted lists
    return {pin: {k: sorted(v) for k, v in mux_map.items()}
            for pin, mux_map in all_pins.items()}


def sort_pin(pin: str) -> tuple:
    m = re.match(r'P([A-I])(\d+)', pin)
    return (ord(m.group(1)), int(m.group(2))) if m else (0, 0)


def format_cell(funcs: list) -> str:
    return '/'.join(funcs) if funcs else '-'


def main():
    if not PDF.exists():
        sys.exit(f"PDF not found: {PDF}")

    print("Step 1: Parsing INAV timer_def_at32f43x.h...")
    timer_data = parse_timer_def(INAV_TIMER_DEF)
    print(f"  Found {sum(len(v) for v in timer_data.values())} timer entries "
          f"across {len(timer_data)} pins")

    print("Step 2: Extracting pin data from datasheet PDF...")
    pdf_data = parse_pdf_pins()
    print(f"  Found {len(pdf_data)} pins with IOMUX functions")

    print("Step 3: Building combined pin→MUX table...")
    all_pins = build_pin_table(timer_data, pdf_data)
    sorted_pins = sorted(all_pins.keys(), key=sort_pin)
    print(f"  Total pins with AF data: {len(sorted_pins)}")

    mux_nums = list(range(16))

    # ── MUX Groups Reference ──────────────────────────────────────────────────
    with MUX_OUT.open('w') as f:
        f.write("# AT32F435/437 MUX Group Reference\n\n")
        f.write("Source: AT32F435/437 Reference Manual + INAV driver source\n\n")
        f.write("The AT32F435 uses GPIO_MUXx registers (MUX0–MUX15) to select alternate\n")
        f.write("functions per pin. This is equivalent to STM32's AF0–AF15 numbering.\n\n")
        f.write("| MUX# | Peripheral Group |\n|------|------------------|\n")
        for n, grp in MUX_GROUPS.items():
            f.write(f"| MUX{n:>2} | {grp} |\n")
        f.write("\n## Key Differences from STM32\n\n")
        f.write("- Called 'IOMUX' / 'GPIO_MUX_n' instead of 'AFn'\n")
        f.write("- AT32 has **4 SPI** peripherals (vs 3 on F405/F722)\n")
        f.write("- AT32 has **4 USART + 4 UART = 8** serial ports (vs 6 on F405)\n")
        f.write("- AT32 has **TMR20** (extra advanced timer) on MUX2 or MUX6 depending on pin\n")
        f.write("- AT32 has **QSPI1/QSPI2** on MUX14 (not available on STM32F4)\n")
        f.write("- AT32 DMA uses **DMAMUX** — any DMA channel can serve any peripheral\n")
        f.write("  (no fixed DMA stream/channel conflicts like STM32F4)\n\n")
        f.write("## INAV Default MUX Values\n\n")
        f.write("In INAV target.h, MUX values are NOT specified for standard pin assignments;\n")
        f.write("INAV uses these defaults from the driver source:\n\n")
        f.write("| Peripheral | Default MUX | Override in target.h |\n")
        f.write("|------------|-------------|----------------------|\n")
        f.write("| SPI1, SPI2 | GPIO_MUX_5 | `SPI1_SCK_AF`, `SPI1_MISO_AF`, `SPI1_MOSI_AF` |\n")
        f.write("| SPI3, SPI4 | GPIO_MUX_6 | `SPI3_SCK_AF`, etc. |\n")
        f.write("| I2C1/2/3   | GPIO_MUX_4 | (always MUX4 for I2C) |\n")
        f.write("| USART1/2/3 | GPIO_MUX_7 | `UART1_AF` or `UART1_TX_AF`/`UART1_RX_AF` |\n")
        f.write("| UART4–8    | GPIO_MUX_8 | `UART4_AF` etc. |\n\n")
        f.write("## Timer DEF_TIM() Notes\n\n")
        f.write("In `target.c`, `DEF_TIM(TMR3, CH3, PB0, ...)` automatically resolves\n")
        f.write("the correct MUX number from the `DEF_TIM_AF__PB0__TCH_TMR3_CH3` macro\n")
        f.write("defined in `timer_def_at32f43x.h`. The `af` (flags) parameter in\n")
        f.write("`DEF_TIM` is unused for AT32 (pass 0).\n")
    print(f"Written: {MUX_OUT.name}")

    # ── TSV ───────────────────────────────────────────────────────────────────
    with TSV_OUT.open('w') as f:
        f.write("Pin\t" + "\t".join(f"MUX{n}" for n in mux_nums) + "\n")
        for pin in sorted_pins:
            mux_map = all_pins[pin]
            row = pin + "\t" + "\t".join(
                format_cell(mux_map.get(n, [])) for n in mux_nums
            )
            f.write(row + "\n")
    print(f"Written: {TSV_OUT.name}")

    # ── Markdown ─────────────────────────────────────────────────────────────
    with MD_OUT.open('w') as f:
        f.write("# AT32F435/437 Alternate Function / IOMUX Mapping\n\n")
        f.write("Sources: AT32F437VGT7 Datasheet (Table 8) + INAV timer_def_at32f43x.h\n\n")
        f.write("**Note:** AT32 uses GPIO_MUX_n (MUX0–MUX15) instead of STM32's AF0–AF15.\n")
        f.write("See `mux-groups.md` for the full MUX number → peripheral group reference.\n\n")
        f.write("## MUX Quick Reference\n\n")
        f.write("| MUX# | Peripheral Group |\n|------|------------------|\n")
        for n, grp in MUX_GROUPS.items():
            f.write(f"| MUX{n:>2} | {grp} |\n")
        f.write("\n---\n\n## Pin Alternate Functions\n")

        current_port = None
        for pin in sorted_pins:
            port = pin[:2]
            if port != current_port:
                current_port = port
                f.write(f"\n### Port {port[1]}\n\n")
                f.write("| Pin |" + "".join(f" MUX{n} |" for n in mux_nums) + "\n")
                f.write("|-----|" + "".join("------|" for _ in mux_nums) + "\n")

            mux_map = all_pins[pin]
            row = f"| **{pin}** |" + "".join(
                f" {format_cell(mux_map.get(n, []))} |" for n in mux_nums
            )
            f.write(row + "\n")
    print(f"Written: {MD_OUT.name}")

    # ── Inverted index ────────────────────────────────────────────────────────
    inverted: dict[str, list[str]] = {}
    for pin in sorted_pins:
        for mux_n, funcs in all_pins[pin].items():
            for func in funcs:
                inverted.setdefault(func, []).append(f"{pin}(MUX{mux_n})")

    with INV_OUT.open('w') as f:
        f.write("# AT32F435/437 — Function to Pin Mapping (IOMUX)\n")
        f.write("# Sources: Datasheet Table 8 + INAV timer_def_at32f43x.h\n")
        f.write("# MUX number = GPIO_MUX_n value for gpio_pin_mux_config()\n\n")
        f.write(f"{'Function':<40} Pins\n")
        f.write("-" * 90 + "\n")
        for func in sorted(inverted.keys()):
            pins_str = ", ".join(inverted[func])
            f.write(f"{func:<40} {pins_str}\n")
    print(f"Written: {INV_OUT.name}")

    # Summary
    print(f"\nDone! {len(sorted_pins)} pins, {len(inverted)} unique functions indexed")
    print(f"\nQuick usage examples:")
    print(f"  grep 'SPI1_SCK' af-by-function.txt      # which pins support SPI1_SCK?")
    print(f"  grep '^TMR3_CH' af-by-function.txt       # all TMR3 channel pins")
    print(f"  grep '^USART1' af-by-function.txt        # all USART1 pins")
    print(f"  grep '^PA9\t' alternate-functions.tsv    # PA9 MUX table row")


if __name__ == "__main__":
    main()
