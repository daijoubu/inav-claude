# Troubleshooting - STM32H7 Documentation Tools

## Common Issues

### 1. pdfgrep or pdftotext Not Found

**Error:**
```
command not found: pdfgrep
command not found: pdftotext
```

**Solution:**
Install poppler-utils:

```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils pdfgrep

# macOS (with Homebrew)
brew install poppler pdfgrep
```

---

### 2. Python Script Fails

**Error:**
```
ModuleNotFoundError: No module named 'yaml'
```

**Solution:**
Install pyyaml (only needed for the generic pdfindexer):

```bash
pip3 install pyyaml
# or
sudo apt-get install python3-yaml
```

---

### 3. PDF Not Found

**Error:**
```
Error: PDF not found at /path/to/stm32h743vi.pdf
```

**Solution:**
Verify the PDF location:

```bash
ls -lh ~/Documents/planes/inavflight/claude/developer/docs/targets/stm32h7/*.pdf
```

The script expects the PDF at:
```
claude/developer/docs/targets/stm32h7/stm32h743vi.pdf
```

---

### 4. Index Build Takes Too Long

**Issue:** Building the index for 100+ keywords is slow.

**Solutions:**

1. **Run in background:**
   ```bash
   ./pdf_indexer.py build-index > build.log 2>&1 &
   tail -f build.log
   ```

2. **Reduce keywords:** Edit `pdf_indexer.py` and comment out keywords you don't need:
   ```python
   MCU_KEYWORDS = [
       # Only keep what you need
       "DMA",
       "SPI",
       "timer",
       # ... etc
   ]
   ```

3. **Use pre-built index:** The index is already built - just use the search-index/ files directly.

---

### 5. No Matches Found

**Issue:** Search returns no results even though the term exists.

**Solutions:**

1. **Try case-insensitive search** (default):
   ```bash
   ./pdf_indexer.py search "dma"  # finds DMA, dma, Dma, etc.
   ```

2. **Check spelling:**
   ```bash
   # Wrong
   ./pdf_indexer.py search "alternte function"

   # Correct
   ./pdf_indexer.py search "alternate function"
   ```

3. **Try broader terms:**
   ```bash
   # Instead of "SPI1_SCK"
   ./pdf_indexer.py search "SPI1"

   # Instead of "TIM1_CH1"
   ./pdf_indexer.py search "TIM1"
   ```

4. **Use pdfgrep directly:**
   ```bash
   pdfgrep -i "your term" ../stm32h743vi.pdf
   ```

---

### 6. Extracted Text is Garbled

**Issue:** Output has weird characters or broken formatting.

**Solutions:**

1. **Use --layout flag** (default):
   ```bash
   ./pdf_indexer.py extract 100 150 --output out.txt
   ```

2. **Try without layout:**
   ```bash
   ./pdf_indexer.py extract 100 150 --no-layout --output out.txt
   ```

3. **Use a PDF reader:** For complex tables/diagrams, open the PDF directly.

---

### 7. Page Numbers Don't Match PDF Reader

**Issue:** Search shows "Page 42" but PDF reader shows different number.

**Explanation:** PDFs can have logical page numbers (i, ii, iii, 1, 2, 3...) vs physical pages.

**Solution:** The tool uses physical page numbers. Count from the first page of the PDF file.

---

## Alternative Workflows

### If Automated Tools Don't Work

You can still use the datasheet effectively:

1. **Open in PDF reader** with search (Ctrl+F)
2. **Use the table of contents** to navigate
3. **Bookmark important pages**
4. **Create manual reference notes:**

```markdown
# STM32H7 Quick Reference (Manual)

## DMA
- Configuration: p. 123-145
- Channel mapping: p. 234
- Request mapping: p. 235-240

## SPI
- Overview: p. 1300-1350
- Registers: p. 1351-1375

## Timers
- General purpose: p. 800-850
- Advanced control: p. 700-750
- Motor control: p. 760-799
```

---

## Manual Index Building

If you prefer to control which terms are indexed:

1. **Edit the keywords list** in `pdf_indexer.py`:

```python
MCU_KEYWORDS = [
    # Add only what you need
    "DMA",
    "SPI",
    "I2C",
    "timer",
    "GPIO",
]
```

2. **Rebuild:**
```bash
./pdf_indexer.py build-index
```

---

## Performance Tips

### For Large Searches

```bash
# Limit output
./pdf_indexer.py search "DMA" | head -50

# Save to file for review
./pdf_indexer.py search "timer" > timer-results.txt
```

### For Repeated Searches

```bash
# Use the pre-built index files directly
cat search-index/DMA.txt
cat search-index/SPI.txt
cat search-index/timer.txt

# Much faster than re-searching!
```

---

## Getting Help

If you encounter issues not covered here:

1. **Check the main README:** `README.md` in this directory
2. **Check generic tool README:** `claude/developer/scripts/pdfindexer/README.md`
3. **Try the cryptography example:** `claude/developer/docs/encryption/Boneh-Shoup-Index/`
4. **Use pdfgrep directly:**
   ```bash
   pdfgrep -n -i "your term" ../stm32h743vi.pdf
   ```

---

## Useful Commands Reference

```bash
# Quick searches
pdfgrep -n "DMA" stm32h743vi.pdf
pdfgrep -n -i "spi" stm32h743vi.pdf  # case-insensitive

# Extract pages
pdftotext -f 100 -l 150 stm32h743vi.pdf output.txt

# PDF info
pdfinfo stm32h743vi.pdf

# Count pages
pdfinfo stm32h743vi.pdf | grep Pages

# Search with context (grep way)
pdfgrep -n -C 3 "DMA" stm32h743vi.pdf
```

---

## Known Limitations

1. **No OCR:** PDF must have embedded text (not scanned images)
2. **Table formatting:** Complex tables may not format well in text extraction
3. **Diagrams:** Cannot extract or search diagrams - use PDF reader
4. **Hyphenation:** Words split across lines may not match searches
5. **Case sensitivity:** Configure with `--case-sensitive` if needed

---

## Success Verification

After setup, verify everything works:

```bash
cd claude/developer/docs/targets/stm32h7/STM32H7-Index

# 1. Check PDF exists
ls -lh ../stm32h743vi.pdf

# 2. Test search
./pdf_indexer.py search "DMA" | head -5

# 3. Check index files
ls -lh search-index/ | head -10

# 4. Test extraction
./pdf_indexer.py extract 1 2 | head -20
```

Expected output:
- PDF file should be ~7.1 MB
- Search should find 200+ occurrences
- Index directory should have 100+ .txt files
- Extraction should show datasheet title page

If all work, your setup is complete!
