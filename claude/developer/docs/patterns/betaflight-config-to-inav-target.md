# Pattern: Porting/Updating an INAV Target from a Betaflight `config.h`

## Wording: Don't Name Betaflight in Code/Commits/PRs

Betaflight is not upstream for INAV — don't call it that, and don't name
Betaflight at all in `target.h`/`target.c`/`config.c` comments, commit
messages, or PR descriptions, even when a target was ported from its
config. Say "the manufacturer's public unified-target config" instead.
Fine to mention Betaflight in internal docs/conversation — just not in
that persistent, user-facing text.

## When This Applies

Recurring task shape: the manager hands you a URL to
`https://github.com/betaflight/config/blob/master/configs/<BOARD>/config.h`
and asks either to (a) create a new INAV target from it, or (b) diff it
against an existing INAV target and bring the target up to date. As of
2026-07-06 there are three tasks in this pattern in flight:
`update-dakefpvf405-target`, `feature-axisflyingh743pro-target`,
`feature-axisflyingecof4-target`.

**Always check `src/main/target/<BOARD>/` exists before treating this as a
new-target project** — `update-dakefpvf405-target` was originally requested
as "new" but the target already existed; it was actually an update. Don't
assume the manager's framing is correct without checking the tree.

---

## There Is Already a Generator: `src/utils/bf2inav.py`

Documented in `inav/docs/development/Converting Betaflight Targets.md`. Usage:

```bash
cd inav/src/utils
python3 ./bf2inav.py -i config.h -o ../main/target/<BOARD>/
```

It generates `target.h`, `target.c`, `config.c`, `CMakeLists.txt` from a
Betaflight `config.h` and a `timer_pins.yaml` lookup table. Good for a
first draft on a genuinely new target. **Known gaps as of 2026-07-06**
(tracked for a fix in a separate PR, see `feature-fix-bf2inav-gaps` /
task history in this repo):

- `buildMap()` rewrites `ICM42688P` → `ICM42605` in `empty_defines`
  (`re.sub('ICM42688P', 'ICM42605', ...)`). **Correction (2026-07-06):**
  this was first logged here as a bug, but it is actually correct —
  see section 3 below. ICM42605/ICM42686P/ICM42688P share one driver
  gated only by `USE_IMU_ICM42605`, so rewriting the Betaflight macro to
  `ICM42605` before generating `target.h` is the right behavior, not a
  gap. Left as-is.
- No handling for `LSM6DSV16X` / `LSM6DSK320X` at all — these silently
  vanish rather than warning that no driver exists.
- No `CAMERA_CONTROL_PIN` generation.
- `writeConfigC()` has the `pinioBoxConfigMutable()->permanentId[n]` lines
  only as **commented-out Python source** (never `file.write()`'d) — the
  generated `config.c` always has an empty `targetConfiguration()` body,
  so PINIO box wiring must be added by hand every time.

For an **existing-target update** (not a fresh port), don't run the
generator — diff by hand and use the `target-developer` agent, as below.

---

## Recurring Translation Rules

### 1. PINIO → `config.c`

Betaflight's `PINIOn_BOX <id>` / `BOX_USERn_NAME "<name>"` map to INAV's
`config.c`:

```c
void targetConfiguration(void)
{
    pinioBoxConfigMutable()->permanentId[0] = BOX_PERMANENT_ID_USER1;
    pinioBoxConfigMutable()->permanentId[1] = BOX_PERMANENT_ID_USER2; // only if PINIO2 exists
}
```

Index `n` in `permanentId[n]` is 0-based; `USERn+1` is 1-based. Only add
the entries for PINIO pins that actually exist on this board — don't add
`permanentId[1]` if there's no `PINIO2_PIN`.

**Config bit → INAV flag:** Betaflight's `PINIOn_CONFIG` value's `0x80` bit
corresponds to INAV's `PINIOx_FLAGS PINIO_FLAGS_INVERTED`. There is no
`PINIOx_CONFIG` macro in INAV at all — `PINIOx_FLAGS` is the real
equivalent. (Confirmed via the AIKONF4V3 fix, commit `e7d8c5701516`.)

### 2. `CAMERA_CONTROL_PIN`

**No driver consumes this prior to INAV 10.0** — as of 2026-07-06 there is
no `camera_control.c` driver and nothing anywhere in `src/main/fc` or
`src/main/drivers` reads `CAMERA_CONTROL_PIN` or tests
`USE_CAMERA_CONTROL`. It's carried over mechanically from Betaflight
conversions with no effect today. **This changes in 10.0** — the planned
flexible PWM-capable PINIO feature will let `CAMERA_CONTROL_PIN` (and
other timer-controlled PINIO pins) actually drive camera control via PWM.
A migration project to convert existing `CAMERA_CONTROL_PIN` targets over
to that feature is expected to be scheduled for October 2026, once 10.0's
PWM-PINIO support lands — see the manager's project tracking for status.
Existing sibling targets (`DAKEFPVH743`, `DAKEFPVH743PRO`,
`DAKEFPVF722X8`) still define it as a bare `#define CAMERA_CONTROL_PIN
<pin>` with **no** `#ifndef USE_CAMERA_CONTROL` guard — match that
convention for consistency today, but leave a comment noting it as a
future PWM-PINIO migration candidate (see `DAKEFPVF405/target.h` for the
wording used there). Do double check the pin isn't claimed by something
else in `target.c`'s timer table first, since Betaflight's
`TIMER_PIN_MAPPING` sometimes assigns it a channel that INAV doesn't
currently use for it.

### 3. New IMU/flash chip IDs on an existing bus

When Betaflight's `config.h` lists a chip your existing target doesn't
have (e.g. `USE_ACC_SPI_ICM42688P` alongside existing
`USE_GYRO_SPI_MPU6000`), first check whether INAV already has a driver
under `src/main/drivers/accgyro/` (or `drivers/flash/`) — grep for the
chip name, don't assume you need a new driver.

**Before adding a `USE_IMU_<CHIP>` block, verify that exact macro name is
tested somewhere real** — `grep -rn "USE_IMU_<CHIP>" src/main/*.c
src/main/target/common_hardware.c` (or the target's own `target.c` if it
registers buses manually). Don't stop at "a driver file with this chip's
name exists" — some chip families share one driver file gated by only
*one* of the macros, with the others only present as harmless-looking
copy-paste in target.h that do nothing at build time.

**Concrete trap, found 2026-07-06 on DAKEFPVF405:** `ICM42605`,
`ICM42686P`, and `ICM42688P` are one driver (`accgyro_icm42605.c`), gated
by `USE_IMU_ICM42605` only — its `WHO_AM_I` switch matches all three chip
IDs. `common_hardware.c` has **no** `#if defined(USE_IMU_ICM42688P)`
registration block, and that macro appears in zero `.c` files anywhere in
the tree. Every existing target that defines `USE_IMU_ICM42688P`
(`AIKONF4V3`, `DAKEFPVF722X8`) also defines `USE_IMU_ICM42605` — the
`ICM42688P` block is pure decoration riding on the `ICM42605` block
actually doing the work. **If a board's Betaflight source lists only
`ICM42688P` with no `ICM42605`** (this is the case for the queued
`AXISFLYINGH743PRO` and `AXISFLYINGECOF4` tasks), the correct INAV
translation is `USE_IMU_ICM42605` + `ICM42605_CS_PIN`/`ICM42605_SPI_BUS`/
`IMU_ICM42605_ALIGN` (the "605" name, even though the physical chip is a
688P) — **not** `USE_IMU_ICM42688P` alone, which would leave the gyro
completely undetected on real hardware. Flagged to the manager
2026-07-06 for both of those tasks.

Once you've confirmed the real macro, add it as an *additional* block on
the **same** bus/CS/EXTI as the sibling entries already in that target.h
when a target genuinely has multiple distinct chip options (INAV
auto-detects at boot via `WHO_AM_I`) — just don't assume every
`USE_ACC_SPI_<X>` in a Betaflight source maps 1:1 to its own working INAV
macro.

If no driver exists (as was the case for `LSM6DSV16X`/`LSM6DSK320X` on
2026-07-06 — INAV's `accgyro_lsm6dxx.c` only recognizes `LSM6DSO`,
`LSM6DSL`, `LSM6DS3` chip IDs, not the newer DSV16X/DSK320X silicon), do
**not** try to write a new driver as a side effect of a target-update
task — flag it to the manager as a separate, larger project. Writing a
new accgyro driver needs the chip's register map/datasheet and its own
design+review, not just target.h wiring. (Datasheets for
`LSM6DSK320X`, `LSM6DSV16XTR`, and a related `LQTP001HTA` board are in
`claude/developer/docs/targets/` as of 2026-07-06 if that project gets
scoped.)

### 3b. `USE_UARTn_PIN_SWAP` is a per-board hardware fact, not a convention

`USE_UART7_PIN_SWAP` (and the equivalent for other UARTs) tells the STM32
UART peripheral to swap which of two AF-identical pins it treats as TX vs
RX (`UART_ADVFEATURE_SWAP` in `serial_uart_stm32h7xx.c`) — this exists
because some UART pin pairs share one AF value for both roles, so the
silicon needs a separate register to say which one is actually TX. In
practice it exists to **match the board's silkscreen labeling** — the
schematic brings both pins out to pads/pins, and the manufacturer picks
which physical pin gets printed "TX" vs "RX" on the board; the swap flag
makes the firmware's TX/RX assignment match what's printed, not the other
way around.
**Whether a given board needs it depends on that board's own PCB
routing, not on what other targets do.** Found 2026-07-06: of ~40 H7/F7
targets using `UART7_TX_PIN PE8`/`UART7_RX_PIN PE7`, only
`DAKEFPVH743_SLIM` sets `USE_UART7_PIN_SWAP` — initially assumed to be a
copy-paste bug by majority-vote reasoning, but it's genuinely correct for
that board's wiring. Don't infer swap correctness from cross-target
consistency; instead trust (in order): (a) the source manufacturer config
for *this specific* board, if it says anything about a swap, (b) a
sibling target from the **same manufacturer/board family** if one exists.

### 4. MCU macro → `CMakeLists.txt`

| Betaflight `FC_TARGET_MCU` | CMakeLists.txt call |
|---|---|
| `STM32F405` | `target_stm32f405xg(<BOARD> ...)` |
| `STM32F411` | `target_stm32f411xe(<BOARD> ...)` |
| `STM32F7X2` | `target_stm32f722xe(<BOARD> ...)` |
| `STM32F745` | `target_stm32f745xg(<BOARD> ...)` |
| `STM32H743` | `target_stm32h743xi(<BOARD> ...)` |
| `AT32F435G`/`AT32F435M` | `target_at32f43x_xGT7`/`target_at32f43x_xMT7` |

(Source: `mcu2target()` in `bf2inav.py` — this part of the script is
correct and reusable even when hand-porting.)

### 5. Reference-target selection

Prefer, in order: (a) another target from the **same manufacturer**
(config.c/PINIO naming conventions tend to be copy-pasted within a
manufacturer's target family), (b) another target with the **same MCU**
and similar gyro count/bus layout, (c) the generic simplest target for
that MCU family. For dual-gyro-with-CLKIN-sync boards specifically, search
for existing `GYRO_2_CLKIN_PIN`/`GYRO_CONFIG_USE_GYRO_BOTH` usage — this
combination is rare enough that most targets won't have it.

---

## Process Checklist

1. Confirm the target doesn't already exist (or does, if the manager
   framed it as new).
2. Diff Betaflight `config.h` against existing `target.h` line-by-line
   (or, for a new target, run `bf2inav.py` for a first draft, then apply
   the rules above to what it gets wrong).
3. Delegate the actual `target.h`/`config.c`/`target.c` edits to the
   `target-developer` agent — it knows the pin/timer/DMA conflict rules.
4. Build the **hardware target**, not SITL, via `inav-builder`.
5. If a required chip has no INAV driver, flag it — don't silently drop
   it and don't write a new driver inline.

---

## Related Files

- `inav/src/utils/bf2inav.py` — the generator (has known gaps above)
- `inav/docs/development/Converting Betaflight Targets.md` — generator usage docs
- `claude/agents/target-developer/` — agent + `check_macro_typos.py` (catches
  typo'd macros like a stray `_PIN` suffix on a non-pin macro)
- `src/main/target/DAKEFPVF722X8/target.h` — good reference for multiple
  IMU chips (MPU6000, ICM42605, BMI270, ICM42688P) coexisting on one bus
