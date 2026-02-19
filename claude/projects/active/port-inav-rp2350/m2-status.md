# RP2350 Milestone 2 — Status & TODO

**Date:** 2026-02-17
**Branch:** `feature/rp2350-port`
**Latest commit:** `f60e62b3ae` — "RP2350 Milestone 2: System timing, GPIO, USB debug, and UF2"
**Pushed to:** `origin/feature/rp2350-port`

## Completed Work

All software implementation is done and committed:

### Files created (6 new):
- `src/main/target/RP2350_PICO/system_rp2350.c` — Real system timing, reset, unique ID
- `src/main/drivers/io_rp2350.c` — GPIO abstraction using Pico SDK
- `src/main/target/RP2350_PICO/pico_sdk_config.h` — Custom SDK config (replaces auto-generated)
- `src/main/target/RP2350_PICO/pico/version.h` — SDK version header (normally cmake-generated)
- `src/main/target/RP2350_PICO/tusb_config.h` — TinyUSB CDC configuration
- `src/utils/elf2uf2.py` — Python UF2 converter with RP2350 family ID (also, picotool is installed at /usr/local/bin/picotool)

### Files modified (5):
- `cmake/rp2350.cmake` — Added ~45 SDK + 7 TinyUSB sources, UF2 post-build step
- `src/main/drivers/io.h` — RP2350-specific IOCFG defines (bit 0=dir, bit 5=pullup, bit 6=pulldown)
- `src/main/target/RP2350_PICO/target.h` — LED0=PB9, TARGET_IO_PORTx, removed DEFIO_NO_PORTS
- `src/main/target/RP2350_PICO/target.c` — Removed stubs moved to system_rp2350.c/io_rp2350.c
- `src/main/target/link/rp2350_flash.ld` — SDK crt0.S symbol compatibility

### Build output:
- Flash: 779KB / 4032KB (18.88%)
- RAM: 104KB / 512KB (20.00%)
- UF2: `build_rp2350/inav_9.0.0_RP2350_PICO.uf2` (1.5MB, 3045 blocks)

### Key technical decisions:
- GPIO 0-15 mapped to Port A, GPIO 16-29 to Port B (fits ioTag_t 4-bit pin encoding)
- LED0 = PB9 = GPIO 25 (Pico 2 onboard LED)
- C11 per-target override for Pico SDK compatibility (INAV uses C99 globally)
- pico_malloc excluded (--wrap=malloc conflicts with INAV)
- _fstat/_isatty stubs with __attribute__((used)) to survive -Wl,-gc-sections

## TODO — Hardware Verification

The Pico 2 was not detected on USB during this session. After reboot:

### 1. Detect Pico 2
```bash
lsusb | grep 2e8a    # Raspberry Pi vendor ID
ls /dev/ttyACM*       # USB CDC serial port
```

### 2. Flash via BOOTSEL
1. Hold **BOOTSEL** button on Pico 2
2. Connect USB (or reset while holding BOOTSEL)
3. Should appear as USB mass storage device (RP2350)
4. Copy UF2:
```bash
cp build_rp2350/inav_9.0.0_RP2350_PICO.uf2 /media/$USER/RP2350/
```

### 3. Verify success criteria
- [ ] LED on GPIO 25 blinks at ~1Hz (warningLedFlash via scheduler)
- [ ] USB serial shows "INAV RP2350 booting..."
```bash
# Open serial terminal (baud rate doesn't matter for USB CDC)
minicom -D /dev/ttyACM0
# or
screen /dev/ttyACM0
```
- [ ] `systemReset()` works (test via MSP or CLI if available)
- [ ] `systemResetToBootloader()` puts Pico back into BOOTSEL mode

### 4. If LED doesn't blink
Debug checklist:
- Check if firmware boots at all (USB serial output?)
- If no USB: LED should still blink if scheduler runs
- If LED stays solid ON: systemInit() ran but scheduler didn't start
- If LED stays OFF: boot2/crt0 startup issue
- Try connecting SWD debugger for more info

### 5. After hardware verification passes
- Update completion report status from "MOSTLY COMPLETE" to "COMPLETE"
- Mark task #14 as completed
- Notify manager

## Lock Status

inav.lock: RELEASED (re-acquire before any code changes)

## Completion Report

Sent to manager inbox: `claude/developer/email/sent/2026-02-16-2100-completed-rp2350-milestone-2.md`
