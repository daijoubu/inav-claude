# Phase 6: Creating and Uploading Releases

**Read this guide when:** Artifacts are verified and release notes are ready

**Prerequisites:**
- Artifacts downloaded and verified (Phases 2-3)
- Release notes written (Phase 5)

**Related guides:**
- [Phase 1: Workflow and Preparation](1-workflow-and-preparation.md)
- [Phase 3: Verifying Artifacts](3-verifying-artifacts.md)
- [Phase 5: Changelog and Notes](5-changelog-and-notes.md)
- [Phase 7: Publishing Releases](7-publishing-releases.md)

---

## Overview

This guide covers creating tags, draft releases, and uploading assets on GitHub. Once assets are uploaded and verified, proceed to [Phase 7](7-publishing-releases.md) to publish and announce.

---

⚠️ **If `gh release create`/`upload`/`edit` returns 403 "Resource not accessible by personal access token":** same restricted-`GITHUB_TOKEN` issue as guide 2's branch-push section. The restriction is intentional. **Ask the human user before dropping it, every time** — see guide 2's warning; it applies here too, and a prior authorization elsewhere in the session doesn't carry over to release creation.

## Check Latest Tags

Before creating new tags, check what tags already exist:

```bash
# Firmware
cd inav
git fetch --tags
git tag --sort=-v:refname | head -10

# Configurator
cd inav-configurator
git fetch --tags
git tag --sort=-v:refname | head -10
```

---

## Creating Releases and Tags Using gh

**TIP:** You can create both the tag and release in one step using `gh release create`, bypassing the need to work in locked local repositories.

### Benefits

- Creates tag and release atomically
- No need for local repository access
- Works even when repository directory is locked
- Can specify exact commit by SHA
- Creates draft releases for review before publishing

⚠️ **"Atomically" only applies once published.** For a `--draft` release, GitHub does **not** push an actual Git tag ref into the repository yet — the draft just stores the target commitish and the intended tag name internally. `git ls-remote --tags` (or any clone) won't see the tag until the release is published. Don't be surprised that the tag "doesn't exist" while a draft is pending review — that's expected, not a bug.

### Choosing the Target Commit When the Branch Has Advanced

If new commits landed on the release branch after the CI artifacts were built, check whether those commits affect compiled firmware:

```bash
git log --oneline <ci-commit>..upstream/<release-branch>
git show --stat <each-new-commit>
```

- If every new commit only touches **non-compiled files** (docs, reference databases, CI scripts) → tag the current branch HEAD. Rebuilding from HEAD produces identical binaries, and tagging HEAD is conventional.
- If any new commit changes **firmware source code** (`.c`, `.h`, `CMakeLists.txt`, `settings.yaml`) → re-run CI on the new HEAD and download fresh artifacts before tagging.

### For Firmware

```bash
# Create release + tag at specific commit on GitHub (no local repo access needed)
gh release create 9.1.1-rc1 \
  --repo iNavFlight/inav \
  --target 34e3e4b3d8525931f825e766c28749a4c6342963 \
  --title "INAV 9.1.1-rc1 release candidate for testing" \
  --notes-file claude/release-manager/releases/9.1.1-rc1/9.1.1-rc1-firmware-release-notes.md \
  --prerelease \
  --draft
```

**Parameters explained:**
- `9.1.1-rc1` - The tag name
- `--target` - Specific commit SHA to tag
- `--title` - Release title shown on GitHub
- `--notes-file` - Path to release notes markdown file
- `--prerelease` - Mark as pre-release (for RC releases)
- `--draft` - Create as draft for review before publishing

### For Configurator

```bash
# Create release + tag at specific commit
gh release create 9.1.1-rc1 \
  --repo iNavFlight/inav-configurator \
  --target 9dbd346dcf941b31f97ccb8418ede367044eb93c \
  --title "INAV Configurator 9.1.1-rc1 release candidate for testing" \
  --notes-file claude/release-manager/releases/9.1.1-rc1/9.1.1-rc1-configurator-release-notes.md \
  --prerelease \
  --draft
```

### For Final Releases (Non-RC)

For final releases, omit the `--prerelease` flag:

```bash
gh release create 9.1.1 \
  --repo iNavFlight/inav \
  --target <commit-sha> \
  --title "INAV 9.1.1" \
  --notes-file claude/release-manager/releases/9.1.1/9.1.1-firmware-release-notes.md \
  --draft
```

---

## Uploading Assets to Draft Releases

After creating the draft release, upload artifacts using `gh release upload`:

### Upload Configurator Builds

Upload by platform to maintain organization:

```bash
# Upload configurator builds by platform
cd claude/release-manager/downloads/configurator-9.1.1-rc1

gh release upload 9.1.1-rc1 linux/* --repo iNavFlight/inav-configurator
gh release upload 9.1.1-rc1 macos/* --repo iNavFlight/inav-configurator
gh release upload 9.1.1-rc1 windows/* --repo iNavFlight/inav-configurator
```

### Upload Firmware Hex Files

```bash
# Upload firmware hex files
cd ../firmware-9.1.1-rc1
gh release upload 9.1.1-rc1 *.hex --repo iNavFlight/inav
```

**Note:** Files should already be renamed (CI suffix removed, RC number added) as per Phase 2.

---

## Asset Naming Conventions

Ensure assets follow these naming patterns:

### Firmware (RC releases)
- Pattern: `inav_<version>_RC<n>_<TARGET>.hex`
- Example: `inav_9.1.1_RC2_MATEKF405.hex`

### Firmware (final releases)
- Pattern: `inav_<version>_<TARGET>.hex`
- Example: `inav_9.1.1_MATEKF405.hex`

### Configurator (RC releases)
- Pattern: `INAV-Configurator_<platform>_<version>_RC<n>.<ext>`
- Example: `INAV-Configurator_linux_x64_9.1.1_RC2.deb`

### Configurator (final releases)
- Pattern: `INAV-Configurator_<platform>_<version>.<ext>`
- Example: `INAV-Configurator_linux_x64_9.1.1.deb`

---

## Managing Release Assets

### Renaming Assets Without Re-uploading

You can rename release assets directly via the GitHub API without re-uploading:

```bash
# Get release ID and asset IDs
gh api repos/iNavFlight/inav/releases --jq '.[] | select(.draft == true) | {id: .id, name: .name}'
gh api repos/iNavFlight/inav/releases/RELEASE_ID/assets --paginate --jq '.[] | "\(.id) \(.name)"'

# Rename a single asset
gh api -X PATCH "repos/iNavFlight/inav/releases/assets/ASSET_ID" -f name="new-filename.hex"
```

**Important:** The GitHub API paginates results (30 per page by default). Always use `--paginate` when listing assets to get all of them.

### Bulk Renaming Firmware Assets

If you uploaded files with the wrong naming pattern:

```bash
# Bulk rename firmware assets (add RC number, remove ci- suffix)
gh api repos/iNavFlight/inav/releases/RELEASE_ID/assets --paginate --jq '.[] | "\(.id) \(.name)"' > /tmp/assets.txt

cat /tmp/assets.txt | while read -r id name; do
  target=$(echo "$name" | sed -E 's/inav_[0-9]+\.[0-9]+\.[0-9]+_(.*)_ci-.*/\1/')
  newname="inav_9.1.1_RC2_${target}.hex"
  gh api -X PATCH "repos/iNavFlight/inav/releases/assets/$id" -f name="$newname" --silent
done
```

### Deleting Release Assets

If a draft release has outdated assets that need to be replaced (e.g., from a previous upload attempt), delete them before uploading new ones:

```bash
# Delete an asset by ID
gh api -X DELETE "repos/iNavFlight/inav/releases/assets/ASSET_ID"
```

---

## Managing Draft Releases

### List All Releases

```bash
# List releases (shows both draft and published)
gh release list --repo iNavFlight/inav --limit 10
gh release list --repo iNavFlight/inav-configurator --limit 10
```

### View Draft Release

```bash
# View release details
gh release view 9.1.1-rc1 --repo iNavFlight/inav
gh release view 9.1.1-rc1 --repo iNavFlight/inav-configurator
```

### Edit Release Notes

```bash
# Edit release notes after creating draft
gh release edit 9.1.1-rc1 --repo iNavFlight/inav \
  --notes-file claude/release-manager/releases/9.1.1-rc1/9.1.1-rc1-firmware-release-notes.md
```

---

## Alternative: Traditional Git Tagging (Less Common)

If you can't use `gh release create` for some reason, you can create tags locally:

```bash
# Create tag locally
cd inav
git tag -a 9.1.1-rc1 -m "INAV 9.1.1-rc1"

# Push tag to GitHub
git push origin 9.1.1-rc1

# Then create release
gh release create 9.1.1-rc1 --draft --title "INAV 9.1.1-rc1" --notes-file release-notes.md
```

However, using `gh release create` with `--target` is preferred as it works even when repos are locked.

---

## Troubleshooting

### Release Creation Fails

**Error: "Reference already exists"**
- Tag already exists on GitHub
- Check: `git ls-remote --tags origin | grep 9.1.1-rc1`
- Solution: Delete tag if incorrect, or use existing tag

**Error: "Not found"**
- Commit SHA doesn't exist
- Check: `gh api repos/iNavFlight/inav/commits/<sha>`
- Solution: Verify commit SHA is correct and pushed

### Upload Fails

**Error: "release not found"**
- Release doesn't exist yet
- Solution: Create draft release first

**Error: "asset already exists"**
- File with same name already uploaded
- Solution: Delete old asset or rename new one

---

## Quick Reference Commands

```bash
# Create draft release with tag
gh release create <version> --repo <owner/repo> --target <commit> --draft --prerelease --notes-file <file>

# Upload assets
gh release upload <version> <files> --repo <owner/repo>

# View release
gh release view <version> --repo <owner/repo>

# List assets
gh api repos/<owner/repo>/releases/<id>/assets --paginate
```

---

## Checklist

- [ ] Latest tags checked
- [ ] Target commit SHA identified for firmware
- [ ] Target commit SHA identified for configurator
- [ ] Draft release created for firmware (with tag)
- [ ] Draft release created for configurator (with tag)
- [ ] Firmware hex files uploaded
- [ ] Configurator Linux builds uploaded
- [ ] Configurator macOS builds uploaded
- [ ] Configurator Windows builds uploaded
- [ ] Asset naming verified
- [ ] Release notes reviewed

---

⚠️ **Reminder for the human user before Phase 7:** Publish firmware first, then verify the release loads correctly in the Configurator's Firmware Flasher tab, **before** publishing the Configurator release itself. Do not manually publish Configurator ahead of that check — see [Phase 7](7-publishing-releases.md) for the full sequence.

---

## Next Steps

Once drafts are created and assets are uploaded:

**→ Proceed to [Phase 7: Publishing Releases](7-publishing-releases.md)**
