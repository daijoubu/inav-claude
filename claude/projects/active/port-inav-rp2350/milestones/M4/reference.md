# M4: Configurator Connects — Reference

**Goal:** INAV Configurator connects, shows board name + firmware version + sensor status.
**BF reference:** `config_flash.c` (72 LOC)

> **About the search tool:** The `search.py` script at `~/Documents/planes/rpi_pico_2350_port/`
> searches thousands of pages of pre-project research — including a detailed implementation guide
> (PDF + MD, 3,000+ lines), Betaflight PR analysis, and a full Claude research session. Use it to
> quickly find relevant implementation details without reading everything.

## Quick Searches
```bash
cd ~/Documents/planes/rpi_pico_2350_port
./search.py --doc PDF flash
./search.py --doc MD flash
./search.py --doc CHAT MSP
./search.py --doc PDF config
./search.py --list-sections | grep -iE 'flash|config|msp|cli|settings'
```
Read sections:
- Config / flash: `./search.py --doc MD config` → find line numbers, then read

---

## MSP Messages Required for Configurator

All in INAV's existing MSP layer — should work once USB VCP (M3) is solid:

| MSP Message | Code | Notes |
|------------|------|-------|
| `MSP_API_VERSION` | 1 | Protocol version |
| `MSP_FC_VARIANT` | 2 | "INAV" |
| `MSP_FC_VERSION` | 3 | Major.minor.patch |
| `MSP_BOARD_INFO` | 4 | Board identifier "RP2350_PICO" |
| `MSP_BUILD_INFO` | 5 | Build date/time/git hash |
| `MSP_STATUS` | 101 | Cycle time, sensor flags, arming |
| `MSP_STATUS_EX` | 240 | Extended status |
| `MSP_SENSOR_STATUS` | 151 | All "not detected" is OK for M4 |
| `MSP_ACTIVEBOXES` | 113 | Active flight modes |
| `MSP_BOXIDS` | 119 | Flight mode identifiers |
| `MSP_BOXNAMES` | 116 | Flight mode names |

---

## Flash Config Storage (`flash_rp2350.c`)

### Memory Region
```c
// From linker script (M1):
// FLASH_CONFIG: 0x103F0000, 64K
extern uint32_t __config_start;
extern uint32_t __config_end;
```

### Write (Erase + Program)
```c
#include "hardware/flash.h"
#include "hardware/sync.h"

void configFlashWrite(const void *data, uint32_t len) {
    uint32_t flashOffset = (uint32_t)&__config_start - XIP_BASE;

    // MUST disable interrupts during flash operations
    uint32_t ints = save_and_disable_interrupts();

    // Erase: 4KB sector boundary
    flash_range_erase(flashOffset, FLASH_SECTOR_SIZE);  // 4096 bytes

    // Program: 256-byte page aligned
    flash_range_program(flashOffset, (const uint8_t*)data, len);

    restore_interrupts(ints);
}
```

**CRITICAL:** `save_and_disable_interrupts()` / `restore_interrupts()` are MANDATORY for flash ops.
(BF `config_flash.c:55-56`)

**TODO for multicore (M12):** use `flash_safe_execute()` — currently just disable interrupts.

### Read
```c
// Flash is memory-mapped at XIP_BASE (0x10000000)
// Config region is directly readable:
const uint8_t *configData = (const uint8_t*)&__config_start;
// Just read it like normal RAM — no special API needed
```

### RAM-only Fallback
For initial bring-up, skip flash writes entirely — config resets on every reboot.
Use `#define USE_CONFIG_RAM_ONLY` to stub out flash write until flash is confirmed working.

---

## CLI Interface

INAV's CLI is platform-agnostic — just needs a serial port connected. For M4:
- Connect CLI to USB VCP port (already done via M3)
- Test commands: `status`, `version`, `set`, `save`, `defaults`, `reboot`

```bash
# Via picocom or similar:
# > version
# INAV 9.x ... RP2350_PICO
# > status
# System Uptime: 12 seconds ...
# > save
# Saving...
```

---

## `target.h` Board Identity

```c
// In src/main/target/RP2350_PICO/target.h
#define TARGET_BOARD_IDENTIFIER "RP23"  // 4 chars, shown in configurator
#define FC_TARGET_MCU           STM32F4 // TEMPORARY — will need new enum value
// OR define RP2350 MCU type in common header
```

---

## Sensor Status for M4

It's fine for all sensors to report "not detected" at this stage:
```c
// MSP_SENSOR_STATUS response:
// gyro: 0 (not detected), baro: 0, mag: 0, gps: 0
// Configurator will show no sensors — that's expected for M4
```
Real sensors come in M5 (SPI/gyro), M6 (GPS), M9 (I2C/baro/mag).

---

## Verification Sequence

1. Flash firmware to Pico 2
2. Open INAV Configurator
3. Select USB serial port (e.g. `/dev/ttyACM0`, `COM3`)
4. Click "Connect"
5. Expected: board name "RP2350_PICO", firmware version, sensor status (all N/A)
6. Check "Summary" tab — should show board info without crashing
