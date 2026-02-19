# Betaflight RP2350 Platform Analysis — Source Code Review

**Date:** 2026-02-15
**Source:** `betaflight/src/platform/PICO/` (local clone)
**Purpose:** Inform INAV RP2350 port by documenting actual BF implementation patterns

---

## Architecture Overview

Betaflight's RP2350 port lives entirely under `src/platform/PICO/` with this structure:

```
src/platform/PICO/
├── include/platform/
│   ├── platform.h          # Type aliases, IO_CONFIG macros, task timing
│   ├── dma.h               # DMA channel/identifier macros
│   ├── multicore.h         # Core 1 command interface
│   └── pwm.h               # picoPwmOutput_t struct
├── link/
│   ├── pico_rp2350_RunFromFLASH.ld   # 4MB flash + 512K RAM + 4K scratch x2
│   └── pico_rp2350_RunFromRAM.ld     # Copy-to-RAM variant
├── mk/
│   ├── RP2350.mk           # Build system: SDK sources, include paths, flags
│   └── PICO_trace.mk       # Debug tracing support
├── startup/
│   └── bs2_default_padded_checksummed.S  # Boot stage 2
├── target/
│   ├── RP2350A/target.h, target.mk  # 30-pin variant
│   └── RP2350B/target.h, target.mk  # 48-pin variant
├── uart/
│   ├── serial_uart_pico.c  # Dispatch: hw UART vs PIO UART
│   ├── serial_uart_pico.h  # Shared UART declarations
│   ├── uart_hw.c           # Hardware UART0/UART1 driver
│   ├── uart_pio.c          # PIO-based software UARTs (PIOUART0/1)
│   ├── uart_rx_program.c   # PIO RX program (generated from .pio)
│   └── uart_tx_program.c   # PIO TX program (generated from .pio)
├── usb/
│   ├── tusb_config.h       # TinyUSB configuration
│   ├── usb_cdc.c/h         # CDC (Virtual COM Port) implementation
│   ├── usb_descriptors.c   # USB device descriptors
│   └── usb_msc_pico.c      # Mass Storage Class for blackbox
├── pico/
│   ├── config_autogen.h    # Pico SDK config overrides
│   └── version.h           # SDK version
├── system.c                # micros/millis/delay, systemReset, cycle counter
├── io_pico.c               # GPIO: IORead/IOWrite/IOHi/IOLo/IOConfigGPIO
├── bus_spi_pico.c           # SPI: blocking + DMA, clock divider, pin config
├── bus_i2c_pico.c           # I2C: interrupt-driven, 16-byte FIFO batching
├── bus_quadspi_pico.c       # QSPI flash interface
├── dma_pico.c               # DMA: 16 channels, edge-triggered IRQ, per-core IRQ
├── dshot_pico.c             # DShot600 motor output via PIO
├── dshot_bidir_pico.c       # Bidirectional DShot telemetry via PIO
├── dshot.pio                # PIO assembly: dshot_600, dshot_600_bidir programs
├── dshot.pio.programs       # Pre-compiled PIO programs
├── dshot_pico.h             # DShot shared declarations
├── dshot_pio_programs.h     # PIO program symbols
├── pwm_motor_pico.c         # PWM motor output (Oneshot/Multishot/Brushed/PWM)
├── pwm_servo_pico.c         # Servo PWM output (50Hz, hardware PWM slices)
├── pwm_beeper_pico.c        # Beeper via PWM
├── adc_pico.c               # ADC: round-robin DMA, 1-4 channels
├── config_flash.c           # Flash config storage: sector erase + page program
├── exti_pico.c              # External interrupts (GPIO edge IRQ for gyro EXTI)
├── persistent.c             # Persistent data via .uninitialized_data section
├── serial_usb_vcp_pico.c    # USB VCP serial port adapter
├── light_ws2811strip_pico.c # WS2812 LED strip: PIO + DMA
├── multicore.c              # Core 1 message queue and task dispatch
├── debug_pico.c             # Debug output helpers
├── debug_pin.c              # Debug pin toggling
├── pico_trace.c/h           # UART-based debug tracing
├── stdio_pico_stub.c        # stdio stubs
└── io_def_generated.h       # Generated IO definitions
```

**Total: ~30 source files implementing the full platform layer.**

---

## File-by-File Key Findings

### 1. `system.c` — Timing & System Control

**Key patterns:**
- `micros()` uses `time_us_32()` from Pico SDK (hardware timer, not DWT)
- `millis()` uses `time_us_64() / 1000` (64-bit for rollover safety)
- `delay()`/`delayMicroseconds()` use SDK `sleep_ms()`/`sleep_us()`
- `getCycleCounter()` uses DWT CYCCNT (Cortex-M33 has DWT just like M4)
- `systemReset()` uses `watchdog_reboot(0, 0, 0)` — resets core 1 first if multicore
- `systemResetToBootloader()` uses `rom_reset_usb_boot_extra(-1, 0, false)` for UF2 BOOTSEL mode
- `SystemCoreClock` populated via `clock_get_hz(clk_sys)`
- `cycleCounterInit()` enables DWT CYCCNT via M33 debug registers (`m33_hw->dwt_ctrl`, `m33_hw->demcr`)
- Unique ID read from `pico_get_unique_board_id()` (8 bytes mapped to 3x uint32_t)

**INAV translation:** Very similar to what INAV needs. The cycle counter and DWT code is directly portable. INAV's `system.c` already has similar functions.

### 2. `io_pico.c` — GPIO Abstraction

**Key patterns:**
- Single GPIO port (no multi-port like STM32) — `DEFIO_PORT_USED_COUNT` must be 1
- `IOInitGlobal()` just assigns pin numbers 0..N to ioRec_t array
- `IORead()/IOWrite()/IOHi()/IOLo()/IOToggle()` map directly to `gpio_get()`/`gpio_put()`
- `IOConfigGPIO()` handles the **gpio_init() gotcha** — only calls `gpio_init()` when function is `GPIO_FUNC_NULL`, not when already SIO. This prevents resetting output levels on SPI CS pins.
- `IOGetByTag()` returns `&ioRecs[pinIdx]` — simple flat array lookup
- `IO_CONFIG(mode, speed, pupd)` macro packs GPIO direction, slew rate, and pull config into a single byte
- Pullup/pulldown via `gpio_set_pulls()`

**INAV translation:** INAV's IO system is slightly different but the single-port model works. Need `DEFIO_PORT_USED_COUNT=1` and `DEFIO_PORT_PINS=30/48` depending on variant.

### 3. `bus_spi_pico.c` — SPI Driver

**Key patterns:**
- Two SPI devices (SPI0, SPI1) with up to 6 pin options each (RP2350B has more)
- Pin mapping uses `DEFIO_TAG_E(PAn)` format (PAn = GPIO pin n)
- `spiInitDevice()` calls `spi_init()` from SDK, then `gpio_set_function()` for MISO/MOSI/SCK
- **MISO pullup enabled** on init: `gpio_set_pulls(miso, true, false)` — prevents SD card float issue
- SPI clock: Custom `spiCalculateDivider()` packs prescale+postdiv into uint16_t, `spiCalculateClock()` reverses it for `spi_set_baudrate()`
- **Blocking transfers:** `spi_write_read_blocking()`, `spi_write_blocking()`, `spi_read_blocking()` with 0xff dummy TX byte
- **DMA transfers:** TX and RX channels allocated dynamically via `dma_claim_unused_channel()`, DMA uses SDK's `dma_channel_configure()` with DREQ from `spi_get_dreq()`
- DMA completion: IRQ on RX channel completion triggers `spiRxIrqHandler()` which negates CS and dispatches
- SPI format switching: `spi_set_format()` for CPOL/CPHA modes, `gpio_set_slew_rate(FAST)` on SCK
- DMA threshold: Only use DMA for transfers >= 8 bytes

**INAV translation:** SPI bus abstraction is very similar between BF and INAV. The DMA pattern maps well. Need to adapt INAV's `busDevice_t` to use Pico SDK SPI.

### 4. `bus_i2c_pico.c` — I2C Driver (Interrupt-Driven)

**Key patterns:**
- **NOT DMA-based** — uses interrupt-driven I2C with 16-byte FIFO batching
- Two I2C devices (I2C0, I2C1)
- Pin validation: I2C0 on pins where `pin % 4 == 0/1`, I2C1 where `pin % 4 == 2/3`
- State machine: `I2C_STATE_IDLE`, `I2C_STATE_ACTIVE`, `I2C_STATE_READ_DATA`
- Write: Preloads TX FIFO with register address + data bytes + STOP bit on last byte
- Read: Single-batch if len <= 15 (FIFO - 1 for reg byte), multi-batch with `I2C_IC_DATA_CMD_RESTART_BITS` and FIFO-full interrupt for reads > 15 bytes
- Interrupts: STOP_DET, TX_ABRT, TX_OVER, RX_OVER, RX_FULL
- Direct register manipulation: `hw->data_cmd`, `hw->tar`, `hw->enable`, `hw->intr_mask`
- FIFO threshold: `hw->rx_tl = I2C_FIFO_BUFFER_DEPTH - 2` (prevents race condition)
- Non-blocking API: `i2cWriteBuffer()`/`i2cReadBuffer()` start transfer, `i2cBusy()` polls completion

**INAV translation:** INAV's I2C bus also supports non-blocking operation. The interrupt-driven approach is more responsive than polling for sensor reads. Key difference: no DMA needed for I2C.

### 5. `dma_pico.c` — DMA Channel Management

**Key patterns:**
- 16 DMA channels on RP2350 (12 on RP2040)
- **Edge-triggered IRQs** — acknowledge BEFORE calling callback (`dma_channel_acknowledge_irq0/1()` before handler dispatch). This is the critical gotcha from BF PR #14514.
- Per-core IRQ routing: DMA_IRQ_0 on core 0, DMA_IRQ_1 on core 1 (configurable via `DMA_IRQ_CORE_NUM`)
- Dynamic channel allocation: `dma_claim_unused_channel(false)` for optional, `true` for required
- Handler table: `dmaDescriptors[DMA_LAST_HANDLER]` with `irqHandlerCallback` function pointers
- `dmaSetHandler()` registers IRQ handler on first call, enables per-channel IRQ

**INAV translation:** INAV's DMA is statically mapped on STM32. The RP2350's dynamic allocation is simpler. Need `dma_rp2350.c` with similar dispatch pattern.

### 6. `dshot_pico.c` + `dshot_bidir_pico.c` — Motor Output

**Key patterns:**
- Uses PIO block 0 (`PIO_DSHOT_INDEX=0`) — one state machine per motor, max 4 motors
- PIO program loaded once, shared across all motor SMs
- GPIO base handling: PIO can address pins 0-31 or 16-47 (set via `pio_set_gpio_base()`)
- DShot600 only currently (300/150 TODO)
- **Unidirectional:** `dshot_600_program` — TX only via PIO, pin is output
- **Bidirectional:** `dshot_600_bidir_program` — TX then RX on same pin, GCR decoding
- `dshotUpdateComplete()`: Stops all motor SMs, loads TX FIFOs, restarts simultaneously (synchronized output)
- Telemetry: `dshotDecodeTelemetry()` reads PIO RX FIFO, GCR decodes, checks CRC
- Pin pulldown when idle: `gpio_set_pulls(pin, false, true)`

**INAV translation:** INAV's motor output uses different abstraction but the PIO DShot implementation is directly reusable. The `.pio` assembly programs are the key artifact.

### 7. `pwm_servo_pico.c` — Servo Output

**Key patterns:**
- Uses RP2350's hardware PWM slices (NOT PIO)
- 50Hz servo frequency, PWM_PRESCALER=64, TOP count ~39063
- `US_TO_COUNTS_FACTOR` = ~1.953 counts/us at 125MHz/64
- `servoWrite()` takes microseconds, clamps to PWM_SERVO_MIN..PWM_SERVO_MAX
- `servoDevInit()` configures PWM slices with `pwm_set_clkdiv()`, `pwm_set_wrap()`
- Pin assigned via `gpio_set_function(pin, GPIO_FUNC_PWM)`

**INAV translation:** Very clean implementation. INAV's servo output needs similar per-pin PWM slice assignment.

### 8. `pwm_motor_pico.c` — PWM Motor Output (Non-DShot)

**Key patterns:**
- Supports Oneshot125, Oneshot42, Multishot, Brushed, standard PWM
- Same hardware PWM slices as servos
- `pulseScale`/`pulseOffset` mapping from 0-1000 range to PWM duty counts
- Motor reordering support via `motorOutputReordering[]`
- Continuous update mode for brushed/PWM protocols

**INAV translation:** INAV supports these protocols too. The hardware PWM approach maps directly.

### 9. `adc_pico.c` — ADC with DMA

**Key patterns:**
- Round-robin ADC with DMA into ring buffer
- RP2350A: ADC channels on pins 26-29, RP2350B: pins 40-47
- Internal temp sensor used as padding when 3 channels active (ring buffer needs power-of-2)
- DMA uses endless mode (`-1` transfer count) with ring buffer (`channel_config_set_ring()`)
- Very slow sample rate: `adc_set_clkdiv(65535)` — ~10 samples/sec per channel (battery monitoring doesn't need speed)
- `adcGetValue()` reads latest DMA-cached value from `adcValues[]` array

**INAV translation:** INAV's ADC is similar. The ring buffer DMA trick for power-of-2 sizing is important to replicate.

### 10. `config_flash.c` — Settings Storage

**Key patterns:**
- Flash config stored in dedicated FLASH_CONFIG region (64KB at end of flash)
- `configWriteWord()` erases sector on 4KB boundary, programs in 256-byte pages
- Uses `save_and_disable_interrupts()` / `restore_interrupts()` around flash ops
- **TODO noted:** Should use `flash_safe_execute()` for multicore safety
- Linker script defines `__config_start` and `__config_end` symbols

**INAV translation:** INAV's config streamer would need similar flash region. The sector erase + page program pattern is identical to INAV's STM32 flash config.

### 11. `exti_pico.c` — External Interrupts (Gyro Data Ready)

**Key patterns:**
- Single shared GPIO IRQ handler dispatches to per-pin callbacks
- `gpio_set_irq_callback()` + `irq_set_enabled(IO_IRQ_BANK0, true)`
- Edge trigger: RISING, FALLING, or BOTH
- Per-pin callback table indexed by GPIO number
- Used for gyro EXTI (data-ready interrupt for high-rate sampling)

**INAV translation:** INAV uses EXTI for gyro data-ready. This pattern maps directly.

### 12. `serial_usb_vcp_pico.c` — USB Virtual COM Port

**Key patterns:**
- Thin wrapper over `cdc_usb_*()` functions from `usb/usb_cdc.c`
- TinyUSB provides CDC backend
- VCP vtable: `serialWrite`, `serialRead`, `serialTotalRxWaiting`, etc.
- Buffered write with flush on buffer full or `endWrite()`
- `usbVcpInit()` calls `cdc_usb_init()` on core 0

**INAV translation:** INAV's VCP is similar. Need TinyUSB CDC integration. The vtable pattern is common to both projects.

### 13. `multicore.c` — Dual-Core Support

**Key patterns:**
- Core 1 runs message loop: receives `core_message_t` with command + function pointer
- Commands: `MULTICORE_CMD_FUNC` (fire-and-forget), `MULTICORE_CMD_FUNC_BLOCKING` (waits for completion), `MULTICORE_CMD_STOP`
- Queues: `core1_queue` (core0→core1, size 4) and `core0_queue` (core1→core0, size 1)
- `tight_loop_contents()` in idle loop
- **TODO noted:** "call scheduler here for core 1 tasks" — not yet implemented
- Currently used for: DMA IRQ routing to core 1, some flash operations

**INAV translation:** INAV could use core 1 for OSD rendering, blackbox writes, or secondary sensor polling. The message queue pattern is clean.

### 14. `light_ws2811strip_pico.c` — LED Strip

**Key patterns:**
- Inline PIO program (4 instructions) for WS2812 timing
- Uses PIO block 2 (`PIO_LEDSTRIP_INDEX=2`)
- DMA transfer from `led_data[]` buffer to PIO TX FIFO
- Supports GRB, RGB, GRBW color formats
- Reset guard: 50us minimum between transfers
- DMA completion interrupt sets `ws2811LedDataTransferInProgress = false`

**INAV translation:** INAV's LED strip driver would use identical PIO program and DMA pattern.

### 15. `persistent.c` — Persistent Data Across Resets

**Key patterns:**
- Uses `.uninitialized_data.persistent` linker section (survives soft reset, not power loss)
- Magic value validation on read
- Replaces STM32's RTC backup registers

**INAV translation:** INAV uses persistent storage for bootloader requests, reset reasons. Same `.noinit` section approach works.

### 16. Linker Script (`pico_rp2350_RunFromFLASH.ld`)

**Key layout:**
```
FLASH:        0x10000000, 4032K  (code + read-only data)
FLASH_CONFIG: 0x103F0000, 64K   (settings storage)
RAM:          0x20000000, 512K   (data, BSS, heap)
SCRATCH_X:    0x20080000, 4K    (core 1 stack)
SCRATCH_Y:    0x20081000, 4K    (core 0 stack)
```

- Time-critical code and libgcc/libm go to RAM (via `> RAM AT> FLASH`)
- `.pg_registry` and `.pg_resetdata` sections for BF's parameter group system
- Stack: 4KB per core in scratch RAM
- Boot2 section limited to 256 bytes

**INAV translation:** INAV needs similar layout but with INAV's own config/EEPROM region. The `__config_start`/`__config_end` pattern matches INAV's config streamer.

---

## Build System (`RP2350.mk`)

### Compiler Flags
```
ARCH_FLAGS = -mthumb -mcpu=cortex-m33 -march=armv8-m.main+fp+dsp -mcmse -mfloat-abi=softfp
             -fno-builtin-memcpy   # Workaround for unaligned ldmia
             -DPICO_COPY_TO_RAM=$(RUN_FROM_RAM)
```

### Pico SDK Sources (60+ files)
- `rp2_common/` — Hardware drivers (GPIO, UART, SPI, I2C, DMA, PIO, ADC, flash, etc.)
- `common/` — Sync primitives, time, utilities
- `rp2350/` — Platform-specific code
- TinyUSB sources for USB CDC/MSC

### Math Optimization (Linker Wraps)
- **pico_float:** 37 wrapped functions (sinf, cosf, atan2f, sqrtf, etc.) using RP2350's hardware DCP
- **pico_double:** 50 wrapped functions (double-precision variants)
- **pico_stdio:** printf/snprintf/puts wraps
- **pico_bit_ops:** `__ctzdi2` wrap
- All pico-sdk library objects compiled with `-O2 -ffast-math -fmerge-all-constants` (no LTO to avoid wrap interaction)

### Include Paths
~75 include directories from Pico SDK covering all hardware modules.

---

## PIO Resource Allocation

| PIO Block | Usage | State Machines |
|-----------|-------|----------------|
| PIO 0 | DShot motors | Up to 4 SMs (1 per motor) |
| PIO 1 | Software UARTs | 2 SMs for TX, 2 SMs for RX (PIOUART0 + PIOUART1) |
| PIO 2 | LED strip | 1 SM |

RP2350 has 3 PIO blocks with 4 SMs each = 12 total SMs.

---

## Feature Enables/Disables (target.h)

### Enabled
- USE_MULTICORE, USE_UART0/1, USE_PIOUART0/1, USE_SPI (2 devices), USE_I2C (2 devices)
- USE_ADC, USE_VCP, USE_USB_MSC, USE_DSHOT_TELEMETRY
- CONFIG_IN_FLASH (flash-based config storage)

### Explicitly Disabled (undef)
- USE_SOFTSERIAL, USE_TRANSPONDER, USE_TIMER, USE_RCC
- USE_RX_SPI, USE_RX_PWM, USE_RX_PPM (no legacy RX protocols)
- Most serial RX protocols except CRSF (SBUS, IBUS, SPEKTRUM, etc.)
- USE_DSHOT_BITBANG (PIO replaces this)
- USE_MAG, USE_SERIAL_PASSTHROUGH, USE_MSP_UART, USE_VTX_*
- USE_OSD_HD (no HD OSD yet)

**Note for INAV:** INAV needs many of these features (MAG, SBUS, GPS, OSD). The BF target disables them because they weren't tested yet, not because they can't work. INAV should enable more features as the port progresses.

---

## Key Gotchas Confirmed in Source Code

| Issue | Where in Code | Solution |
|-------|---------------|----------|
| `gpio_init()` resets output | `io_pico.c:145-149` | Only call when `GPIO_FUNC_NULL` |
| DMA IRQ edge-triggered | `dma_pico.c:68-71` | Acknowledge BEFORE callback |
| MISO float on SD card | `bus_spi_pico.c:228` | `gpio_set_pulls(miso, true, false)` |
| memcpy alignment | `RP2350.mk:378` | `-fno-builtin-memcpy` |
| Flash write blocks | `config_flash.c:55-56` | `save_and_disable_interrupts()` |
| I2C FIFO race | `bus_i2c_pico.c:468` | `rx_tl = FIFO_DEPTH - 2` |
| PIO pin range limit | `dshot_pico.c:294-302` | Set `pio_set_gpio_base()` for pins 16-47 |
| Config not multicore safe | `config_flash.c:50` | TODO: use `flash_safe_execute()` |

---

## Lines of Code Summary

| File | LOC | Complexity |
|------|-----|------------|
| system.c | 270 | Low — mostly SDK wrappers |
| io_pico.c | 198 | Low — flat pin array |
| bus_spi_pico.c | 518 | Medium — DMA + clock divider math |
| bus_i2c_pico.c | 489 | High — interrupt state machine |
| dma_pico.c | 155 | Medium — per-core IRQ routing |
| dshot_pico.c | 393 | High — PIO + telemetry decode |
| dshot_bidir_pico.c | ~300 | High — GCR decode, timing |
| adc_pico.c | 270 | Medium — ring buffer DMA trick |
| config_flash.c | 72 | Low — sector erase + page write |
| serial_uart_pico.c | 137 | Low — dispatch layer |
| uart_hw.c | ~200 | Medium — hardware UART IRQs |
| uart_pio.c | 403 | High — PIO SM setup + IRQ |
| serial_usb_vcp_pico.c | 212 | Low — TinyUSB wrapper |
| exti_pico.c | 126 | Low — GPIO IRQ callback |
| light_ws2811strip_pico.c | 242 | Medium — PIO + DMA |
| pwm_motor_pico.c | 216 | Medium — multi-protocol PWM |
| pwm_servo_pico.c | 113 | Low — hardware PWM slices |
| multicore.c | 134 | Low — message queue |
| persistent.c | 71 | Low — noinit section |
| **Total platform code** | **~4500** | |

---

## Adaptation Strategy for INAV

### Files to Create (mapped from BF equivalents)

| INAV File | BF Equivalent | Notes |
|-----------|---------------|-------|
| `src/main/drivers/system_rp2350.c` | `PICO/system.c` | Nearly 1:1 |
| `src/main/drivers/io_rp2350.c` | `PICO/io_pico.c` | Adapt IO model |
| `src/main/drivers/bus_spi_rp2350.c` | `PICO/bus_spi_pico.c` | Adapt busDevice_t |
| `src/main/drivers/bus_i2c_rp2350.c` | `PICO/bus_i2c_pico.c` | Adapt i2cDevice_t |
| `src/main/drivers/dma_rp2350.c` | `PICO/dma_pico.c` | Adapt DMA identifiers |
| `src/main/drivers/serial_uart_rp2350.c` | `PICO/uart/*.c` | Adapt serial abstraction |
| `src/main/drivers/serial_usb_vcp_rp2350.c` | `PICO/serial_usb_vcp_pico.c` | Adapt VCP vtable |
| `src/main/drivers/pwm_output_rp2350.c` | `PICO/dshot_pico.c` + `pwm_motor_pico.c` | Motor output |
| `src/main/drivers/pwm_servo_rp2350.c` | `PICO/pwm_servo_pico.c` | Servo output |
| `src/main/drivers/adc_rp2350.c` | `PICO/adc_pico.c` | ADC ring buffer DMA |
| `src/main/drivers/flash_rp2350.c` | `PICO/config_flash.c` | Config storage |
| `src/main/drivers/exti_rp2350.c` | `PICO/exti_pico.c` | Gyro data-ready |
| `src/main/drivers/light_ws2811strip_rp2350.c` | `PICO/light_ws2811strip_pico.c` | LED strip |
| `src/main/drivers/persistent_rp2350.c` | `PICO/persistent.c` | Boot flags |
| `cmake/rp2350.cmake` | `PICO/mk/RP2350.mk` | Build system (CMake) |
| `src/main/target/RP2350_PICO/target.h` | `PICO/target/RP2350B/target.h` | Target config |
| `src/main/target/link/rp2350_flash.ld` | `PICO/link/pico_rp2350_RunFromFLASH.ld` | Memory layout |

### What Can Be Copied Almost Directly
- PIO assembly programs (`.pio` files)
- Linker script structure
- System timing (micros/millis/delay)
- GPIO operations
- EXTI implementation
- Persistent storage
- ADC ring buffer DMA

### What Needs Significant Adaptation
- SPI/I2C bus device model (INAV vs BF have different bus abstractions)
- Serial port abstraction (INAV's serialPort_t vs BF's)
- Motor/servo output wiring to INAV's mixer
- Config streamer adaptation for INAV's settings system
- Build system (CMake vs Make)
