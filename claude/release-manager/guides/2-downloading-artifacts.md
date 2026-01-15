# Phase 2: Downloading Release Artifacts

**Read this guide when:** You're ready to download firmware and configurator artifacts for a release

**Prerequisites:** Phase 1 checklist completed (PRs merged, CI passing, version numbers updated)

**Related guides:**
- [Phase 1: Workflow and Preparation](1-workflow-and-preparation.md)
- [Phase 3: Verifying Artifacts](3-verifying-artifacts.md)

---

## Overview

This guide covers downloading firmware hex files from inav-nightly and configurator builds from GitHub Actions CI. Proper organization during download prevents cross-platform contamination.

---

## Key Principles

- **Firmware hex files** come from inav-nightly releases
- **Configurator builds** come from GitHub Actions CI artifacts
- **CRITICAL: Organize configurator builds by platform** (linux/, macos/, windows/) to prevent cross-platform contamination
- **NEVER flatten directories** containing multiple platforms together
- **Rename firmware files** before upload: remove `_ci-YYYYMMDD-hash` suffix, add RC number for RC releases

**Lesson learned (9.0.0 release):** A Windows .exe file was found inside a Mac DMG. The exact cause is unknown, but improper artifact handling during download/preparation is suspected. Platform separation and verification steps prevent this.

---

## Artifact Download Timing

**IMPORTANT:** You can download CI artifacts for a specific commit BEFORE creating the release tag.

### How It Works

1. **Commits are immutable** - Once a commit exists, it has a unique SHA
2. **CI runs on commits** - GitHub Actions builds artifacts for each commit automatically
3. **Tags point to commits** - A tag is just a named pointer to a specific commit

### Benefits

- Download and verify artifacts while repositories are locked
- Organize and rename files in advance
- Verify DMG contents thoroughly
- Create releases when ready without rushing

---

## Downloading Firmware Artifacts

Firmware uses nightly builds instead of CI artifacts:

### Step 1: Get Target Commit SHA

```bash
# Get commit SHA from firmware repo
cd inav
gh api repos/iNavFlight/inav/commits/HEAD --jq '{sha: .sha, date: .commit.committer.date}'
```

### Step 2: Find Matching Nightly Build

```bash
# List recent nightly builds
gh release list --repo iNavFlight/inav-nightly --limit 20
```

Look for the nightly build created after your target commit date. Nightly tags follow format: `v9.0.0-YYYYMMDD.BUILD_NUMBER`

### Step 3: Download Firmware Hex Files

```bash
# Download all hex files from the nightly release
gh release download v9.0.0-20251207.178 --repo iNavFlight/inav-nightly --pattern "*.hex" -D downloads/firmware-9.0.0-RC3/
```

### Step 4: Download SITL Binaries

```bash
# Download SITL resources from the same nightly
gh release download v9.0.0-20251207.178 --repo iNavFlight/inav-nightly --pattern "sitl-resources.zip" -D downloads/sitl-9.0.0-RC3/

# Extract SITL binaries
cd downloads/sitl-9.0.0-RC3/
unzip sitl-resources.zip
```

The SITL binaries will be needed for the configurator (Phase 4: Building Locally).

### Step 5: Rename Firmware Files

Use the rename script to remove CI build suffixes and add RC numbers:

```bash
# For RC releases
./claude/release-manager/rename-firmware-for-release.sh 9.0.0-RC3 downloads/firmware-9.0.0-RC3/

# For final releases
./claude/release-manager/rename-firmware-for-release.sh 9.0.0 downloads/firmware-9.0.0/
```

**Example transformation:**
- Before: `inav_9.0.0_MATEKF405_ci-20251129-abc123.hex`
- After: `inav_9.0.0_RC3_MATEKF405.hex`

---

## Downloading Configurator Artifacts

Configurator builds come from GitHub Actions CI.

### Step 1: Find Target Commit

```bash
# Get commit SHA from configurator repo
cd inav-configurator
gh api repos/iNavFlight/inav-configurator/commits/HEAD --jq '.sha'
# Output: 9dbd346dcf941b31f97ccb8418ede367044eb93c
```

### Step 2: Find CI Run for That Commit

```bash
# Find the CI workflow run for the target commit
gh run list --repo iNavFlight/inav-configurator --limit 20 --json headSha,databaseId,status,conclusion | \
  jq '.[] | select(.headSha == "9dbd346dcf941b31f97ccb8418ede367044eb93c")'
```

Note the `databaseId` - this is your `<run-id>`.

### Step 3: Download Artifacts

**CRITICAL:** Download to separate directories by platform to prevent contamination.

```bash
# Create platform-specific directories
mkdir -p downloads/configurator-9.0.0-RC3/{linux,macos,windows}

# Download all artifacts from the CI run
gh run download <run-id> --repo iNavFlight/inav-configurator

# The download creates subdirectories, one per artifact:
# - INAV-Configurator_linux_x64/
# - INAV-Configurator_macOS/
# - INAV-Configurator_win_x64/
```

### Step 4: Organize by Platform

Move files to platform-specific directories:

```bash
# Move Linux builds
mv INAV-Configurator_linux_x64/* downloads/configurator-9.0.0-RC3/linux/

# Move macOS builds
mv INAV-Configurator_macOS/* downloads/configurator-9.0.0-RC3/macos/

# Move Windows builds
mv INAV-Configurator_win_x64/* downloads/configurator-9.0.0-RC3/windows/

# Remove empty artifact directories
rmdir INAV-Configurator_*
```

**NEVER** use commands like `find . -mindepth 2 -type f -exec mv -t . {} +` that flatten all files into one directory - this can mix Windows .exe files into macOS DMGs.

### Step 5: Verify Directory Structure

Your downloads should look like:

```
downloads/
├── firmware-9.0.0-RC3/
│   ├── inav_9.0.0_RC3_MATEKF405.hex
│   ├── inav_9.0.0_RC3_MATEKF411.hex
│   └── ... (all renamed hex files)
├── sitl-9.0.0-RC3/
│   └── resources/sitl/
│       ├── linux/
│       ├── macos/
│       └── windows/
└── configurator-9.0.0-RC3/
    ├── linux/
    │   ├── INAV-Configurator_linux_x64_9.0.0.AppImage
    │   ├── INAV-Configurator_linux_x64_9.0.0.deb
    │   └── INAV-Configurator_linux_x64_9.0.0.rpm
    ├── macos/
    │   ├── INAV-Configurator_macOS_arm64_9.0.0.dmg
    │   └── INAV-Configurator_macOS_x64_9.0.0.dmg
    └── windows/
        ├── INAV-Configurator_win_x64_9.0.0.exe
        ├── INAV-Configurator_win_x64_9.0.0.msi
        └── INAV-Configurator_win_x64_9.0.0.zip
```

---

## Next Steps

Once artifacts are downloaded and organized:

**→ Proceed to [Phase 3: Verifying Artifacts](3-verifying-artifacts.md)**
