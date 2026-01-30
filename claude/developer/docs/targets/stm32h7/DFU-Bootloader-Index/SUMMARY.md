# DFU/Bootloader Index Creation Summary

## What Was Created

A searchable index for the STM32 DFU/bootloader application note (AN2606) - a 517-page document covering system memory boot mode for all STM32 families.

## Index Details

- **Document:** AN2606 "Introduction to system memory boot mode on STM32 MCUs"
- **Size:** 517 pages, 6.8 MB
- **Keywords indexed:** 110 DFU/bootloader-specific terms
- **Matches found:** Thousands across bootloader, USB DFU, boot modes, protocols, etc.

## Most Useful Indexes

For H743 DFU reboot investigation:
- `search-index/bootloader.txt` - 1599 matches
- `search-index/DFU.txt` - 433 matches
- `search-index/USB-DFU.txt` - 36 matches
- `search-index/STM32H7.txt` - 146 matches
- `search-index/system-memory.txt` - 423 matches
- `search-index/boot-mode.txt` - 437 matches
- `search-index/reset.txt` - 248 matches
- `search-index/NVIC-SystemReset.txt` - 1 match

## Quick Usage

```bash
cd claude/developer/docs/targets/stm32h7/DFU-Bootloader-Index

# View pre-indexed results (fastest)
cat search-index/H743.txt
cat search-index/DFU.txt

# Search for new terms
./pdf_indexer.py search "your term"

# Search with context
./pdf_indexer.py find "DFU mode" --context 2

# Extract specific pages
./pdf_indexer.py extract 200 250 --output h7-section.txt
```

## Related Documents

In the parent directory:
- **STM32H7-Index/** - H743 datasheet index (pinouts, electrical specs)
- **STM32Ref-Index/** - Reference manual index (registers, peripherals)
- **DFU-Bootloader-Index/** - This directory (bootloader configuration)

## Sandbox Compatibility Fixes

All pdf_indexer.py scripts were updated to work in the Claude sandbox environment:

**Fixed scripts:**
1. `/claude/developer/docs/targets/stm32h7/DFU-Bootloader-Index/pdf_indexer.py` ✅
2. `/claude/developer/docs/targets/stm32h7/STM32H7-Index/pdf_indexer.py` ✅
3. `/claude/developer/docs/targets/stm32h7/STM32Ref-Index/pdf_indexer.py` ✅
4. `/claude/developer/docs/aerodynamics/Houghton-Carpenter-Index/pdf_indexer.py` ✅
5. `/claude/developer/docs/encryption/Boneh-Shoup-Index/pdf_indexer.py` ✅

**Problem:** Scripts used `capture_output=True` with subprocess.run(), which doesn't work in sandbox.

**Solution:** Changed to use temporary files for stdout redirection:
- pdfgrep output → temp file → read results
- pdftotext output → temp file → read text

All scripts now work correctly in the sandboxed environment.

## Files Created

- `DFU-Bootloader-Index/pdf_indexer.py` - Indexing tool (110 keywords)
- `DFU-Bootloader-Index/README.md` - Complete usage documentation
- `DFU-Bootloader-Index/search-index/*.txt` - 110 pre-built keyword indexes
- `DFU-Bootloader-Index/index-build.log` - Build log
- `DFU-Bootloader-Index/SUMMARY.md` - This file

## Next Steps

For the H743 DFU reboot investigation task:
1. Read `search-index/H743.txt` to find H743-specific bootloader info
2. Read `search-index/system-memory-address.txt` for bootloader address
3. Read `search-index/USB-DFU.txt` for USB DFU mode details
4. Search for specific issues: `./pdf_indexer.py find "timeout" --context 2`

## Date Created

2026-01-26
