# Project: GitHub Action - PG Version Check

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Automation / CI Enhancement
**Created:** 2026-01-22
**Estimated Effort:** 3-5 hours
**Depends On:** document-parameter-group-system (understanding required)

## Overview

Create a GitHub Action that automatically detects when a pull request modifies parameter group struct definitions and checks whether the PG version was incremented. If a likely breaking change is detected without a corresponding version increment, the action posts a helpful comment reminding the developer to check if a version bump is needed.

## Problem

Developers sometimes forget to increment PG versions when modifying struct definitions, leading to settings corruption on firmware updates (as seen in PR #11236). This is easy to miss in code review and can cause serious user issues.

## Solution

Implement a lightweight GitHub Action that:
1. Detects changes to files containing PG struct definitions
2. Identifies likely breaking changes (field additions/removals/modifications)
3. Checks if the corresponding `PG_REGISTER_WITH_RESET_TEMPLATE` version was incremented
4. Posts a reminder comment if version increment appears missing

**Design Philosophy:**
- Non-blocking: Comment only, don't fail CI
- Conservative: Better to have false positives than miss real issues
- Helpful: Provide context and links to documentation
- Simple: Use grep/regex, not full C parsing

## Implementation

### Phase 1: Detection Logic (2-3 hours)

**Files to Check:**
- `.c` and `.h` files in `src/` that contain `PG_REGISTER`

**Patterns to Detect:**

1. **Struct Definition Changes:**
   - Look for `typedef struct <name>_s {` in diff
   - Check if fields were added/removed/modified within the struct
   - Pattern: Lines with `+` or `-` between struct opening `{` and closing `}`

2. **Version Check:**
   - Find corresponding `PG_REGISTER_WITH_RESET_TEMPLATE(<type>, <name>, <pgn>, <version>)`
   - Extract version number (4th parameter)
   - Check if version number changed in the diff
   - Pattern: `-PG_REGISTER.*,\s*(\d+)\);` vs `+PG_REGISTER.*,\s*(\d+)\);`

**Logic Flow:**
```
For each changed file in PR:
  If file contains PG_REGISTER:
    Extract struct name from PG_REGISTER line
    Check if struct definition changed (fields added/removed/modified)
    If struct changed:
      Check if PG_REGISTER version incremented
      If version NOT incremented:
        Add to list of potential issues

If potential issues found:
  Post single comment with all findings
```

### Phase 2: GitHub Action (1-2 hours)

**Action Triggers:**
- `pull_request` events (opened, synchronize)
- Target: `maintenance-9.x` and `maintenance-10.x` branches

**Implementation Approach:**
- Use bash script with grep/sed for detection
- Use GitHub CLI (`gh`) or octokit for commenting
- Use `github.rest.issues.createComment` API

**Comment Format:**
```markdown
## ⚠️ Parameter Group Version Check

The following parameter groups may need version increments:

### `blackboxConfig_t` (blackbox.c:102)
- **Struct modified:** Field changes detected
- **Version status:** ❌ Not incremented (still version 4)
- **Recommendation:** Review changes and increment version if needed

**Why this matters:**
Modifying PG struct fields without incrementing the version can cause settings
corruption when users flash new firmware. See [Parameter Group Documentation]
(link) for versioning rules.

**When to increment:**
- ✅ Adding fields
- ✅ Removing fields
- ✅ Changing field types
- ✅ Changing field order
- ❌ Only changing default values (no struct change)

---
*This is an automated check. False positives are possible.*
```

### Phase 3: Testing & Refinement (30-60 minutes)

**Test Cases:**
1. PR that adds struct field without version increment (should detect)
2. PR that removes struct field with version increment (should not comment)
3. PR that only changes PG_RESET_TEMPLATE values (should not detect)
4. PR that modifies multiple PG structs (should list all)

## Technical Details

### Detection Algorithm (Pseudocode)

```bash
# Get list of changed files
changed_files=$(gh pr diff $PR_NUMBER --name-only | grep -E '\.(c|h)$')

issues=()

for file in $changed_files; do
  # Check if file has PG registrations
  if grep -q "PG_REGISTER" "$file"; then
    # Get the diff for this file
    diff=$(gh pr diff $PR_NUMBER -- "$file")

    # Find all PG_REGISTER lines and extract struct names
    while read -r pg_line; do
      struct_name=$(echo "$pg_line" | sed -E 's/PG_REGISTER.*\(([^,]+),.*/\1/')

      # Check if this struct was modified
      if struct_modified "$file" "$struct_name" "$diff"; then
        # Check if version was incremented
        if ! version_incremented "$file" "$struct_name" "$diff"; then
          issues+=("$file:$struct_name")
        fi
      fi
    done < <(grep "PG_REGISTER" "$file")
  fi
done

if [ ${#issues[@]} -gt 0 ]; then
  post_comment "$PR_NUMBER" "${issues[@]}"
fi
```

### GitHub Action Workflow File

**Location:** `.github/workflows/pg-version-check.yml`

```yaml
name: Parameter Group Version Check

on:
  pull_request:
    types: [opened, synchronize]
    branches:
      - maintenance-9.x
      - maintenance-10.x

jobs:
  check-pg-versions:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
      contents: read

    steps:
      - name: Checkout PR
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Check PG Versions
        env:
          GH_TOKEN: ${{ github.token }}
          PR_NUMBER: ${{ github.event.pull_request.number }}
        run: |
          bash .github/scripts/check-pg-versions.sh
```

### Detection Script

**Location:** `.github/scripts/check-pg-versions.sh`

Main logic to:
1. Parse PR diff
2. Detect struct changes
3. Check version increments
4. Format and post comment

## Success Criteria

- [ ] GitHub Action workflow file created
- [ ] Detection script implemented and tested
- [ ] Detects struct field additions/removals
- [ ] Checks for corresponding version increments
- [ ] Posts helpful comment with recommendations
- [ ] No false negatives on obvious cases (PR #11236 example)
- [ ] Acceptable false positive rate (<20%)
- [ ] Documentation added to `.github/workflows/README.md`

## Related

- **Prerequisite:** `document-parameter-group-system` (provides versioning rules understanding)
- **PR Example:** [#11236](https://github.com/iNavFlight/inav/pull/11236) - Should have detected missing version increment
- **API Reference:** [GitHub REST API - Create Comment](https://docs.github.com/en/rest/issues/comments#create-an-issue-comment)

## Notes

**Limitations:**
- Uses regex/grep, not full C parsing
- May have false positives for complex macro usage
- Cannot detect all semantic changes (e.g., changing field meaning without changing type)

**Future Enhancements:**
- Parse C structs with proper parser (tree-sitter)
- Track version history to detect wraparound (15→0)
- Check settings.yaml sync with struct changes
- Auto-suggest correct next version number

**Testing Approach:**
- Create test PR in personal fork first
- Verify detection on historical PRs
- Test on PR #11236 scenario (should detect)
