# Cryptography Documentation - Indexed for Quick Search

## What's Here

This directory contains **"A Graduate Course in Applied Cryptography" by Dan Boneh and Victor Shoup** with a searchable index.

The PDF is TOO LARGE to read directly, so you MUST use the index or other tools.

📖 **Quick Start:** Read `QUICK-START.md` for usage and examples

📚 **Full Guide:** Read `Boneh-Shoup-Index/README.md` for complete documentation

## Quick Search — use `search_indexes.py`

`search_indexes.py` is a unified tool that searches the index, then extracts matched pages from the PDF. It works in two phases:
1. **Index lookup** — reads pre-built `search-index/*.txt` files to find page numbers (instant, no PDF tools needed)
2. **Page extraction** — uses `pdftotext` to pull the matched pages from the source PDF

```bash
cd claude/developer/docs/encryption

# Search the index, extract matched pages from PDF
./search_indexes.py ChaCha20

# Index lookup only — fast page listing, skip PDF extraction
./search_indexes.py --no-extract AES

# Add context pages around each match
./search_indexes.py --context 2 timing-attack

# Find keywords by substring
./search_indexes.py --match cipher

# List all available keywords
./search_indexes.py --list
```

## What's Covered

**~800 pages** covering modern applied cryptography including:
- **Symmetric encryption:** AES, ChaCha20, stream ciphers, block ciphers
- **Authenticated encryption:** AEAD, GCM, Poly1305, MAC verification
- **Key exchange:** Diffie-Hellman, ECDH, ephemeral keys
- **Digital signatures:** RSA, Ed25519, elliptic curve cryptography
- **Hashing:** SHA-256, collision resistance, hash functions
- **Security properties:** CPA/CCA security, forward secrecy, semantic security
- **Attacks:** Timing attacks, side channels, padding oracles, replay attacks
- **Protocols:** TLS handshake, CBC/CTR modes, IV handling
- **Key management:** KDF, HKDF, key derivation, key rotation
- **Random number generation:** PRNG, entropy, nonce handling

## Files

```
encryption/
├── CLAUDE.md (this file - quick reference)
├── QUICK-START.md (usage guide)
├── search_indexes.py ← unified search tool (start here)
├── applied_cryptography-BonehShoup_0_4.pdf (~800-page textbook)
└── Boneh-Shoup-Index/
    ├── README.md (complete documentation)
    ├── pdf_indexer.py (per-document search tool)
    ├── chapters/ (extracted chapters)
    ├── relevant-to-privacylrs/ (PrivacyLRS-critical sections)
    └── search-index/ (52 pre-indexed crypto keywords)
```

## Use Cases

**Security analysis and cryptographic code review:**
- Timing attack analysis: `./search_indexes.py timing-attack`
- AEAD implementation review: `./search_indexes.py AEAD`
- Nonce handling: `./search_indexes.py nonce`
- Side-channel risks: `./search_indexes.py side-channel`

**Quick concept lookup:**
- ChaCha20 stream cipher: `./search_indexes.py ChaCha20`
- Poly1305 MAC: `./search_indexes.py Poly1305`
- HKDF key derivation: `./search_indexes.py HKDF`
- Forward secrecy: `./search_indexes.py forward-secrecy`

## PrivacyLRS Relevance

This textbook is critical for security analysis of PrivacyLRS:

⭐⭐⭐ **CRITICAL:**
- Timing attacks and side-channel analysis
- Authenticated encryption (AEAD) protocols
- Nonce handling and IV management
- Random number generation
- Constant-time implementation

⭐⭐ **HIGH:**
- ChaCha20 stream cipher analysis
- Poly1305 MAC verification
- Key derivation (HKDF)
- Forward secrecy properties

See `Boneh-Shoup-Index/README.md` for complete relevance ratings and workflow integration.

## Security Analysis Workflow

When reviewing cryptographic code:

1. **Read the code** - Understand what it does
2. **Search the textbook** - Find relevant concepts:
   ```bash
   cd Boneh-Shoup-Index
   ./pdf_indexer.py find "MAC verification" --context 1
   ```
3. **Analyze** - Apply textbook knowledge to find vulnerabilities
4. **Document** - Reference specific pages in findings reports

## Indexed Keywords

The index includes **50+ cryptography-relevant terms:**

- **Symmetric:** AES, ChaCha20, stream cipher, block cipher, CTR, GCM
- **MACs:** MAC, HMAC, Poly1305, hash function, SHA-256
- **Key Exchange:** Diffie-Hellman, ECDH, key exchange, ephemeral key
- **RNG:** random number, PRNG, entropy, nonce
- **Asymmetric:** RSA, elliptic curve, Ed25519, Curve25519, digital signature
- **Security:** forward secrecy, CPA security, CCA security, semantic security
- **Attacks:** timing attack, side channel, padding oracle, replay attack
- **Key Management:** key derivation, KDF, HKDF, key rotation

## Generic PDF Indexer

This same approach can be used for **any large PDF**. See:

📦 **Generic tool:** `claude/developer/scripts/pdfindexer/`
📖 **Generic tool README:** `claude/developer/scripts/pdfindexer/README.md`

Examples for other documents:
- Microcontroller datasheet: `claude/developer/docs/targets/stm32h7/STM32H7-Index/`
- Aerodynamics textbook: `claude/developer/docs/aerodynamics/Houghton-Carpenter-Index/`
- Any datasheet, RFC, or technical document

## Tools Required

- `pdftotext` and `pdfgrep` (install: `sudo apt-get install poppler-utils pdfgrep`)
- Python 3.6+ (for indexer script)

---

**Start here:** Read `QUICK-START.md` to begin using these tools.
