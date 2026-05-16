# Todo: Cortex-M7 SD Card Write Ordering Investigation

## Phase 1: Audit

- [ ] Locate SD card driver files (STM32F7 HAL-based, DMA/ISR paths)
- [ ] Audit ISR/DMA callback paths for missing `volatile` qualifiers
- [ ] Audit ISR/DMA callback paths for missing DMB/DSB barriers
- [ ] Check DMA descriptor setup for D-cache coherency (invalidate/clean before/after transfers)
- [ ] Identify any SPSC or shared-data structures between SD ISR and main task
- [ ] Compare findings against STM32 AN4748 (cache management on STM32F7/H7)

## Phase 2: Document Findings

- [ ] Write investigation report in `claude/developer/investigations/`
- [ ] List any issues found with severity (correctness bug vs latent hazard)
- [ ] If no issues: document as clean audit

## Phase 3: Fix (if needed)

- [ ] Implement fixes for any identified issues
- [ ] Build and verify affected F7 targets
- [ ] Create PR or append to existing HAL update PR

## Completion

- [ ] Investigation report complete
- [ ] Any fixes implemented and building
- [ ] Send completion report to manager
