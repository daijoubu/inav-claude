---
description: Check pull requests for documentation updates and compliance
triggers:
  - check pr docs
  - check pr documentation
  - verify pr docs
  - check documentation
  - pr documentation check
  - docs compliance
  - documentation compliance
---

# Check PR Documentation Compliance

Analyzes recent PRs to verify documentation updates. Checks wiki commits independently (authors may update wiki without mentioning in PR).

## Quick Check

```bash
# Get recent PRs
cd inav && gh pr list --state all --search "created:>=$(date -d '7 days ago' +%Y-%m-%d)"
cd inav-configurator && gh pr list --state all --search "created:>=$(date -d '7 days ago' +%Y-%m-%d)"
```

## Workflow

### Step 1: Get Recent PRs

```bash
cd inav
gh pr list --state all --search "created:>=$(date -d '7 days ago' +%Y-%m-%d)" --json number,title,url,state,author
```

### Step 2: Check Wiki Independently

```bash
# Clone/update wiki
git clone https://github.com/iNavFlight/inav.wiki.git 2>/dev/null || cd inav.wiki && git pull

# Recent wiki commits
git log --since="7 days ago" --pretty=format:"%H|%an|%ai|%s"
```

### Step 3: Check Each PR for Docs

**A. Files modified:**
```bash
gh pr view <PR> --json files --jq '.files[].path' | grep -iE "docs/|README|\.md$"
```

**B. PR description:**
```bash
gh pr view <PR> --json body --jq '.body' | grep -iE "wiki|documentation|#[0-9]+"
```

**C. Wiki commit match:**
```bash
# Direct PR reference
git log --since="7 days ago" --grep="#<PR>"

# Same author, ±2 days
git log --since="7 days ago" --author="<author>" --pretty=format:"%ai|%s"
```

### Step 4: Assess If Docs Needed

**Needs docs:** New features, CLI commands, settings, MSP messages, user-visible changes

**No docs needed:** Internal refactoring, code cleanup, dependency updates, test fixes, bug fixes (no behavior change)

### Step 5: Generate Report

```markdown
## PR Docs Check - YYYY-MM-DD

### inav
✅ Has docs: #1234 (docs/), #1235 (wiki)
⚠️ Needs review: #1236 (new CLI command)
ℹ️ No docs: #1237 (refactor)

### inav-configurator
[Similar]

### Actions
- Tag #1236 as "documentation needed"
```

## Notes

- macOS date: `date -v-7d +%Y-%m-%d`
- Wiki repos: `inav.wiki`, `inav-configurator.wiki`
- Check wiki independently - may not link in PR

## Related

- **pr-review** - Code review
- **wiki-search** - Search wiki
- **check-builds** - Verify builds
