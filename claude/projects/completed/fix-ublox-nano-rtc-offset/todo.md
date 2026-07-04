# Todo: Fix uBlox nano Field RTC Offset

## Phase 1: Reproduce & Confirm

- [ ] Locate both affected lines in `src/main/io/gps_ublox.c` (~673 and ~712)
- [ ] Confirm the `nano` field type is `int32_t` and that both usages assign to `uint16_t`
- [ ] Write a unit test (or desk-check) confirming -50,000,000 nano → 65,486 ms without fix, → 0 ms with fix

## Phase 2: Fix — release/9.1

- [ ] Apply clamp to both nano usages: `(uint16_t)(MAX(0, _buffer.pvt.nano) / (1000 * 1000))`
- [ ] Confirm `MAX` macro is available in scope (or use conditional)
- [ ] Build full matrix on `release/9.1`: F4, F7, H7, AT32, SITL — all clean
- [ ] Open PR against `release/9.1`

## Phase 3: Fix — maintenance-10.x

- [ ] Cherry-pick or re-apply the same change to `maintenance-10.x`
- [ ] Build full matrix on `maintenance-10.x`: F4, F7, H7, AT32, SITL — all clean
- [ ] Open PR against `maintenance-10.x`

## Completion

- [ ] Two PRs open (one per branch)
- [ ] Both build matrices clean
- [ ] Completion report sent to manager with both PR numbers
