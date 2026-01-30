# Quick Start Guide - Cryptography PDF Tools

## What You Have

✅ **~800-page cryptography textbook (Boneh & Shoup) indexed and ready**
✅ **52 crypto-relevant keywords pre-indexed**
✅ **`search_indexes.py` — two-phase search tool (index lookup + page extraction)**

## How It Works

`search_indexes.py` uses a two-phase approach:

1. **Phase 1 — Index lookup** (instant): Reads the pre-built `search-index/*.txt` files to find which pages mention your keyword, with a snippet of matched text.
2. **Phase 2 — Page extraction** (uses pdftotext): Extracts only the matched pages from the PDF so you can read the surrounding content.

If a keyword has too many results (>20 by default), Phase 2 is skipped automatically — the script warns you and suggests a more specific keyword or `--max N`.

## Basic Usage

```bash
cd claude/developer/docs/encryption

# Search index + extract matched pages (full workflow)
./search_indexes.py ChaCha20

# Phase 1 only — fast page listing, no PDF extraction
./search_indexes.py --no-extract AES

# Add context pages around each match
./search_indexes.py --context 2 timing-attack

# Browse available keywords
./search_indexes.py --list
./search_indexes.py --match cipher
```

## Most Relevant Topics for PrivacyLRS Security Analysis

| Topic | Relevance | Index Keyword | Use in Security Analysis |
|-------|-----------|---------------|--------------------------|
| Timing attacks | CRITICAL | `timing-attack` | Side-channel analysis, constant-time review |
| Authenticated encryption | CRITICAL | `AEAD`, `authenticated-encryption` | Protocol design review |
| Nonce handling | CRITICAL | `nonce` | Implementation correctness |
| Random number gen | CRITICAL | `PRNG`, `entropy` | Cryptographic strength |
| ChaCha20 | HIGH | `ChaCha20` | Stream cipher analysis |
| Poly1305 | HIGH | `Poly1305` | MAC verification |
| Key derivation | HIGH | `HKDF`, `KDF` | Key management review |
| Forward secrecy | HIGH | `forward-secrecy` | Protocol security properties |

## Pre-Indexed Keywords

Browse with `./search_indexes.py --list` or search by substring with `--match`:

**Symmetric Encryption:** `AES`, `ChaCha20`, `stream-cipher`, `block-cipher`, `CTR-mode`, `GCM`

**Authentication:** `MAC`, `HMAC`, `Poly1305`, `authenticated-encryption`, `AEAD`

**Security Properties:** `CPA-security`, `CCA-security`, `forward-secrecy`, `semantic-security`

**Attacks:** `timing-attack`, `side-channel`, `padding-oracle`, `replay-attack`, `man-in-the-middle`

**Key Management:** `key-derivation`, `KDF`, `HKDF`, `key-rotation`, `key-schedule`, `nonce`, `entropy`

**Asymmetric / Signatures:** `RSA`, `elliptic-curve`, `Ed25519`, `Curve25519`, `digital-signature`, `ECDH`, `Diffie-Hellman`

## Security Analysis Workflow

```bash
# 1. You're reviewing MAC verification in auth.c

# 2. Search textbook for relevant concepts
cd claude/developer/docs/encryption
./search_indexes.py timing-attack

# 3. Check if code uses constant-time comparison
grep "memcmp\|sodium_memcmp" PrivacyLRS/src/auth.c

# 4. Document finding with textbook reference
# "See Boneh & Shoup p.XXX on timing attacks"
```

## Files

```
claude/developer/docs/encryption/
├── search_indexes.py ← start here
├── CLAUDE.md (quick reference)
├── QUICK-START.md (this file)
├── applied_cryptography-BonehShoup_0_4.pdf (26 MB, ~800 pages)
└── Boneh-Shoup-Index/
    ├── README.md (index guide with PrivacyLRS relevance ratings)
    ├── pdf_indexer.py (per-document search tool)
    ├── relevant-to-privacylrs/ (PrivacyLRS-critical sections)
    └── search-index/ (52 pre-indexed crypto keywords)
```

## Tips

- **Start with `search_indexes.py`** — it reads the index first (instant), then extracts only the pages you need
- **Use `--no-extract`** for quick page listings when you just need to know where something is
- **Use `--match`** to discover keyword names (e.g., `--match key` finds `key-derivation`, `key-rotation`, `key-schedule`, etc.)
- **Use `--context N`** when you need surrounding pages for full theoretical understanding
- **For findings reports:** Reference specific page numbers (e.g., "See Boneh & Shoup p.XXX")
