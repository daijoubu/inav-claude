# Security Analysis Scripts Library

This directory contains reusable security analysis tools and scripts.

## Directory Structure

- **scanning/** - Automated security scanning scripts
- **analysis/** - Code analysis utilities and helpers
- **testing/** - Security test harnesses and validation tools

## Purpose

Build a toolkit of reusable security analysis scripts to make future analyses faster and more thorough.

## Guidelines

**When adding scripts:**

1. Include a docstring explaining purpose and usage
2. Make scripts executable: `chmod +x script.py`
3. Add example usage in script header
4. Document dependencies and requirements
5. Use descriptive filenames

**Example script template:**

```python
#!/usr/bin/env python3
"""
Brief description of what this script does.

Usage: ./script.py <args>

Example:
    ./script.py PrivacyLRS/src --check-timing

Dependencies:
    - Python 3.9+
    - tree-sitter (for AST parsing)
"""
```

**Common script types:**

- Vulnerability scanners (e.g., `check-timing-attacks.py`)
- Code pattern analyzers (e.g., `find-crypto-usage.py`)
- Test harnesses (e.g., `test-mac-verification.py`)
- Data extraction tools (e.g., `extract-crypto-params.py`)

## Maintenance

- Keep scripts up to date with codebase changes
- Add new scripts when you write analysis tools
- Document any breaking changes
- Consider making scripts project-agnostic when possible
