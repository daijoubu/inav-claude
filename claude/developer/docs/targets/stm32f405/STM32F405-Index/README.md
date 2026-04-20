# STM32F405 Datasheet — Search Index

Pre-built keyword index for the STM32F405/F407 datasheet (DS8626, 205 pages).

## Quick Search

```bash
cd ..   # go to stm32f405/
./search_indexes.py DMA
./search_indexes.py SPI
./search_indexes.py --list
```

See `../CLAUDE.md` for full usage and the alternate function reference.

## Index Contents

- **115 keyword index files** in `search-index/`
- **Source PDF:** `../stm32f405-datasheet.pdf` (relative to this directory)
- **Built with:** `claude/developer/scripts/pdfindexer/pdfindexer.py`
- **Config:** `claude/developer/scripts/pdfindexer/stm32f405.yaml`

## Rebuilding

Only needed if you update the PDF or add new keywords:

```bash
cd claude/developer/scripts/pdfindexer
# Add/edit keywords in stm32f405.yaml, then:
./pdfindexer.py --config stm32f405.yaml build-index
```

> ⚠️ Check `search-index/*.txt` first — if files exist, the index is already built.
