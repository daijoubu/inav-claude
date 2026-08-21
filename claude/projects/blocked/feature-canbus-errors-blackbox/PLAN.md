# feature-canbus-errors-blackbox — Implementation Plan

**Branch:** `feature/canbus-errors-blackbox` (based on `fix/h7-dronecan-driver`, i.e. PR #11607)
**Target:** `maintenance-10.x`
**PR dependency:** #11607 is still open/unmerged. Branching directly off it, same pattern
already used by `feature/dronecan-getnodeinfo`, `feature/dronecan-param-getset`,
`fix/dronecan-gps-health-guard`, and `feature/dronecan-dna-server`. Rebase onto
`maintenance-10.x` once #11607 merges.

**Plan revised 2026-07-14** — scope cut from 6 fields down to 1 after a design review
walked through each field's actual diagnostic value and sampling characteristics
(see "Fields Considered And Dropped" below). The 2026-07-07 revision (which fixed
factual errors in the original Feb 2026 plan) is superseded by this one for scope;
its corrections about what exists in the driver are still accurate and summarized
below.

---

## What We're Building

Log DroneCAN bus-off events to the INAV blackbox slow frame so intermittent CAN bus
problems are diagnosable from flight logs rather than requiring live debugging.

---

## Final Field Set: One Field

| Blackbox field | Source | Type | Encoding |
|---|---|---|---|
| `droneCANBusOffCount` | `dronecanGetBusOffCount()` | uint32_t | `PREDICT(PREVIOUS)`, `ENCODING(UNSIGNED_VB)` |

`dronecanGetBusOffCount()` (`dronecan.c`/`.h`, already exists) returns a monotonic,
non-destructive, lifetime-since-boot count of bus-off events — incremented once each
time the driver's state machine observes `protocolStatus.BusOff != 0` and transitions
into `STATE_DRONECAN_BUS_OFF` (`dronecan.c:185`). Never reset except on reboot. No
firmware changes needed outside `blackbox.c`.

Use `uint32_t` in the struct, matching the getter's return type exactly — narrowing it
(e.g. to `uint16_t`) would add a truncation/wraparound bug that doesn't exist in the
source counter, for zero benefit: `UNSIGNED_VB` encoding costs bytes proportional to
the *actual value*, not the declared width, so a narrower type saves nothing on disk
and only costs 2 bytes of RAM to avoid.

---

## Fields Considered And Dropped

Walked through all 6 fields from the original scope; only `BusOffCount` survived.

- **`droneCANRxDropCount`** (`canardSTM32GetAndClearRxDropCount()`) — deferred, not
  ruled out permanently. Two problems: (1) it's a **destructive read** (clears on
  read), and `dronecan.c:170` already calls it once a second in the driver's own 1Hz
  service task, discarding the value after a `LOG_DEBUG`. A second caller in
  `loadSlowState()` would race with that existing call for the same counts — whichever
  fires first in a given window gets the drops, the other gets 0. Confirmed conflict,
  not hypothetical. (2) F7-only; always 0 on H7. Revisit later if wanted — would need
  either removing the existing `dronecan.c:170` caller or making the counter
  non-destructive (accumulate + peek/clear).

- **`droneCANTec` / `droneCANRec`** (TEC/REC, `canStat.tec`/`.rec`) — dropped.
  These are read live out of the CAN peripheral's ESR hardware register
  (`canard_stm32f7xx_driver.c:224-225`), incremented/decremented by hardware *per
  frame* per the CAN fault-confinement spec — not cumulative, not latched-peak, purely
  instantaneous. `loadSlowState()` only runs once per *logged* main frame (rate
  capped by the configured blackbox rate, often throttled for SD bandwidth), and an
  S-frame is only actually **written** if the sampled value differs from the last
  write or the ~4096-iteration periodic keepalive fires. A brief TEC/REC spike between
  samples can be entirely missed — aliasing risk on exactly the transient you'd most
  want to catch. Decided the bus-off event itself is the actionable signal for "why did
  sensors fail"; TEC/REC are noisy intermediate readings on the way there, not worth
  the aliasing risk for the value they'd add.

- **`droneCANLec`** (Last Error Code) — dropped for the same live-register/aliasing
  reason as TEC/REC, even though it captures error *type* (stuff/form/ACK/CRC/bit)
  rather than a magnitude, which would still carry some signal even from a stale
  sample. Cut for simplicity alongside TEC/REC.

- **`droneCANState`** (`dronecanGetState()`) — dropped. Bus-off recovery
  (`STATE_DRONECAN_BUS_OFF`) is quick and self-healing, so a point-in-time state read
  doesn't add much beyond what `BusOffCount` already shows. `STATE_DRONECAN_FAILED`
  (peripheral init failure) would already be obvious from a total absence of DroneCAN
  data for the whole flight, so a dedicated field for it wasn't judged worth it.

---

## Foundation Actually In Place (verified against `origin/fix/h7-dronecan-driver`, tip `37ec2baf3`)

Carried over from the 2026-07-07 revision — still accurate, kept for reference even
though most of it is no longer needed for the (now much smaller) scope:

`canardProtocolStatus_t` in `libcanard/canard_stm32_driver.h`:

```c
typedef struct {
    uint32_t BusOff;
    uint32_t ErrorPassive;
    uint8_t  tec;
    uint8_t  rec;
    uint8_t  lec;
} canardProtocolStatus_t;
```

No `tx_dropped`/`tx_queue_hwm`/`rx_buffer_hwm` fields exist (contrary to the original
Feb 2026 plan) — not relevant now since none of those were ever in scope for this
revision anyway.

**Already implemented, no work needed:**
- `uint32_t dronecanGetBusOffCount(void)` (`dronecan.c`/`.h`) — the one getter this
  plan actually uses.

---

## What We Still Need to Add

### Blackbox slow state field — `blackbox.c`

**a) Extend `blackboxSlowState_t` struct** (find the `__packed__` struct, add before
closing brace):

```c
#ifdef USE_DRONECAN
    uint32_t droneCANBusOffCount;    // Cumulative bus-off events
#endif
```

**b) Add field definition** to `blackboxSlowFields[]` array (after the `#ifdef
USE_ESC_SENSOR` block):

```c
#ifdef USE_DRONECAN
    {"droneCANBusOffCount", -1, UNSIGNED, PREDICT(PREVIOUS), ENCODING(UNSIGNED_VB)},
#endif
```

**c) Populate in `loadSlowState()`** (add after the `#ifdef USE_ESC_SENSOR` block):

```c
#ifdef USE_DRONECAN
    slow->droneCANBusOffCount = dronecanGetBusOffCount();
#endif
```

**d) Write in `writeSlowFrame()`** (add after the `#ifdef USE_ESC_SENSOR` block):

```c
#ifdef USE_DRONECAN
    blackboxWriteUnsignedVB(slowHistory.droneCANBusOffCount);
#endif
```

Note: struct member order does **not** need to match the field-defs/write-call order —
confirmed by inspecting the existing code (`activeWpNumber` and `rxUpdateRate` are
positioned differently in `blackboxSlowState_t` vs. `blackboxSlowFields[]`/
`writeSlowFrame()` already, and it works fine). The struct is only ever accessed by
field name (`loadSlowState()` writes members individually, `writeSlowFrame()` reads
them individually); the two full-struct `memcmp`/`memcpy` calls in
`writeSlowFrameIfNeeded()` are order-agnostic since they compare two instances of the
same type. **The constraint that actually matters is `blackboxSlowFields[]` order
must match `writeSlowFrame()`'s call order exactly** — that's what produces the wire
bytes and what the H-frame header (built from `blackboxSlowFields[]`) tells decoders
to expect.

No changes needed to `dronecan.c`/`dronecan.h`.

---

## Files to Edit

| File | Change |
|------|--------|
| `src/main/blackbox/blackbox.c` | Extend struct, add field def, loadSlowState, writeSlowFrame — one field |

---

## Build Matrix

Build before opening PR:
- F7 (e.g. MATEKF765SE) — primary target
- H7 (e.g. MATEKH743 / KAKUTEH7WING) — bus-off counting works the same as F7
- AT32 (e.g. IFLIGHT_BLITZ_ATF435)
- F4 (e.g. SPEEDYBEEF405WING)
- SITL — value will be 0, must compile clean with -Werror

---

## Testing

1. Flash F7 board, connect DroneCAN node
2. Arm and fly (or bench-arm) with blackbox logging enabled
3. After landing, pull log and verify:
   - Blackbox header (`H` frame) lists the `droneCANBusOffCount` field name
   - S frames appear with the field present (0 if no bus-off occurred)
4. Briefly disconnect/short the CAN bus mid-session to trigger a bus-off event;
   verify `droneCANBusOffCount` increments in the log
5. Cross-check against live `dronecan` CLI output for the same count

---

## PR Notes (for when #11607 merges)

1. `git rebase upstream/maintenance-10.x` — diff will narrow to only `blackbox.c`
2. Open PR to `maintenance-10.x`
3. PR description should mention:
   - Consumes the bus-off counter already exposed by PR #11607's driver rework
   - Scope was deliberately cut to just the one cumulative counter after review —
     TEC/REC/LEC/state were considered and dropped as low-value/alias-prone for a
     slow-frame sampling model; RX-drop-count deferred due to a destructive-read
     conflict with the driver's existing 1Hz consumer
   - References the `dronecan` CLI command as companion live view
