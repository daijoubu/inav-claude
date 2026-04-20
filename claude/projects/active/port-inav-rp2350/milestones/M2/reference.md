# M2: System Tick, GPIO & LED Blink — Reference

**Goal:** LED blinks at 1Hz on real Pico 2; debug printf over USB serial.
**BF reference:** `system.c` (270 LOC), `io_pico.c` (198 LOC)

> **About the search tool:** The `search.py` script at `~/Documents/planes/rpi_pico_2350_port/`
> searches thousands of pages of pre-project research — including a detailed implementation guide
> (PDF + MD, 3,000+ lines), Betaflight PR analysis, and a full Claude research session. Use it to
> quickly find relevant implementation details without reading everything.

## Quick Searches
```bash
cd ~/Documents/planes/rpi_pico_2350_port
./search.py GPIO
./search.py --doc MD GPIO    # → sections at lines 456, 465, 534
./search.py --doc PDF timing
./search.py --doc CHAT DWT
./search.py --list-sections | grep -iE 'gpio|system|timing|interrupt|nvic'
```
Read sections:
- GPIO HAL: `offset=456, limit=120`
- GPIO Interrupts (EXTI): `offset=534, limit=80`

---

## System Timing (`system_rp2350.c`)

```c
// micros() — 32-bit, wraps at ~71 min. Use 64-bit if needed.
uint32_t micros(void) { return time_us_32(); }

// millis()
uint32_t millis(void) { return (uint32_t)(time_us_64() / 1000); }

// delay / delayMicroseconds
void delay(uint32_t ms)          { sleep_ms(ms); }
void delayMicroseconds(uint32_t us) { sleep_us(us); }

// Cycle counter for sub-microsecond timing
uint32_t getCycleCounter(void) { return m33_hw->dwt_cyccnt; }
// Enable DWT: m33_hw->demcr |= CoreDebug_DEMCR_TRCENA_Msk;
//             m33_hw->dwt_ctrl |= DWT_CTRL_CYCCNTENA_Msk;

// SystemCoreClock
void systemInit(void) {
    SystemCoreClock = clock_get_hz(clk_sys);  // typically 150 MHz
    stdio_init_all();  // enables USB CDC stdio for printf
}

// Reset
void systemReset(void) { watchdog_reboot(0, 0, 0); }
// If multicore active: multicore_reset_core1() first

// Bootloader (UF2 BOOTSEL)
void systemResetToBootloader(void) { rom_reset_usb_boot_extra(-1, 0, false); }

// Unique ID (8 bytes → 3x uint32_t)
void getUniqueId(uint32_t *id) {
    pico_unique_board_id_t board_id;
    pico_get_unique_board_id(&board_id);
    // map 8 bytes to 3 uint32_t fields
}
```

## GPIO Abstraction (`io_rp2350.c`)

**CRITICAL: `IOConfigGPIO()` — do NOT call `gpio_init()` unconditionally.**
- `gpio_init()` resets output level to LOW — breaks SPI CS pins that should be HIGH.
- Fix (BF PR #14707): Only call `gpio_init()` when `gpio_get_function(pin) == GPIO_FUNC_NULL`.

```c
void IOConfigGPIO(IO_t io, ioConfig_t cfg) {
    uint pin = IO_Pin(io);
    // CRITICAL: preserve output state on reconfigure
    if (gpio_get_function(pin) == GPIO_FUNC_NULL) {
        gpio_init(pin);
    }
    // Set direction from cfg
    gpio_set_dir(pin, (cfg & IOCFG_OUT) ? GPIO_OUT : GPIO_IN);
    // Pullup/pulldown
    gpio_set_pulls(pin, (cfg & IOCFG_PULL_UP), (cfg & IOCFG_PULL_DOWN));
}

void IOHi(IO_t io)     { gpio_put(IO_Pin(io), 1); }
void IOLo(IO_t io)     { gpio_put(IO_Pin(io), 0); }
bool IORead(IO_t io)   { return gpio_get(IO_Pin(io)); }
void IOToggle(IO_t io) { gpio_xor_mask(1u << IO_Pin(io)); }

void IOInitGlobal(void) {
    // Assign pin numbers to ioRec_t array (single-port model, flat array)
    for (int i = 0; i < DEFIO_PORT_PINS; i++) {
        ioRecs[i].gpio = (GPIO_TypeDef*)0;  // not used
        ioRecs[i].pin  = i;
    }
}
IO_t IOGetByTag(ioTag_t tag) { return &ioRecs[DEFIO_TAG_PIN(tag)]; }
```

## NVIC / Interrupts

RP2350 Cortex-M33 uses NVIC — same API as STM32 Cortex-M4:
```c
#include "hardware/irq.h"
NVIC_EnableIRQ(irq);
NVIC_SetPriority(irq, priority);  // 0 = highest, 0-255
```
IRQ numbers from Pico SDK differ from STM32 — must remap in IRQ registration code.

## GPIO Interrupts (EXTI equivalent)

```c
// For gyro data-ready pin:
gpio_set_irq_enabled_with_callback(GYRO_EXTI_PIN,
    GPIO_IRQ_EDGE_RISE, true, &gpioIrqHandler);

// In handler:
void gpioIrqHandler(uint gpio, uint32_t events) {
    if (gpio == GYRO_EXTI_PIN) {
        // gyro data ready — schedule read
    }
}
```

## USB Debug Printf

```cmake
# CMakeLists.txt
target_link_libraries(RP2350_PICO pico_stdio_usb ...)
```
- `stdio_init_all()` in `systemInit()` — connects SDK printf to USB CDC
- Output visible on USB serial terminal (e.g. picocom, minicom, screen)
- Note: this is SDK-level stdio only; full INAV VCP abstraction is M3

## LED Blink

- Pico 2 onboard LED: **GPIO 25**
- In `target.h`: `#define LED0_PIN  DEFIO_TAG_E(25)`
- INAV scheduler runs LED blink task automatically once scheduler starts

## `IO_CONFIG` Macro

Pack direction + slew + pull into one byte (matches BF `io_pico.c` pattern):
```c
#define IO_CONFIG(mode, speed, pupd)  ((mode) | ((speed)<<2) | ((pupd)<<4))
```
