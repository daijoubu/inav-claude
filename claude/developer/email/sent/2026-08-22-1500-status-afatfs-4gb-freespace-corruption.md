# Status Update: AFATFS SD Card Free-Space Corruption at 4GB Boundary

**Date:** 2026-08-22 15:00
**From:** Developer
**To:** Manager
**Re:** New bug finding during NEMESIS blackbox investigation

## Finding

While investigating the DroneCAN cell-voltage task and attempting to recover blackbox data from the NEMESIS crash flight, Developer discovered a significant SD card filesystem corruption issue in INAV's AFATFS implementation.

The card recovered from NEMESIS (14.8GB, MATEKF765SE craft) was forensically examined using:
- `dd` to create a full raw image (read-only, original untouched)
- `fsck.vfat -n -v` dry-run validation against the extracted FAT32 partition

## Technical Details

**Corruption Evidence:**

1. **Free-cluster count mismatch:** FSInfo sector reported free clusters was wrong by 128,913 clusters (32768 bytes/cluster) = ~4.22GB — almost exactly 4GiB. This matches developer's observation that INAV can only reliably use approximately the first 4GB of this card.

2. **Cluster chain truncation failure:** 1023 of 1024 log files had cluster chains longer than their actual file size. `fsck` had to truncate every one. This pattern is consistent with INAV's AFATFS pre-allocating cluster chains per log file for fast async writes, but failing to truncate them back down to actual written size before finalizing.

3. **Filesystem dirty state:** The dirty bit was set, indicating the filesystem was not cleanly unmounted at some point.

4. **No orphaned data:** Raw-disk string search for the blackbox header signature ("Product:Blackbox flight data recorder") across the entire partition image returned exactly 1023 hits — matching the known real files. Zero orphaned or hidden sessions found anywhere.

5. **Confirmed timeline:** All 1023 real logs dated 2026-05-07 (bench endurance-test session, ~5 months old). Last file is 0-byte stub marking session end.

## Practical Impact

**For NEMESIS investigation:**
- The 2026-08-16 crash blackbox data is not recoverable from this card
- Recording likely never started on crash day because free-space corruption from May 7 had already put the filesystem in a state where INAV couldn't or wouldn't open a new log file
- Investigation must proceed using video-derived data + live bench reproduction

**For INAV codebase:**
- This is a genuine bug in AFATFS's free-cluster/FSInfo tracking or per-file cluster-chain truncation-on-close
- Likely surfaces once total allocated space approaches the 4GiB boundary
- Affects any user with SD cards >4GB, particularly those doing extended logging sessions

## Recommendation

Track this as a separate investigation rather than folding into the cell-voltage task. Suggest opening a new project (candidate name: `fix-afatfs-4gb-freespace-corruption` or similar) to:

1. Reproduce the issue on a test board with a large SD card
2. Identify the exact code path in AFATFS responsible for cluster truncation
3. Fix the FSInfo/free-cluster tracking
4. Validate the fix with extended logging sessions

## Working Files

Developer's forensic analysis files are currently saved in `claude/developer/workspace/fix-dronecan-cell-voltage-calculation/` (large binary files: raw disk image, extracted partition image, fsck output). These can be moved to a dedicated project workspace once the manager opens a new project for this investigation.

---
**Developer**
