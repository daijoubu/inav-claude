# Todo List: Investigate H7 FLASH_LATENCY_2 Hardcoded

## Phase 1: Confirm the Datasheet Requirement

- [ ] Pull RM0433 (Rev.5) Table 12 (FLASH recommended wait states/programming
      delay) and confirm required wait states for HCLK=200MHz @ VOS1
- [ ] Pull AN5312 (Rev.1) Section 1.2.1 Table 1 and confirm required wait
      states for HCLK=240MHz @ VOS0 (RevV)
- [ ] Enumerate every VOS/HCLK combination INAV's `pll1ConfigRevY` /
      `pll1ConfigRevV` paths can actually produce, not just the two called
      out in the existing comment
- [ ] Write up findings: does 2WS/4WS as currently commented hold, or does a
      more granular table apply?

## Phase 2: Implement the Fix

- [ ] Make the flash latency argument to `HAL_RCC_ClockConfig()` conditional
      on which `pll1Config` (RevY vs RevV) was selected in
      `SystemClockHSE_Config()` (`system_stm32h7xx.c`)
- [ ] Check for other call sites in the file (or elsewhere) that assume
      `FLASH_LATENCY_2` unconditionally
- [ ] Build full H7 target matrix (at minimum one RevY-era and one
      RevV-capable target)

## Phase 3: Verification

- [ ] Hardware-verify on a RevV board running at 240MHz/VOS0 — confirm no
      regression, ideally confirm the fix is actually reachable/exercised
- [ ] Check whether any existing bug reports (crash logs, hard fault
      reports) plausibly match this failure mode

## Completion

- [ ] PR opened against correct base branch (check
      `.claude/skills/git-workflow/SKILL.md` for current table)
- [ ] All tests passing
- [ ] Send completion report to manager
