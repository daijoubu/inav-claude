#!/bin/bash
#
# Scan for potentially unsafe cryptographic function usage
#
# This script searches for common cryptographic pitfalls and insecure patterns
# in C/C++ codebases.
#
# Usage: ./scan-crypto-functions.sh [directory]
#
# Example:
#   ./scan-crypto-functions.sh PrivacyLRS/src
#   ./scan-crypto-functions.sh .
#
# Exit codes:
#   0 - No issues found
#   1 - Potential issues found
#   2 - Script error
#

set -euo pipefail

# Default to current directory if not specified
TARGET_DIR="${1:-.}"

if [[ ! -d "$TARGET_DIR" ]]; then
    echo "Error: Directory '$TARGET_DIR' not found" >&2
    exit 2
fi

echo "================================================"
echo "Cryptographic Security Scanner"
echo "================================================"
echo "Scanning: $TARGET_DIR"
echo ""

ISSUES_FOUND=0

# Check for weak/deprecated algorithms
echo "🔍 Checking for weak/deprecated algorithms..."
if grep -r --include="*.c" --include="*.cpp" --include="*.h" \
    -E "(MD5|SHA1|DES|RC4|ECB)" "$TARGET_DIR" 2>/dev/null; then
    echo "⚠️  WARNING: Found usage of weak cryptographic algorithms"
    ISSUES_FOUND=1
else
    echo "✅ No weak algorithms detected"
fi
echo ""

# Check for unsafe random number generation
echo "🔍 Checking for unsafe random number generation..."
if grep -r --include="*.c" --include="*.cpp" \
    -E "\b(rand|srand)\s*\(" "$TARGET_DIR" 2>/dev/null; then
    echo "⚠️  WARNING: Found usage of rand()/srand() - not cryptographically secure"
    echo "   Recommendation: Use cryptographically secure RNG (e.g., arc4random, /dev/urandom)"
    ISSUES_FOUND=1
else
    echo "✅ No unsafe RNG usage detected"
fi
echo ""

# Check for non-constant-time comparison in crypto code
echo "🔍 Checking for potential timing vulnerabilities..."
if grep -r --include="*.c" --include="*.cpp" \
    -A 5 -B 5 "verify\|auth\|mac\|signature" "$TARGET_DIR" 2>/dev/null | \
    grep -E "memcmp|strcmp" 2>/dev/null; then
    echo "⚠️  WARNING: Found memcmp/strcmp in crypto-related code"
    echo "   Recommendation: Use constant-time comparison (e.g., sodium_memcmp)"
    ISSUES_FOUND=1
else
    echo "✅ No obvious timing vulnerabilities detected"
fi
echo ""

# Check for hardcoded secrets
echo "🔍 Checking for hardcoded secrets..."
if grep -r --include="*.c" --include="*.cpp" --include="*.h" \
    -iE "(password|secret|api[_-]?key)\s*=\s*\"" "$TARGET_DIR" 2>/dev/null; then
    echo "⚠️  WARNING: Found potential hardcoded secrets"
    echo "   Recommendation: Use environment variables or secure key storage"
    ISSUES_FOUND=1
else
    echo "✅ No hardcoded secrets detected"
fi
echo ""

# Check for unsafe string functions
echo "🔍 Checking for unsafe string functions..."
if grep -r --include="*.c" --include="*.cpp" \
    -E "\b(strcpy|strcat|sprintf|gets)\s*\(" "$TARGET_DIR" 2>/dev/null; then
    echo "⚠️  WARNING: Found unsafe string functions (buffer overflow risk)"
    echo "   Recommendation: Use strncpy, strncat, snprintf, fgets instead"
    ISSUES_FOUND=1
else
    echo "✅ No unsafe string functions detected"
fi
echo ""

echo "================================================"
if [[ $ISSUES_FOUND -eq 0 ]]; then
    echo "✅ Scan complete: No issues found"
    exit 0
else
    echo "⚠️  Scan complete: Potential issues found (review above)"
    echo "   Note: This is an automated scan - manual review recommended"
    exit 1
fi
