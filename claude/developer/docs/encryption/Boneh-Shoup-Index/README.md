# Boneh & Shoup Cryptography Textbook Index

## Overview

This directory contains tools and indexes for searching the 800-page "A Graduate Course in Applied Cryptography" by Dan Boneh and Victor Shoup.

**Purpose:** Enable quick lookup of cryptographic concepts during security analysis.

---

## Directory Structure

```
Boneh-Shoup-Index/
├── README.md (this file)
├── pdf_indexer.py (Python indexing tool)
├── chapters/ (extracted chapters)
├── relevant-to-privacylrs/ (PrivacyLRS-critical sections)
└── search-index/ (pre-indexed crypto keywords)
    ├── ChaCha20.txt
    ├── timing-attack.txt
    ├── authenticated-encryption.txt
    └── ... (50+ more)
```

---

## Quick Start

⚠️ **Note:** If automated indexing doesn't work with this PDF, see `TROUBLESHOOTING.md` for manual reference workflow.

### 1. Try Building the Search Index

First time setup - attempt to build the keyword index:

```bash
cd claude/developer/docs/encryption/Boneh-Shoup-Index
./pdf_indexer.py build-index
```

If this works, it will create index files for 50+ cryptography keywords.

**If it doesn't work:** Use the PDF reader directly and build a manual index (see TROUBLESHOOTING.md).

### 2. Search for a Term

```bash
# Simple search
./pdf_indexer.py search "ChaCha20"

# Search with context
./pdf_indexer.py find "timing attack" --context 2
```

### 3. Extract Pages

```bash
# Extract specific pages
./pdf_indexer.py extract 200 250 --output temp-extract.txt
```

---

## Indexed Keywords

The indexer searches for these cryptography-relevant terms:

**Symmetric Encryption:**
- AES, ChaCha20, stream cipher, block cipher
- CTR mode, GCM, authenticated encryption, AEAD

**MACs and Hashing:**
- MAC, HMAC, Poly1305, hash function
- SHA-256, collision resistance

**Key Exchange:**
- Diffie-Hellman, ECDH, key exchange
- ephemeral key, key agreement

**Random Number Generation:**
- random number, PRNG, entropy, nonce

**Asymmetric Crypto:**
- RSA, elliptic curve, Ed25519, Curve25519
- digital signature

**Security Properties:**
- forward secrecy, CPA security, CCA security
- semantic security, IND-CPA, IND-CCA

**Attacks:**
- timing attack, side channel, padding oracle
- replay attack, man-in-the-middle
- chosen plaintext, chosen ciphertext

**Key Management:**
- key derivation, KDF, HKDF
- key rotation, key schedule

**Protocols:**
- CBC mode, ECB mode, initialization vector
- IV, TLS, handshake

---

## Usage in Security Analysis

### Workflow Integration

When analyzing cryptographic code:

1. **Read the code** - Understand what it does
2. **Search the textbook** - Find relevant concepts:
   ```bash
   ./pdf_indexer.py find "MAC verification" --context 1
   ```
3. **Analyze** - Apply textbook knowledge to find vulnerabilities
4. **Document** - Reference specific pages in findings reports

### Example: Reviewing MAC Verification

```bash
# Step 1: You find MAC verification code in PrivacyLRS

# Step 2: Search for timing attack information
cd claude/developer/docs/encryption/Boneh-Shoup-Index
./pdf_indexer.py find "timing attack" --context 1 > /tmp/timing-ref.txt

# Step 3: Read reference material
cat /tmp/timing-ref.txt

# Step 4: Check code for constant-time comparison
grep "memcmp" PrivacyLRS/src/crypto/verify.c

# Step 5: Document finding with textbook page reference
# "Non-constant-time MAC verification (see Boneh & Shoup p.XXX)"
```

---

## PrivacyLRS Relevance Ratings

| Topic | Relevance | Use Case |
|-------|-----------|----------|
| Timing attacks | CRITICAL | Side-channel analysis |
| Authenticated encryption (AEAD) | CRITICAL | Protocol review |
| Nonce handling | CRITICAL | Implementation review |
| Random number generation | CRITICAL | Crypto strength |
| ChaCha20 | HIGH | Stream cipher analysis |
| Poly1305 | HIGH | MAC verification |
| Key derivation (HKDF) | HIGH | Key management |
| Forward secrecy | HIGH | Protocol security |

---

## Extracting Sections for Reference

### Extract AEAD Chapter

```bash
# Find AEAD first
./pdf_indexer.py search "authenticated encryption" | head -20

# Extract relevant pages (example page numbers)
./pdf_indexer.py extract 300 350 \
  --output relevant-to-privacylrs/authenticated-encryption.txt
```

### Extract Timing Attack Section

```bash
./pdf_indexer.py find "timing attack" --context 2 \
  > relevant-to-privacylrs/timing-attacks.txt
```

### Build PrivacyLRS Reference Library

Create focused reference documents:

```bash
mkdir -p relevant-to-privacylrs

# Extract key topics
./pdf_indexer.py find "ChaCha20" --context 1 \
  > relevant-to-privacylrs/chacha20-reference.txt

./pdf_indexer.py find "Poly1305" --context 1 \
  > relevant-to-privacylrs/poly1305-reference.txt

./pdf_indexer.py find "constant time" --context 1 \
  > relevant-to-privacylrs/constant-time-implementation.txt
```

---

## Tools Required

- `pdftotext` - Extract text from PDF
- `pdfgrep` - Search PDF contents
- `pdfinfo` - PDF metadata
- Python 3.6+

Install on Ubuntu/Debian:
```bash
sudo apt-get install poppler-utils pdfgrep
```

---

## Notes

- **First search may be slow** - Large 800-page PDF
- **Index files speed up repeated searches**
- **Page numbers** - Reference these in security findings reports
- **Extract frequently-used sections** - Faster than searching each time

---

## See Also

- `claude/developer/docs/encryption/QUICK-START.md` - Quick reference guide
- `claude/security-analyst/guides/crypto-review-guide.md` - How to use this during crypto review
