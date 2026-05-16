# Todo: Fix Cortex-M7 SD Card Write Ordering

## Phase 1: Implement

- [ ] Add `static volatile` to `sdReadParameters` in `sdmmc_sdio_hal.c`
- [ ] Reorder `HAL_SD_RxCpltCallback`: move `RXCplt = 1` after `SCB_InvalidateDCache_by_Addr()` with `__DMB()` barrier
- [ ] Build for affected F7 targets

## Phase 2: PR

- [ ] Create PR on `fix/cortex-m7-sd-write-ordering` → `maintenance-10.x`
- [ ] Reference issue #11562
- [ ] Send completion report
