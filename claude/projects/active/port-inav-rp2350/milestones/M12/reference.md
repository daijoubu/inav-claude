# M12: Feature Complete — OSD, Blackbox, LED Strip, Polish — Reference

**Goal:** Full-featured flight: OSD overlay, blackbox downloadable, LED strip, full configurator.
**BF reference:** `light_ws2811strip_pico.c` (242 LOC), `multicore.c` (134 LOC), `usb/usb_msc_pico.c`

> **About the search tool:** The `search.py` script at `~/Documents/planes/rpi_pico_2350_port/`
> searches thousands of pages of pre-project research — including a detailed implementation guide
> (PDF + MD, 3,000+ lines), Betaflight PR analysis, and a full Claude research session. Use it to
> quickly find relevant implementation details without reading everything.

## Quick Searches
```bash
cd ~/Documents/planes/rpi_pico_2350_port
./search.py multicore
./search.py --doc PDF OSD
./search.py --doc PDF blackbox
./search.py --doc MD "LED strip"
./search.py --doc CHAT WS2812
./search.py --doc PDF MSC
./search.py --list-sections | grep -iE 'osd|blackbox|led|multicore|msc|persistent'
# Read the dedicated files:
cat inav_rp2350_dshot.txt    # DShot timing notes relevant to perf
cat rp2350_hal_wrappers.txt  # HAL wrapper patterns
cat accuracy_analysis.md     # Timing accuracy analysis
```
Read sections: USB MSC at `offset=1581, limit=80`

---

## OSD (MAX7456 over SPI)

MAX7456 connects via SPI — should "just work" once M5 SPI driver is solid.
- Same SPI driver as gyro (M5); different SPI bus or same bus with different CS
- INAV's MAX7456 driver is platform-agnostic

### Optional: Dual-Core OSD Offload

BF `multicore.c` (134 LOC) runs OSD on core 1, flight control on core 0:

```c
// Core 0 (flight control):
void core0_main(void) {
    systemInit();
    multicore_launch_core1(core1_osd_task);  // start core 1

    // Spinlock to protect shared OSD data
    spin_lock_t *osdLock = spin_lock_init(spin_lock_claim_unused(true));

    while (true) {
        scheduler();  // all flight control tasks

        if (shouldUpdateOSDData()) {
            uint32_t save = spin_lock_blocking(osdLock);
            // Copy telemetry to shared osdData struct
            osdData.batteryVoltage = getBatteryVoltage();
            osdData.gpsSats = gpsSol.numSat;
            osdData.altitude = getEstimatedActualPosition(Z);
            osdData.armed = ARMING_FLAG(ARMED);
            spin_unlock(osdLock, save);
        }
    }
}

// Core 1 (OSD):
void core1_osd_task(void) {
    while (true) {
        uint32_t save = spin_lock_blocking(osdLock);
        // Read osdData snapshot
        spin_unlock(osdLock, save);
        // Write to MAX7456
        max7456DrawScreen(...);
    }
}
```

**BF Message Queue:**
- Core 0 → Core 1: size 4 (fire-and-forget commands: FUNC, FUNC_BLOCKING)
- Core 1 → Core 0: size 1

---

## Blackbox Logging

### SPI Flash (primary)
```c
// Non-blocking writes via DMA:
// Write header to flash, then stream gyro/nav data each cycle
// Log to dedicated SPI flash chip (W25Q128 or similar)
// Same SPI driver as M5; different CS pin
```
- SD card also supported — MISO pull-up already handled in M5 SPI driver

### USB MSC (Blackbox Download)
BF `usb/usb_msc_pico.c` — TinyUSB CDC+MSC switching:
```c
// When user clicks "Download Logs" in Configurator:
// Switch USB from CDC (MSP) to MSC (mass storage)
// Flash/SD appears as USB drive
// User copies log files
// Reboot to return to CDC mode
```
From `inav_rp2350_detailed.md` line 1581.

---

## LED Strip (`light_ws2811strip_rp2350.c`)

Uses PIO block 2 (`PIO_LEDSTRIP_INDEX=2`) + DMA:

```c
// 4-instruction PIO program for WS2812 timing:
// Inline in BF light_ws2811strip_pico.c (no separate .pio file)
// Program timing: 0-bit = 350ns high, 900ns low; 1-bit = 900ns high, 350ns low

// DMA: transfer led_data[] buffer → PIO TX FIFO (non-blocking)
uint dma_ch = dma_claim_unused_channel(true);
dma_channel_config cfg = dma_channel_get_default_config(dma_ch);
channel_config_set_dreq(&cfg, pio_get_dreq(pio2, sm, true));
dma_channel_configure(dma_ch, &cfg,
    &pio2->txf[sm],  // PIO TX FIFO
    led_data,         // source
    ledCount,         // transfer count
    false);

// Reset guard: wait ≥50μs between transfers (WS2812 reset)
// DMA completion IRQ sets transfer-complete flag

// Color formats: GRB (most common), RGB, GRBW
```

---

## Persistent Data (`persistent_rp2350.c`)

Replaces STM32's RTC backup registers for data that survives soft reset.

```c
// Linker script addition needed:
// .uninitialized_data.persistent (section NOT zeroed on reset)

typedef struct {
    uint32_t magic;           // validated on read
    uint32_t resetReason;
    uint32_t bootloaderRequest;
} persistentData_t;

#define PERSISTENT_MAGIC  0xDEADBEEF

void persistentObjectWrite(persistentObjectId_e id, uint32_t value) {
    if (persistent->magic != PERSISTENT_MAGIC) {
        memset(persistent, 0, sizeof(*persistent));
        persistent->magic = PERSISTENT_MAGIC;
    }
    // write field by id
}

uint32_t persistentObjectRead(persistentObjectId_e id) {
    if (persistent->magic != PERSISTENT_MAGIC) return 0;
    // read field by id
}
```
Used for: bootloader requests, reset reasons, crash recovery flags.

---

## Math Optimization (verify from M1)

The DCP (Double Coprocessor) linker wraps must be in place from M1:
```
37 pico_float wraps + 50 pico_double wraps in cmake/rp2350.cmake
```
Verify float math uses DCP (significant speedup for PID, nav calculations):
```c
// Quick test — PID loop should run faster than software FP:
uint32_t t0 = getCycleCounter();
float result = arm_sin_f32(angle);  // should use DCP
uint32_t t1 = getCycleCounter();
// Compare cycles vs STM32 FPU equivalent
```

---

## Beeper

Hardware PWM (same slices as M8 servo/motor, different frequency):
```c
// Beeper frequency: typically 2-4kHz
// Use a free PWM slice and vary duty cycle for on/off
pwm_set_gpio_level(BEEPER_PIN, beep_on ? BEEPER_HALF_DUTY : 0);
```

---

## Flash-Safe Multicore Writes (from M4)

When multicore is active, flash writes need special handling:
```c
// Use flash_safe_execute() instead of bare save_and_disable_interrupts()
// This pauses core 1 before erasing/programming flash
flash_safe_execute(configFlashWriteCore, &writeParams, UINT32_MAX);
```
(BF noted this requirement too.)

---

## Performance Profiling

```bash
# CLI commands for cycle time:
status           # shows cycle time in μs
tasks            # shows task timing breakdown
# Target: cycle time ≤ 250μs (4kHz) or ≤ 125μs (8kHz)
# CPU load ≤ 70% of cycle budget
```

---

## Upstream PR Checklist

- [ ] All tests passing (bench + flight)
- [ ] `src/main/target/RP2350_PICO/` complete with proper pin mapping
- [ ] README / setup guide for Pico 2 hardware wiring
- [ ] No `#ifdef STM32` leaking into RP2350 code paths
- [ ] Builds clean with `-Wall -Werror` equivalent
- [ ] Submit RFC to INAV Discord/GitHub before formal PR
