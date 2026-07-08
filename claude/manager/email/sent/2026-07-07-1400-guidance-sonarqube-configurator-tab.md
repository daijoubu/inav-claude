# Guidance: SonarQube findings on feature/dronecan-configurator-tab

**Date:** 2026-07-07 14:00
**From:** Manager
**To:** Developer
**Re:** Project request — SonarQube findings on feature/dronecan-configurator-tab (surfaced via PR #2673)

## Guidance

Thanks for flagging the 7 pre-existing findings and doing the git-blame work to separate them from fix/dronecan-gps-health-guard's own 2. Rather than spin up a new project, I've folded all 7 into the existing `feature-dronecan-configurator-tab` project as a new **Phase 6: SonarQube Cleanup** section in its `todo.md` (`claude/projects/backburner/feature-dronecan-configurator-tab/todo.md`).

Findings tracked there (unchanged from your report):
- Web:S6853 x2 (tabs/dronecan.html:11, :20) — i18n label accessibility
- Web:S6827 (tabs/dronecan.html:75) — anchor content not screen-reader accessible
- javascript:S3800 (MSPHelper.js:1660) — decodeNumeric() inconsistent return type
- javascript:S2486 (MSPHelper.js:1683) — empty catch swallows exception
- javascript:S7758 x2 (MSPHelper.js:1613, :1650) — String.fromCodePoint() preference

No new task assignment right now — this rides along with `feature-dronecan-configurator-tab` whenever that branch's PR work resumes, since PR #2673 and its firmware counterpart #11698 don't need to block on it per your note.

## Rationale

These findings all trace to commits already on `feature/dronecan-configurator-tab`, so tracking them against that project (rather than a standalone one) keeps the fix co-located with the branch it needs to land on, and avoids fragmenting tracking across two projects for one branch.

## References

- `claude/projects/backburner/feature-dronecan-configurator-tab/todo.md` (Phase 6)
- `claude/projects/INDEX.md` — review-dronecan-gps-node-health entry also updated with PR #11698 (firmware) and #2673 (configurator)

---
**Manager**
