# Phase 5: Changelog and Release Notes

**Read this guide when:** Ready to generate changelogs and write release notes

**Note:** This can be done in parallel with artifact download/verification

**Related guides:**
- [Phase 1: Workflow and Preparation](1-workflow-and-preparation.md) - RC Release Pattern
- [Phase 6: Creating Releases](6-creating-releases.md)

---

## Overview

This guide covers generating changelogs from merged PRs, identifying incompatible settings changes, and writing release notes.

---

## Changelog Generation

### List PRs Since Last Tag

#### Using gh pr list

```bash
# Firmware - PRs merged since last tag
cd inav
LAST_TAG=$(git describe --tags --abbrev=0)
gh pr list --state merged --search "merged:>=$(git log -1 --format=%ai $LAST_TAG | cut -d' ' -f1)" --limit 100

# Configurator - same approach
cd inav-configurator
LAST_TAG=$(git describe --tags --abbrev=0)
gh pr list --state merged --search "merged:>=$(git log -1 --format=%ai $LAST_TAG | cut -d' ' -f1)" --limit 100
```

#### Alternative: Using git log

If `gh pr list` is slow or not working, use `git log` to find merge commits:

```bash
# Merged PRs since a specific date
cd inav
git log --since="2024-11-15" --oneline --merges | head -30

# Merged PRs since last tag
LAST_TAG=$(git describe --tags --abbrev=0)
git log $LAST_TAG..HEAD --oneline --merges
```

The merge commit messages include PR numbers (e.g., "Merge pull request #11144").

### Changelog Format

```markdown
## INAV <version> Release Notes

### Firmware Changes

#### New Features
- PR #1234: Description (@contributor)

#### Bug Fixes
- PR #1236: Description (@contributor)

#### Improvements
- PR #1237: Description (@contributor)

### Configurator Changes

#### New Features
- PR #100: Description (@contributor)

### Full Changelog
**Firmware:** https://github.com/iNavFlight/inav/compare/<prev-tag>...<new-tag>
**Configurator:** https://github.com/iNavFlight/inav-configurator/compare/<prev-tag>...<new-tag>
```

### Reviewing Recent Releases for Style

Before writing release notes, review recent releases to match the format and level of detail:

```bash
# View recent releases
gh release list --repo iNavFlight/inav --limit 5
gh release list --repo iNavFlight/inav-configurator --limit 5

# View specific release notes
gh release view 9.0.0-RC2 --repo iNavFlight/inav
```

---

## Identifying Incompatible Settings Changes

**CRITICAL:** Before releasing a major version, identify any CLI settings that have been renamed or removed. These cause errors (shown in RED) when users load their old `diff all` into the new firmware.

### Why This Matters

When users upgrade from INAV 8.x to 9.x, they:
1. Export configuration with `diff all` from old version
2. Flash new firmware
3. Load their old diff into new CLI

If settings were renamed or removed, those lines will fail and show in RED. Users need to know about these incompatibilities upfront.

### How to Find Incompatible Changes

Compare `settings.yaml` between the previous stable release and the new release:

```bash
cd inav

# For major releases (e.g., 8.0.1 → 9.0.0)
git diff 8.0.1..9.0.0-RC3 -- src/main/fc/settings.yaml | grep -E "^[\+\-].*name:"

# Look for:
# - Lines starting with "-" = Settings removed or renamed
# - Lines starting with "+" = New settings or renamed-to names
```

### Using the Automation Script

Save as `claude/release-manager/find-incompatible-settings.sh`:

```bash
#!/bin/bash
# Find incompatible settings between two releases

if [ $# -ne 2 ]; then
    echo "Usage: $0 <old-version> <new-version>"
    echo "Example: $0 8.0.1 9.0.0-RC3"
    exit 1
fi

OLD=$1
NEW=$2

echo "=== Incompatible Settings: $OLD → $NEW ==="
echo ""

cd inav
git diff $OLD..$NEW -- src/main/fc/settings.yaml | \
  grep -E "^[\-].*name:" | \
  grep -v "^\-\-\-" | \
  sed 's/^-.*name: /REMOVED\/RENAMED: /'

echo ""
echo "=== Review git diff for context to determine renames vs removals ==="
```

Run it:

```bash
# From release-manager directory
./find-incompatible-settings.sh 8.0.1 9.0.0-RC3

# Review output and create the renamed/removed lists
# Use git diff to determine renames vs removals
cd inav
git diff 8.0.1..9.0.0-RC3 -- src/main/fc/settings.yaml | less
```

### Creating the Incompatibility Report

Create a document listing:

1. **Renamed settings** - Show old name → new name
2. **Removed settings** - Explain why they were removed
3. **Migration instructions** - How users should update their diff

**Example:** `claude/release-manager/9.0.0-INCOMPATIBLE-SETTINGS.md`

### Where to Document

1. **Release notes** - Add "Incompatible Settings" section
2. **Wiki release notes** - Add to upgrade instructions
3. **Separate document** - For reference during user support

### Common Types of Changes

- **Renamed for clarity:** `controlrate_profile` → `use_control_profile`
- **Terminology changes:** `pid_profile` → `control_profile` (major refactoring)
- **Removed features:** `reboot_character` (legacy MSP method removed)
- **Value format changes:** `pwm2centideg` → `decadegrees` (unit change)

---

## Release Notes Template for Incompatibilities

Add this section to **both firmware and configurator release notes** for major version releases:

```markdown
## ⚠️ Incompatible Settings Changes

The following CLI settings have been renamed or removed in INAV X.0. When loading an older `diff all`, these will show in RED:

**Renamed Settings:**
- `old_setting_name` → `new_setting_name` - Brief explanation
- `another_old_name` → `another_new_name` - Brief explanation

**Removed Settings:**
- `removed_setting` - Reason for removal / what replaced it

**Migration Instructions:**
1. Export configuration from old version: CLI → `diff all` → Save to file
2. Flash new firmware with **Full Chip Erase**
3. Edit your saved diff file and update the renamed settings
4. Load edited diff into new CLI

See full upgrade guide: https://github.com/iNavFlight/inav/wiki/X.0.0-Release-Notes
```

---

## RC Release Notes Pattern

For RC releases, follow the **cumulative** pattern (see [Phase 1: Workflow and Preparation](1-workflow-and-preparation.md#rc-release-pattern-cumulative-approach) for details).

**Key points:**
- Each RC copies all content from previous RC
- Adds new section at top documenting changes since last RC
- Keeps all previous sections intact

**Example for RC3:**

```markdown
# INAV 9.0.0-RC3

## Changes in RC3 (from RC2)
* Fix X
* Fix Y

## Changes in RC2 (from RC1)
* Fix A
* Fix B

[All RC1 content below]
```

---

## Where to Save Release Notes

Create separate files for firmware and configurator:

```
claude/release-manager/
├── 9.0.0-RC3-firmware-release-notes.md
└── 9.0.0-RC3-configurator-release-notes.md
```

These files will be used when creating releases in Phase 6.

---

## Release Notes Checklist

- [ ] Changelog generated for firmware (list of PRs)
- [ ] Changelog generated for configurator (list of PRs)
- [ ] PRs categorized (features, fixes, improvements)
- [ ] Contributors credited
- [ ] **Incompatible settings identified** (for major versions)
- [ ] Incompatible settings section added to release notes
- [ ] RC cumulative pattern followed (if applicable)
- [ ] Release notes saved to files
- [ ] Full changelog links prepared

---

## Next Steps

Once release notes are complete:

**→ Proceed to [Phase 6: Creating Releases](6-creating-releases.md)**
