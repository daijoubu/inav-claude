# Todo List: Fix PLL2 VCO Frequency

## Phase 1: Audit

- [ ] Read `src/main/startup/system_stm32h7xx.c` PLL2 block — record original M, N, P, Q, R values
- [ ] Diff against the pre-`fix/h7-dronecan-driver` state to find every PLL2 parameter changed
- [ ] Calculate actual VCO, PLL2Q (FDCAN), and PLL2R (SDMMC) frequencies before and after
- [ ] Identify what specifically changed and on which targets

## Phase 2: Fix

- [ ] Determine correct M and N values that preserve original VCO for 8 MHz HSE
- [ ] Determine correct M and N values for 16 MHz HSE (KAKUTEH7WING) without altering other dividers
- [ ] Update `fix/11594-pll2-dynamic-m-divider` branch with corrected PLL2 config
- [ ] Verify FDCAN = 80 MHz and SDMMC = 200 MHz on all affected targets

## Phase 3: Verify

- [ ] Build KAKUTEH7WING — confirm FDCAN and SDMMC clocks
- [ ] Build a standard 8 MHz HSE H7 target — confirm no clock change
- [ ] Update PR #11596 description with corrected explanation

## Completion

- [ ] PR #11596 updated and ready for review
- [ ] Send completion report to manager
