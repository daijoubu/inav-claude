# Quick Start Guide - Cryptography PDF Tools

## What You Have

✅ **800-page cryptography textbook (Boneh & Shoup) available for reference**
✅ **Indexing scripts ready** (may need manual fallback - see TROUBLESHOOTING.md)
✅ **Python script for searching** (if PDF allows)
⚠️ **Note:** If automated tools don't work, use PDF reader + manual index (see below)

## 3 Fastest Ways to Find Information

### 1. Search the Pre-Built Index (Fastest)
```bash
cd claude/developer/docs/encryption/Boneh-Shoup-Index/search-index

# View all occurrences of "ChaCha20"
cat ChaCha20.txt

# View all occurrences of "timing attack"
cat timing-attack.txt

# View all occurrences of "authenticated encryption"
cat authenticated-encryption.txt
```

### 2. Search for Any Term (Quick)
```bash
cd claude/developer/docs/encryption

# Search and show page numbers
pdfgrep -n "your search term" applied_cryptography-BonehShoup_0_4.pdf

# Examples:
pdfgrep -n "nonce reuse" applied_cryptography-BonehShoup_0_4.pdf
pdfgrep -n "constant time" applied_cryptography-BonehShoup_0_4.pdf
pdfgrep -n "forward secrecy" applied_cryptography-BonehShoup_0_4.pdf
```

### 3. Use the Python Script (Most Powerful)
```bash
cd claude/developer/docs/encryption/Boneh-Shoup-Index

# Search with context
./pdf_indexer.py find "GCM mode" --context 1

# Extract specific pages
./pdf_indexer.py extract 200 250 --output temp-extract.txt

# Simple search
./pdf_indexer.py search "Poly1305"
```

## Extract Key Sections for PrivacyLRS Reference

```bash
cd claude/developer/docs/encryption

# Example: Extract authenticated encryption chapter
./Boneh-Shoup-Index/pdf_indexer.py extract 300 350 \
  --output Boneh-Shoup-Index/relevant-to-privacylrs/authenticated-encryption.txt

# Example: Extract timing attack section
./Boneh-Shoup-Index/pdf_indexer.py find "timing attack" --context 2 \
  > Boneh-Shoup-Index/relevant-to-privacylrs/timing-attacks.txt
```

## Most Relevant Topics for PrivacyLRS Security Analysis

| Topic | Relevance | Use in Security Analysis |
|-------|-----------|--------------------------|
| ChaCha20 | HIGH | Stream cipher analysis, performance review |
| Poly1305 | HIGH | MAC verification, authenticated encryption |
| Timing attacks | CRITICAL | Side-channel analysis, constant-time review |
| Authenticated encryption (AEAD) | CRITICAL | Protocol design review |
| Key derivation (HKDF) | HIGH | Key management review |
| Nonce handling | CRITICAL | Implementation correctness |
| Forward secrecy | HIGH | Protocol security properties |
| Random number generation | CRITICAL | Cryptographic strength |

## Pre-Indexed Keywords

All in `search-index/` directory (counts will vary):

**Symmetric Encryption:**
- `AES.txt`
- `ChaCha20.txt`
- `stream-cipher.txt`
- `block-cipher.txt`
- `CTR-mode.txt`
- `GCM.txt`

**Authentication:**
- `MAC.txt`
- `HMAC.txt`
- `Poly1305.txt`
- `authenticated-encryption.txt`
- `AEAD.txt`

**Security Properties:**
- `CPA-security.txt`
- `CCA-security.txt`
- `forward-secrecy.txt`
- `semantic-security.txt`

**Attacks:**
- `timing-attack.txt`
- `side-channel.txt`
- `padding-oracle.txt`
- `replay-attack.txt`
- `man-in-the-middle.txt`

**Key Management:**
- `key-derivation.txt`
- `KDF.txt`
- `HKDF.txt`
- `nonce.txt`
- `entropy.txt`

... and many more!

## Files Created

```
claude/developer/docs/encryption/
├── applied_cryptography-BonehShoup_0_4.pdf (26 MB, ~800 pages)
├── QUICK-START.md (this file)
└── Boneh-Shoup-Index/
    ├── README.md (index guide with PrivacyLRS relevance ratings)
    ├── pdf_indexer.py (Python indexing tool)
    ├── chapters/ (for extracted chapters)
    ├── relevant-to-privacylrs/ (PrivacyLRS-critical sections)
    └── search-index/ (50+ pre-indexed crypto keywords)
        ├── ChaCha20.txt
        ├── timing-attack.txt
        ├── authenticated-encryption.txt
        └── ... (50+ more)
```

## Usage in Security Analysis

### When Reviewing Cryptographic Code

1. **Read the code** to understand what it does
2. **Search the textbook** for relevant concepts:
   ```bash
   ./pdf_indexer.py find "MAC verification" --context 2
   ```
3. **Extract key sections** for reference while analyzing
4. **Document findings** with references to specific pages

### Example Workflow

```bash
# 1. You're reviewing MAC verification in auth.c

# 2. Search for timing attack information
cd claude/developer/docs/encryption/Boneh-Shoup-Index
./pdf_indexer.py find "timing attack" --context 1 > /tmp/timing-ref.txt

# 3. Read the reference
cat /tmp/timing-ref.txt

# 4. Check if code uses constant-time comparison
grep "memcmp\|sodium_memcmp" PrivacyLRS/src/auth.c

# 5. Document finding with textbook reference
# "See Boneh & Shoup p.XXX on timing attacks"
```

## Next Steps

1. Browse the search index: `ls -lh Boneh-Shoup-Index/search-index/`
2. Search for terms relevant to your security analysis
3. Extract sections you need frequently
4. Build PrivacyLRS-specific reference documentation from extracted sections

## Tips

- **For quick lookups:** Use the pre-built index files
- **For exploration:** Use `pdfgrep` to search
- **For reading:** Extract sections to text with `pdftotext -layout`
- **For analysis:** Use the Python script to extract with context
- **For findings reports:** Reference specific page numbers (e.g., "See Boneh & Shoup p.XXX")
