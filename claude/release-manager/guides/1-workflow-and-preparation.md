# Phase 1: Release Workflow and Preparation

**Read this guide when:** Starting a new release process

**Related guides:**
- Phase 2: [Downloading Artifacts](2-downloading-artifacts.md)
- Phase 3: [Verifying Artifacts](3-verifying-artifacts.md)
- Phase 4: [Building Locally](4-building-locally.md)
- Phase 5: [Changelog and Notes](5-changelog-and-notes.md)
- Phase 6: [Creating Releases](6-creating-releases.md)

---

## Overview

This guide covers the complete release workflow and preparation steps you need to complete before starting artifact downloads and builds.

## Release Workflow

**IMPORTANT:** Verify builds BEFORE creating tags. Never tag a commit that hasn't been proven to build successfully.

```
1. Verify release readiness
   ├── All PRs merged to firmware repo
   ├── Version number updated in firmware (CMakeLists.txt)
   └── CI passing on firmware target commit

2. Configurator version bump PR
   ├── Create PR branch with version bump (package.json)
   ├── This PR will also receive SITL binaries in step 4
   └── Do NOT merge yet - wait for SITL update

3. Download firmware artifacts
   ├── Download firmware hex files from CI
   ├── Download SITL binaries from same CI run
   ├── Build Linux x64 SITL locally if needed (for glibc compatibility)
   └── This provides SITL binaries needed for configurator

4. Update SITL in configurator (same PR as step 2)
   ├── Add SITL binaries as additional commit to version bump PR
   ├── Wait for configurator CI to pass
   └── Merge the combined version bump + SITL PR

5. Download configurator artifacts
   ├── Download from CI run after combined PR merged
   ├── Verify macOS DMGs (no cross-platform contamination)
   ├── Verify Windows SITL (cygwin1.dll present)
   ├── Verify Linux SITL (glibc <= 2.35)
   └── Test SITL functionality

6. Generate changelog
   ├── List PRs since last tag
   ├── Categorize changes
   ├── **Identify incompatible settings** (./find-incompatible-settings.sh)
   └── Format release notes

7. Create tags and draft releases (ONLY after artifacts verified)
   ├── Create draft release for firmware (targeting verified commit)
   ├── Create tag + draft release tag for configurator (targeting verified commit)
   ├── Upload verified artifacts
   └── Add release notes

8. Review and publish
   ├── Final review of draft releases
   ├── Maintainer approval
   ├── Add tag to drafty release
   └── Publish releases
```

**Why this order matters:** If you tag first and then discover the build is broken, you have a tag pointing to a broken commit. By verifying artifacts first, you only tag commits that are proven to work.

---

## RC Release Pattern (Cumulative Approach)

Release Candidates (RC) follow a **cumulative** pattern where each RC builds on the previous one:

### Release Notes Structure

#### For Each RC Release:
1. **Copy all content from previous RC** release notes
2. **Add new section** at the top documenting changes since last RC
3. **Keep all previous sections** intact

Example progression:

**RC1 Release Notes:**
```
# INAV 9.0.0-RC1

[All new features for 9.0.0]
```

**RC2 Release Notes:**
```
# INAV 9.0.0-RC2

## Changes in RC2 (from RC1)
* Fix A
* Fix B

[All RC1 content below]
```

**RC3 Release Notes:**
```
# INAV 9.0.0-RC3

## Changes in RC3 (from RC2)
* Fix X
* Fix Y

## Changes in RC2 (from RC1)
* Fix A
* Fix B

[All RC1 content below]
```

**Final 9.0.0 Release:**
```
# INAV 9.0.0

## Changes in 9.0.0 (from RC3)
* Final fix 1
* Final fix 2

## Changes in RC3 (from RC2)
[RC3 changes]

## Changes in RC2 (from RC1)
[RC2 changes]

[All RC1 content below]
```

### Wiki Release Notes

The `inavwiki/X.Y.Z-Release-Notes.md` file is continuously updated:
- RC1 creates the initial document
- RC2 adds a "Changes in RC2" section at the top
- RC3 adds a "Changes in RC3" section
- Final release adds final changes section

### GitHub Releases

Both firmware and configurator GitHub releases follow the same cumulative pattern:
- Each RC copies the previous RC notes
- Adds incremental changes section
- Updates "Full Changelog" link to compare against previous RC

### Example References

- Configurator RC1: https://github.com/iNavFlight/inav-configurator/releases/tag/9.0.0-RC1
- Firmware RC2: https://github.com/iNavFlight/inav/releases/tag/9.0.0-RC2
- Wiki (continuous): https://github.com/iNavFlight/inav/wiki/9.0.0-Release-Notes

---

## Pre-Release Checklist

### Code Readiness

- [ ] All planned PRs merged
- [ ] CI passing on master branch
- [ ] No critical open issues blocking release
- [ ] Version numbers updated in both repositories
- [ ] SITL binaries updated in configurator

### Documentation

- [ ] Release notes drafted
- [ ] **Incompatible settings changes identified and added to release notes** (use find-incompatible-settings.sh)
- [ ] Breaking changes documented
- [ ] New features documented

### Artifact Verification

- [ ] Firmware hex files downloaded and renamed
- [ ] Configurator artifacts organized by platform (linux/, macos/, windows/)
- [ ] macOS DMG contents verified (no .exe files, correct architecture)
- [ ] **Windows SITL cygwin1.dll verified** (use verify-windows-sitl.sh)
- [ ] **Configurator SITL tested** (launch SITL, verify version matches firmware)

---

## Post-Release Tasks

- [ ] Announce release (Discord, forums, etc.)
- [ ] Update any pinned issues
- [ ] Monitor for critical bug reports
- [ ] Prepare hotfix if needed
- [ ] Update this document with any lessons learned

---

## Next Steps

Once you've verified release readiness:

**→ Proceed to [Phase 2: Downloading Artifacts](2-downloading-artifacts.md)**
