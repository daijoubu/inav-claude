# M7: Motor Output — DShot via PIO — Reference

**Goal:** Motors spin on bench (props off!); DShot ERPM telemetry visible in CLI.
**BF reference:** `dshot_pico.c` (393 LOC), `dshot_bidir_pico.c` (~300 LOC), `dshot.pio`

> **About the search tool:** The `search.py` script at `~/Documents/planes/rpi_pico_2350_port/`
> searches thousands of pages of pre-project research — including a detailed implementation guide
> (PDF + MD, 3,000+ lines), Betaflight PR analysis, and a full Claude research session. Use it to
> quickly find relevant implementation details without reading everything.

## Quick Searches
```bash
cd ~/Documents/planes/rpi_pico_2350_port
./search.py DShot
./search.py --doc MD DShot    # → sections at lines 807, 817, 937
./search.py --doc PDF PIO     # motor PIO details
./search.py --doc CHAT pico-bidir-dshot
./search.py --list-sections | grep -iE 'dshot|motor|pio|bidir|gcr'
# Also read the dedicated DShot file:
head -100 ~/Documents/planes/rpi_pico_2350_port/inav_rp2350_dshot.txt
```
Read sections:
- DShot PIO: `offset=807, limit=130` (includes wrapper code)
- DShot Protocol Details: `offset=937, limit=80`
- PIO Resource Usage: `offset=963, limit=60`

---

## PIO Block Allocation (from target.h)

```c
#define PIO_DSHOT_INDEX    0   // PIO0 — motor DShot
#define PIO_UART_INDEX     1   // PIO1 — software UARTs (M6)
#define PIO_LEDSTRIP_INDEX 2   // PIO2 — WS2812 (M12, RP2350B only)
```
PIO0 has 8 state machines (SM), PIO1 has 4. RP2350B has PIO2 with 4 more.
**1 SM per motor** → max 4 motors on PIO0 (with some SMs reserved).

---

## Approach A: BF Native PIO Implementation (Recommended)

BF PR #14618 wrote DShot in pure PIO assembly (`.pio` files). This is what INAV should mirror.

### PIO Programs
- `dshot_600_program` — unidirectional DShot (`dshot.pio`)
- `dshot_600_bidir_program` — bidirectional DShot+telemetry

Programs are loaded ONCE, shared across all motor SMs:
```c
uint offset = pio_add_program(pio0, &dshot_600_bidir_program);
for (int i = 0; i < motorCount; i++) {
    dshot_program_init(pio0, i, offset, motorPins[i]);
}
```

### Synchronized Motor Update
```c
// dshotUpdateComplete() — BF dshot_pico.c pattern:
// 1. Stop all SMs
for (int i = 0; i < motorCount; i++) pio_sm_set_enabled(pio0, i, false);
// 2. Load TX FIFOs with new values
for (int i = 0; i < motorCount; i++) pio_sm_put(pio0, i, dshotPacket[i]);
// 3. Restart all simultaneously (single mask write → same cycle)
pio_enable_sm_mask_in_sync(pio0, motorSmMask);
```
This ensures all motors update at exactly the same time.

### GPIO Base for Pins 16-47 (CRITICAL)
```c
// If motor pins are 16+, must set PIO GPIO base
pio_set_gpio_base(pio0, 16);  // BF dshot_pico.c:294-302
// Then pin offsets in PIO programs are relative to base
```

### Pin Pulldown When Idle
```c
gpio_set_pulls(motorPin, false, true);  // pulldown (BF pattern)
```

---

## Approach B: pico-bidir-dshot Library (Alternative)

Library: https://github.com/bastian2001/pico-bidir-dshot
- 28 PIO instructions per motor, 1 SM per ESC
- Bidirectional DShot up to DShot 1200
- Handles timing asynchronously

```bash
git submodule add https://github.com/bastian2001/pico-bidir-dshot.git lib/pico-bidir-dshot
```

```cmake
add_subdirectory(lib/pico-bidir-dshot)
target_link_libraries(RP2350_PICO pico_bidir_dshot)
```

```c
// Wrapper (motor_dshot_rp2350.c):
#include "PIO_DShot.h"

BidirDShotX1 *dshotMotors[MAX_MOTORS];

void motorDevInit(...) {
    for (int i = 0; i < motorCount; i++) {
        dshotMotors[i] = new BidirDShotX1(motorPins[i], 600);
    }
}

void pwmWriteMotor(uint8_t idx, uint16_t value) {
    // INAV: 1000-2000, DShot: 48-2047 (0-47 reserved for commands)
    uint16_t dshot = (value < 1000) ? 0 :
                     48 + ((value - 1000) * 1999) / 1000;
    dshotMotors[idx]->sendThrottle(dshot);
}

uint32_t pwmGetMotorErpm(uint8_t idx) {
    uint32_t erpm;
    dshotMotors[idx]->getTelemetryErpm(&erpm);
    return erpm;
}
```

---

## Bidirectional DShot Telemetry (GCR)

BF `dshot_bidir_pico.c`:
- PIO captures response from ESC in RX FIFO
- GCR decode: 5-bit groups → 4-bit nibbles → 12-bit packet (ERPM or extended)
- CRC validation on decoded packet
- `dshotDecodeTelemetry()` reads PIO FIFO, decodes, stores ERPM

---

## DShot Protocol Values

| Value | Meaning |
|-------|---------|
| 0 | Motor stop |
| 1-47 | Special commands (beep, direction, etc.) |
| 48-2047 | Throttle (maps to 1000-2000 from INAV) |

### Special DShot Commands (send 10× each)
```c
// DSHOT_CMD_MOTOR_STOP = 0
// DSHOT_CMD_SPIN_DIRECTION_NORMAL = 20
// DSHOT_CMD_SPIN_DIRECTION_REVERSED = 21
// DSHOT_CMD_SAVE_SETTINGS = 12
void pwmWriteDshotCommand(uint8_t idx, uint8_t cmd) {
    for (int i = 0; i < 10; i++) {
        dshotMotors[idx]->sendThrottle(cmd);
        sleep_us(200);
    }
}
```

---

## Why PIO DShot is Better Than STM32

1. **No DMA config needed** — PIO handles it in hardware
2. **No timer conflicts** — STM32 has limited shared timers
3. **Zero CPU overhead** — PIO runs independently
4. **Built-in bidir telemetry** — no complex edge detection
5. **Jitter resistant** — PIO hardware handles timing

---

## Verification

```bash
# CLI:
status        # Check motor output enabled
motor 0 1050  # Spin motor 0 at low throttle (PROPS OFF!)
# Configurator → Motors tab → enable motor test → spin with slider
# CLI: 'status' or dedicated ERPM display → check ERPM values updating
```
