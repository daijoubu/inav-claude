# feature-canbus-errors-blackbox — Implementation Plan

**Branch:** `feature/canbus-errors-blackbox` (based on `fix/h7-dronecan-driver`, i.e. PR #11607)
**Target:** `maintenance-10.x`
**PR dependency:** #11607 is still open/unmerged. Branching directly off it now, same pattern
already used by `feature/dronecan-getnodeinfo`, `feature/dronecan-param-getset`,
`fix/dronecan-gps-health-guard`, and `feature/dronecan-dna-server`. Rebase onto
`maintenance-10.x` once #11607 merges.

**Plan revised 2026-07-07** — the previous version of this plan (written Feb 2026,
before the driver rework) was checked against the actual `fix/h7-dronecan-driver`
branch and found stale in three ways: it claimed a field-set that doesn't exist, it
was unaware that a counter had already been added, and it didn't know about two
newer getters. Corrected below.

---

## What We're Building

Log CAN bus error statistics to the INAV blackbox slow frame so intermittent CAN
bus problems are diagnosable from flight logs rather than requiring live debugging.

---

## Foundation Actually In Place (verified against `origin/fix/h7-dronecan-driver`)

`canardProtocolStatus_t` in `libcanard/canard_stm32_driver.h` — **note: smaller than
previously documented, no `tx_dropped`/`tx_queue_hwm`/`rx_buffer_hwm` fields exist**:

```c
typedef struct {
    uint32_t BusOff;
    uint32_t ErrorPassive;
    uint8_t  tec;
    uint8_t  rec;
    uint8_t  lec;
} canardProtocolStatus_t;
```

Populated via `canardSTM32GetProtocolStatus(&stat)`. Both F7 (`canard_stm32f7xx_driver.c`)
and H7 (`canard_stm32h7xx_driver.c`) now populate tec/rec/lec fully — **the "H7
tec/rec/lec deferred" TODO from the original PR #11560 is resolved in #11607.** SITL
still returns zeros for all fields (acceptable — must still compile clean).

**Already implemented, no work needed:**
- `uint32_t dronecanGetBusOffCount(void)` (`dronecan.c`/`.h`) — cumulative bus-off
  event counter already exists and increments in the state machine. The counter is
  `uint32_t`, not `uint16_t` as the old plan assumed.
- `dronecanState_e dronecanGetState(void)` — current state (INIT/NORMAL/BUS_OFF/FAILED).

**Available but not in the old plan at all:**
- `uint32_t canardSTM32GetAndClearRxDropCount(void)` — real cumulative RX-drop
  counter on F7 (incremented in the RX ISR, cleared on read). **Stubbed to always
  return 0 on H7** ("H7 FIFO0 has no software ring buffer; FIFO overflow drops are
  not currently counted" — comment in `canard_stm32h7xx_driver.c`).
- `int32_t canardSTM32GetTxQueueFillLevel(void)` / `GetRxFifoFillLevel(void)` —
  instantaneous fill levels (not cumulative, not high-water-marks).
- `CanardPoolAllocatorStatistics dronecanGetPoolStats(void)` — libcanard memory pool
  stats: `capacity_blocks`, `current_usage_blocks`, `peak_usage_blocks`. Useful for
  diagnosing memory-pressure related node dropouts, not considered in the original
  scope.

**Does NOT exist, contrary to the old plan:**
- No TX-side drop counter anywhere in the driver. The original scope's "TX dropped"
  field has no backing data today — logging it would mean adding new instrumentation
  (out of scope for "just wire up the blackbox fields," a separate decision).
- No high-water-mark tracking (`tx_queue_hwm`/`rx_buffer_hwm`) — only instantaneous
  fill levels exist.

The `dronecan` CLI command (`cliDronecan()` in `fc/cli.c`) already displays TEC/REC/LEC,
BusOff/ErrorPassive, TX/RX fill level, and bus-off count live — useful as a reference
implementation and for cross-checking blackbox values during testing.

---

## Recommended Field Set (revised)

Given what's actually available, the straightforward field set — all backed by
existing getters, no new instrumentation required:

| Blackbox field | Source | Type |
|---|---|---|
| `droneCANState` | `dronecanGetState()` | uint8_t |
| `droneCANTec` | `canStat.tec` | uint8_t |
| `droneCANRec` | `canStat.rec` | uint8_t |
| `droneCANLec` | `canStat.lec` | uint8_t |
| `droneCANBusOffCount` | `dronecanGetBusOffCount()` | uint32_t |
| `droneCANRxDropCount` | `canardSTM32GetAndClearRxDropCount()` | uint32_t (real on F7, always 0 on H7) |

Optional, discuss before including (changes scope slightly beyond the original ask):
- `droneCANPoolPeakUsage` from `dronecanGetPoolStats().peak_usage_blocks` — cheap to
  add, diagnostically useful for memory-pressure issues.
- TX queue / RX fifo instantaneous fill level — less useful in a slow frame than a
  cumulative/peak stat, since a snapshot between logging intervals can miss transients.

Note `canardSTM32GetAndClearRxDropCount()` clears on read — if the CLI command and
the blackbox logger both call it, one will steal the other's counts. Blackbox's
`loadSlowState()` should be the sole caller, or the counter needs to become
non-destructive (accumulate internally, expose a peek + separate clear).

---

## What We Still Need to Add

### 1. Blackbox slow state fields — `blackbox.c`

**a) Extend `blackboxSlowState_t` struct** (find the `__packed__` struct, add before closing brace):

```c
#ifdef USE_DRONECAN
    uint8_t  droneCANState;          // dronecanState_e value
    uint8_t  droneCANTec;            // Transmit Error Counter
    uint8_t  droneCANRec;            // Receive Error Counter
    uint8_t  droneCANLec;            // Last Error Code
    uint32_t droneCANBusOffCount;    // Cumulative bus-off events
    uint32_t droneCANRxDropCount;    // Cumulative RX drops (F7 real, H7 always 0 today)
#endif
```

**b) Add field definitions** to `blackboxSlowFields[]` array (after the `#ifdef USE_ESC_SENSOR` block):

```c
#ifdef USE_DRONECAN
    {"droneCANState",       -1, UNSIGNED, PREDICT(PREVIOUS), ENCODING(UNSIGNED_VB)},
    {"droneCANTec",         -1, UNSIGNED, PREDICT(PREVIOUS), ENCODING(UNSIGNED_VB)},
    {"droneCANRec",         -1, UNSIGNED, PREDICT(PREVIOUS), ENCODING(UNSIGNED_VB)},
    {"droneCANLec",         -1, UNSIGNED, PREDICT(PREVIOUS), ENCODING(UNSIGNED_VB)},
    {"droneCANBusOffCount", -1, UNSIGNED, PREDICT(PREVIOUS), ENCODING(UNSIGNED_VB)},
    {"droneCANRxDropCount", -1, UNSIGNED, PREDICT(PREVIOUS), ENCODING(UNSIGNED_VB)},
#endif
```

Note: `PREDICT(PREVIOUS)` is better than `PREDICT(0)` for counters — P-frames store
the delta (usually 0), so they compress to a single byte when nothing changes.

**c) Populate in `loadSlowState()`** (add after the `#ifdef USE_ESC_SENSOR` block):

```c
#ifdef USE_DRONECAN
    {
        canardProtocolStatus_t canStat;
        canardSTM32GetProtocolStatus(&canStat);
        slow->droneCANState       = (uint8_t)dronecanGetState();
        slow->droneCANTec         = canStat.tec;
        slow->droneCANRec         = canStat.rec;
        slow->droneCANLec         = canStat.lec;
        slow->droneCANBusOffCount = dronecanGetBusOffCount();
        slow->droneCANRxDropCount = canardSTM32GetAndClearRxDropCount();
    }
#endif
```

**d) Write in `writeSlowFrame()`** (add after the `#ifdef USE_ESC_SENSOR` block, in the
same order as the struct fields — order MUST match `blackboxSlowFields[]`):

```c
#ifdef USE_DRONECAN
    blackboxWriteUnsignedVB(slowHistory.droneCANState);
    blackboxWriteUnsignedVB(slowHistory.droneCANTec);
    blackboxWriteUnsignedVB(slowHistory.droneCANRec);
    blackboxWriteUnsignedVB(slowHistory.droneCANLec);
    blackboxWriteUnsignedVB(slowHistory.droneCANBusOffCount);
    blackboxWriteUnsignedVB(slowHistory.droneCANRxDropCount);
#endif
```

No changes needed to `dronecan.c`/`dronecan.h` — everything this plan uses already
exists there.

---

## Key Constraint: Field Order Must Be Consistent

The order in `blackboxSlowFields[]`, in `blackboxSlowState_t`, and in `writeSlowFrame()`
must all match exactly. Mismatch = log corruption. When adding, keep the same block
position in all three places.

---

## Files to Edit

| File | Change |
|------|--------|
| `src/main/blackbox/blackbox.c` | Extend struct, add field defs, loadSlowState, writeSlowFrame |

No other files need changing — unlike the original plan, no `dronecan.c`/`.h` changes
are required since the bus-off counter already exists.

---

## Build Matrix

Build before opening PR:
- F7 (e.g. MATEKF765SE) — primary target, full driver support including real RX drop count
- H7 (e.g. MATEKH743) — tec/rec/lec now populated (fixed in #11607); RX drop count always 0
- SITL — all fields will be 0, but must compile clean with -Werror

---

## Testing

1. Flash F7 board, connect DroneCAN node
2. Arm and fly (or bench-arm) with blackbox logging enabled
3. After landing, pull log and verify:
   - Blackbox header (`H` frame) lists the 6 new `droneCAN*` field names
   - S frames appear with non-zero values when a node is active
   - TEC/REC values match what `dronecan` CLI command shows live
4. Optionally: briefly disconnect CAN bus mid-flight to trigger a bus-off event;
   verify `droneCANBusOffCount` increments in the log
5. Verify the CLI command and blackbox logger don't both call
   `canardSTM32GetAndClearRxDropCount()` in a way that steals each other's counts
   (see note above) — confirm which one is the sole/intended caller

---

## PR Notes (for when #11607 merges)

1. `git rebase upstream/maintenance-10.x` — diff will narrow to only `blackbox.c`
2. Open PR to `maintenance-10.x`
3. PR description should mention:
   - Consumes CAN error/status data already exposed by PR #11607
   - References the `dronecan` CLI command as companion live view
   - Notes TX-side drop counting doesn't exist yet — out of scope, could be a
     follow-up if wanted (would need new instrumentation, not just wiring)
