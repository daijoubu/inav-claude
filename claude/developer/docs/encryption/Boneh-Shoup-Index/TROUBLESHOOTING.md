# Troubleshooting: PDF Indexing Issues

## Issue: PDF Tools Not Working

If `pdfgrep`, `pdftotext`, or `pdfinfo` don't produce output for the Boneh & Shoup PDF, the PDF may have restrictions or be in a format that requires special handling.

### Symptoms
- `pdfgrep -n "ChaCha20" applied_cryptography-BonehShoup_0_4.pdf` returns no output
- `pdfinfo` returns no information
- `pdftotext` produces no text

### Possible Causes
1. **PDF copy protection** - Some academic PDFs have restrictions
2. **Encrypted PDF** - Password-protected or DRM
3. **Image-only PDF** - Scanned pages without text layer
4. **PDF version incompatibility** - Tools may need updated

### Solutions

#### Option 1: Use the PDF Reader Directly
Since the indexing tools may not work, use the PDF directly:
- Open in a PDF reader (Evince, Okular, Adobe Reader)
- Use the built-in search function (Ctrl+F)
- Navigate using the table of contents
- Bookmark important pages

#### Option 2: Create Manual Reference Index
Create a manual index of important sections:

```bash
cat > Boneh-Shoup-Index/manual-index.md << 'EOF'
# Manual Index - Boneh & Shoup Cryptography Textbook

## Quick Reference by Topic

### Authenticated Encryption
- Chapter X: AEAD Introduction
- Page XXX: GCM Mode
- Page XXX: ChaCha20-Poly1305

### Timing Attacks
- Page XXX: Side Channel Introduction
- Page XXX: Constant-Time Implementation

### Key Derivation
- Page XXX: HKDF
- Page XXX: Key Derivation Functions

[Update as you use the book]
EOF
```

#### Option 3: Try Alternative Tools

```bash
# Try mutool (from mupdf-tools)
sudo apt-get install mupdf-tools
mutool draw -F txt -o output.txt applied_cryptography-BonehShoup_0_4.pdf

# Try extracting with qpdf (removes restrictions)
sudo apt-get install qpdf
qpdf --decrypt applied_cryptography-BonehShoup_0_4.pdf unlocked.pdf
```

#### Option 4: Download Unrestricted Version
Check if there's an unrestricted version available:
- https://crypto.stanford.edu/~dabo/cryptobook/
- Contact authors for unrestricted academic copy

### Workaround: Manual Section Extraction

When you find a relevant section during analysis:

```bash
# Create a notes file
mkdir -p Boneh-Shoup-Index/extracted-notes

# Document the section manually
cat > Boneh-Shoup-Index/extracted-notes/timing-attacks.md << 'EOF'
# Timing Attacks (Pages XXX-XXX)

## Key Points
- [Your notes from the textbook]
- [Important concepts]
- [Relevant to PrivacyLRS because...]

## Application to Code
- Check for constant-time comparisons
- Verify MAC verification timing
EOF
```

### Best Practice: Hybrid Approach

1. **Use PDF reader** with search function for quick lookups
2. **Extract notes** for sections you reference frequently
3. **Build manual index** in `manual-index.md` as you use the book
4. **Reference page numbers** in your security findings reports

### Example Security Analysis Without Automated Index

```bash
# 1. Open PDF in reader
evince applied_cryptography-BonehShoup_0_4.pdf &

# 2. Search for "timing attack" using PDF reader's search (Ctrl+F)

# 3. Read relevant pages, take notes
vim Boneh-Shoup-Index/extracted-notes/timing-attacks.md

# 4. Reference in findings report
# "Non-constant-time MAC verification allows timing attacks (see Boneh & Shoup p.XXX)"
```

## Current Status

✅ **PDF exists** at `claude/developer/docs/encryption/applied_cryptography-BonehShoup_0_4.pdf`
✅ **Index infrastructure ready** (scripts, directories)
⚠️ **Automated indexing** may not work due to PDF restrictions
✅ **Manual reference workflow** described above

## Recommendations

1. **Use the PDF reader** for your primary reference
2. **Extract key sections** manually as you encounter them
3. **Build your own index** in `manual-index.md`
4. **Document page numbers** in security findings
5. **Consider contributing** manual index entries for common topics

Over time, the manual index will become just as useful as an automated one, and it will be specifically tailored to PrivacyLRS security analysis needs.
