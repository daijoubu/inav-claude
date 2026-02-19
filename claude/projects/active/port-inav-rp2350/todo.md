# Todo: Port INAV to RP2350 — 12 Milestones

> Each milestone is a separate developer assignment (subproject).
> Milestones are sequential — each builds on the previous one.
> Branch: `feature/rp2350-port` from `maintenance-9.x`
> BF reference: `betaflight/src/platform/PICO/` (~4500 LOC, ~30 files)

---

## Milestone 1: Build System & Empty Target (20-30 hrs) — ✅ COMPLETE

**Subproject:** `rp2350-m01-build-system`
**Completed:** 2026-02-16 | **Commit:** 4761ac2f51 | **Branch:** feature/rp2350-port
**Test:** `cmake` configures and `make RP2350_PICO` produces a .uf2 binary (does nothing useful yet)
**Hardware:** None (compile-only)
**BF reference:** `mk/RP2350.mk` (584 LOC), `target/RP2350B/target.h`, `link/pico_rp2350_RunFromFLASH.ld` (346 LOC)

### Pico SDK Integration
- [ ] Fetch Pico SDK (submodule at `lib/main/pico-sdk/` or external reference)
  - BF includes ~60 `.c`/`.S` SDK source files directly (not as a library)
  - ~75 include directories from SDK needed
  - SDK version: see `PICO/pico/version.h`
- [ ] Boot stage 2: either use BF's `bs2_default_padded_checksummed.S` or generate via SDK
  - Must be exactly 256 bytes (linker script reserves `.boot2` section)

### CMake Build Files
- [ ] Create `cmake/cortex-m33.cmake` — CPU arch flags
  - BF uses: `-mthumb -mcpu=cortex-m33 -march=armv8-m.main+fp+dsp -mcmse -mfloat-abi=softfp`
  - **Decision needed:** BF uses `softfp` ABI; consider `hard` for INAV (better FP performance, but must match all linked libs)
- [ ] Create `cmake/rp2350.cmake` — platform module with `target_rp2350()` function
  - [ ] Define RP2350_SRC (platform-specific driver stubs)
  - [ ] Define RP2350_DEFINITIONS: `PICO_RP2350`, `PICO_BOARD="pico2"`, `PICO_COPY_TO_RAM=0`
  - [ ] Define RP2350_INCLUDE_DIRS (~75 dirs from SDK, see `RP2350.mk:40-135`)
  - [ ] Compile options: `-fno-builtin-memcpy` (BF `RP2350.mk:378`, prevents unaligned `ldmia` crash)
  - [ ] SDK objects MUST use `-O2 -ffast-math -fmerge-all-constants` WITHOUT LTO (BF `RP2350.mk:580-583`)
  - [ ] Linker wraps: 37 pico_float + 50 pico_double + stdio + bit_ops (BF `RP2350.mk:136-252`)
    - These redirect math functions to RP2350's hardware DCP (Double Coprocessor)
  - [ ] UF2 output generation (elf2uf2 tool from Pico SDK, or python `uf2conv.py`)
  - [ ] Feature extraction macro (`get_rp2350_target_features`)
- [ ] Add `include(rp2350)` to root `CMakeLists.txt`

### Platform Header
- [ ] Add `#elif defined(RP2350)` block to `src/main/platform.h`
  - Type aliases needed (from BF `include/platform/platform.h`):
    - `SPI_TypeDef` → `SPI0_Type` (Pico SDK)
    - `I2C_TypeDef` → `i2c_inst_t`
    - `USART_TypeDef` → `uart_inst_t`
    - `GPIO_TypeDef` → `uint32_t` (single-port GPIO)
  - IO macros: `IO_CONFIG(mode, speed, pupd)` packing (BF packs into single byte)
  - `DEFIO_PORT_PINS` = 48 (RP2350B) or 30 (RP2350A)
  - `DEFIO_PORT_USED_COUNT` = 1 (single GPIO port, unlike STM32's GPIOA/B/C)
  - Task timing: `TASK_GYROPID_DESIRED_PERIOD 125` (8kHz, BF `platform.h:62`)

### Linker Script
- [ ] Create `src/main/target/link/rp2350_flash.ld`
  - Memory layout (from BF `pico_rp2350_RunFromFLASH.ld`):
    ```
    FLASH:        0x10000000, 4032K   (code + rodata)
    FLASH_CONFIG: 0x103F0000, 64K    (INAV settings storage)
    RAM:          0x20000000, 512K   (data + BSS + heap)
    SCRATCH_X:    0x20080000, 4K     (core 1 stack)
    SCRATCH_Y:    0x20081000, 4K     (core 0 stack)
    ```
  - Time-critical code → RAM (via `> RAM AT> FLASH`)
  - `.boot2` section (256 bytes) for boot stage 2
  - `__config_start`/`__config_end` symbols for INAV config streamer

### Startup Code
- [ ] Create `src/main/startup/startup_rp2350.s` — or use Pico SDK boot sequence
  - BF uses pre-compiled `bs2_default_padded_checksummed.S` for boot2
  - Vector table + Reset_Handler can follow standard Cortex-M33 pattern

### Target Directory
- [ ] Create `src/main/target/RP2350_PICO/` directory:
  - [ ] `target.h` — Board config (modeled on BF `target/RP2350B/target.h`)
    - Feature enables: USE_VCP, USE_SPI, USE_I2C, USE_ADC, USE_DSHOT
    - Feature disables: USE_SOFTSERIAL, USE_TRANSPONDER, USE_TIMER, USE_DSHOT_BITBANG
    - PIO allocation: `PIO_DSHOT_INDEX 0`, `PIO_UART_INDEX 1`, `PIO_LEDSTRIP_INDEX 2`
    - Pin assignments for Pico 2 board
  - [ ] `target.c` — System stubs (micros, millis, delay, systemReset — all returning 0 or no-op)
  - [ ] `config.c` — Empty default configuration
  - [ ] `CMakeLists.txt` — `target_rp2350(RP2350_PICO)`

### Stub Drivers
- [ ] Create stub driver files so COMMON_SRC compiles:
  - Stub or exclude files from COMMON_SRC that don't apply (study SITL's approach)
  - Key stubs needed: system, io, bus_spi, bus_i2c, dma, serial, adc, timer, exti, persistent

### Verification
- [ ] `cmake` configures without error
- [ ] `make RP2350_PICO` compiles and links to produce .uf2

---

## Milestone 2: System Tick, GPIO & LED Blink (15-20 hrs)

**Subproject:** `rp2350-m02-gpio-led`
**Test:** Flash .uf2 to Pico 2, onboard LED blinks at 1Hz
**Hardware:** Raspberry Pi Pico 2
**BF reference:** `system.c` (270 LOC), `io_pico.c` (198 LOC)

### System Timing (`system_rp2350.c`, replaces stubs from M1)
- [ ] `micros()` — use `time_us_32()` from Pico SDK (BF `system.c` pattern)
  - Hardware timer, NOT DWT cycle counter (DWT is separate for sub-microsecond)
- [ ] `millis()` — use `time_us_64() / 1000` (BF uses 64-bit to avoid rollover)
- [ ] `delay()` / `delayMicroseconds()` — SDK `sleep_ms()` / `sleep_us()` (BF pattern)
- [ ] `getCycleCounter()` — DWT CYCCNT via `m33_hw->dwt_cyccnt` (BF `system.c`)
  - Enable via `m33_hw->dwt_ctrl |= DWT_CTRL_CYCCNTENA_Msk` + `m33_hw->demcr |= CoreDebug_DEMCR_TRCENA_Msk`
  - Cortex-M33 has full DWT just like Cortex-M4 — this is standard ARM
- [ ] `SystemCoreClock` — populate via `clock_get_hz(clk_sys)` (BF `system.c`)
- [ ] `systemInit()` — clock init, call `stdio_init_all()` for SDK setup
- [ ] `systemReset()` — `watchdog_reboot(0, 0, 0)` (BF `system.c`)
  - If multicore active: reset core 1 first via `multicore_reset_core1()`
- [ ] `systemResetToBootloader()` — `rom_reset_usb_boot_extra(-1, 0, false)` for UF2 BOOTSEL mode
- [ ] `getUniqueId()` — `pico_get_unique_board_id()` maps 8-byte ID to 3x uint32_t (BF `system.c`)

### GPIO Abstraction (`io_rp2350.c`)
- [ ] `IOInitGlobal()` — assign pin numbers to `ioRec_t` array (BF `io_pico.c` uses flat array)
- [ ] `IOGetByTag()` — return `&ioRecs[pinIdx]` (no port lookup needed, single-port model)
- [ ] `IOHi()`, `IOLo()`, `IORead()`, `IOToggle()` — map to `gpio_put()`/`gpio_get()`
- [ ] `IOConfigGPIO()` — **CRITICAL:** Only call `gpio_init()` when function == `GPIO_FUNC_NULL`
  - BF `io_pico.c:145-149` — prevents resetting output levels on already-configured SPI CS pins
  - Use `gpio_get_function()` to check before calling `gpio_init()`
- [ ] Pullup/pulldown via `gpio_set_pulls()` (BF `io_pico.c`)
- [ ] `IO_CONFIG(mode, speed, pupd)` macro packs direction + slew rate + pull into one byte

### NVIC / Interrupts
- [ ] Cortex-M33 NVIC is standard ARM — `NVIC_EnableIRQ()`, `NVIC_SetPriority()`, etc.
  - Same API as STM32's Cortex-M4, just different IRQ numbers
- [ ] Include `hardware/irq.h` from Pico SDK for IRQ number definitions

### USB Debug Printf (Pico SDK stdio)
- [ ] Enable `pico_stdio_usb` in cmake build
- [ ] `stdio_init_all()` called in `systemInit()` (enables USB CDC stdio)
- [ ] `printf()` output visible over USB serial terminal
- [ ] Note: This is SDK-level stdio only — full INAV VCP abstraction is M3

### Scheduler & LED Blink
- [ ] INAV scheduler starts and runs LED blink task
- [ ] Pico 2 onboard LED is GPIO 25 — configure as output in target.h

### Verification
- [ ] LED blinks at 1Hz on real Pico 2 hardware
- [ ] Debug printf visible over USB serial (e.g. "INAV RP2350 booting...")

---

## Milestone 3: USB VCP & Debug Console (15-25 hrs)

**Subproject:** `rp2350-m03-usb-vcp`
**Test:** USB serial terminal shows INAV boot messages + debug output
**Hardware:** Raspberry Pi Pico 2
**BF reference:** `serial_usb_vcp_pico.c` (212 LOC), `usb/usb_cdc.c`, `usb/tusb_config.h`

### TinyUSB Integration
- [ ] Pico SDK provides TinyUSB — configure as CDC device
  - BF uses `usb/tusb_config.h` for configuration
  - CDC endpoints: EP1 IN/OUT for data, EP2 IN for notification
- [ ] USB descriptors (BF `usb/usb_descriptors.c`):
  - Vendor: "INAV", Product: "RP2350_PICO"
  - VID/PID: allocate for INAV or use generic CDC
- [ ] `cdc_usb_init()` must run on core 0 (BF `serial_usb_vcp_pico.c`)
- [ ] TinyUSB task polling: `tud_task()` called periodically from scheduler

### VCP Serial Port (`serial_usb_vcp_rp2350.c`)
- [ ] Implement INAV's `serialPort_t` vtable:
  - `usbVcpOpen()`, `usbVcpRead()`, `usbVcpWrite()`
  - `serialTotalRxWaiting()`, `serialTotalTxFree()`
- [ ] Buffered write with flush on buffer full or `endWrite()` (BF pattern)
- [ ] RX: TinyUSB CDC callback → INAV ring buffer

### MSP Protocol (Basic)
- [ ] MSP responds to version/board queries over USB VCP
- [ ] `printf`-style debug output works over USB serial
- [ ] Verify: connect USB, open serial terminal, see INAV boot messages

---

## Milestone 4: Configurator Connects (20-30 hrs)

**Subproject:** `rp2350-m04-configurator`
**Test:** INAV Configurator connects, shows board name + firmware version + sensor status
**Hardware:** Raspberry Pi Pico 2
**BF reference:** `config_flash.c` (72 LOC)

### Full MSP Protocol
- [ ] MSP_API_VERSION, MSP_FC_VARIANT, MSP_FC_VERSION
- [ ] MSP_BOARD_INFO (board identifier "RP2350_PICO"), MSP_BUILD_INFO
- [ ] MSP_STATUS, MSP_STATUS_EX (cycle time, sensor flags, arming flags)
- [ ] MSP_SENSOR_STATUS (all "not detected" is fine for M4)
- [ ] MSP_ACTIVEBOXES, MSP_BOXIDS, MSP_BOXNAMES

### Settings Storage (`flash_rp2350.c`)
- [ ] Config streamer using dedicated FLASH_CONFIG region (64KB at `0x103F0000`)
  - BF pattern: `flash_range_erase()` on 4KB sector boundary + `flash_range_program()` in 256-byte pages
  - **MUST** wrap in `save_and_disable_interrupts()` / `restore_interrupts()` (BF `config_flash.c:55-56`)
  - Linker symbols: `__config_start`, `__config_end`
- [ ] Option B (fallback): RAM-only config for initial bring-up (loses settings on reboot)
- [ ] `save` command writes config to flash
- [ ] **TODO for later:** multicore-safe flash writes via `flash_safe_execute()` (BF notes this too)

### CLI Interface
- [ ] CLI responds to: `status`, `version`, `set`, `save`, `defaults`, `reboot`
- [ ] Settings read/write working

### Verification
- [ ] INAV Configurator connects over USB, shows correct board name + firmware version

---

## Milestone 5: SPI & Gyro/Accelerometer Reading (25-35 hrs)

**Subproject:** `rp2350-m05-spi-gyro`
**Test:** Live gyro/accel data in configurator when board is tilted
**Hardware:** Pico 2 + ICM42688P or MPU6500 breakout (SPI)
**BF reference:** `bus_spi_pico.c` (518 LOC), `dma_pico.c` (155 LOC)

### SPI Driver (`bus_spi_rp2350.c`)
- [ ] Two SPI devices (SPI0, SPI1) — RP2350B has more pin options
- [ ] `spiInitDevice()`:
  - Call `spi_init()` from SDK
  - Set `gpio_set_function()` for MISO/MOSI/SCK
  - **Enable MISO pullup:** `gpio_set_pulls(miso, true, false)` (BF `bus_spi_pico.c:228`)
    - Prevents SD card MISO float on shared SPI bus
  - Set `gpio_set_slew_rate(sck, GPIO_SLEW_RATE_FAST)` for high-speed operation
- [ ] Blocking transfers:
  - `spi_write_read_blocking()`, `spi_write_blocking()`, `spi_read_blocking()` (0xff dummy TX)
- [ ] DMA transfers (for transfers >= 8 bytes, BF threshold):
  - TX + RX channels via `dma_claim_unused_channel()`
  - DREQ from `spi_get_dreq(spi, true/false)`
  - RX completion IRQ triggers CS negate + callback dispatch
- [ ] SPI clock: custom prescale+postdiv packing for `spi_set_baudrate()` (BF `bus_spi_pico.c`)
- [ ] CS pin management:
  - **CRITICAL:** Don't call `gpio_init()` on CS pin if already configured as SIO output
  - BF `io_pico.c:145-149` handles this in `IOConfigGPIO()`
- [ ] Format switching: `spi_set_format()` for CPOL/CPHA modes

### DMA Driver (`dma_rp2350.c`)
- [ ] 16 DMA channels on RP2350 (BF `dma_pico.c`)
- [ ] Dynamic allocation: `dma_claim_unused_channel(false)` for optional, `true` for required
- [ ] **CRITICAL:** Acknowledge IRQ BEFORE callback dispatch (BF `dma_pico.c:68-71`)
  - Edge-triggered IRQ — if you ack after callback, you miss events during callback
  - Pattern: `dma_channel_acknowledge_irq0(ch)` → then call `handler()`
- [ ] Per-core IRQ routing: DMA_IRQ_0 on core 0, DMA_IRQ_1 on core 1
- [ ] Handler table: indexed by channel number, stores callback function pointers

### IMU Integration
- [ ] Wire up ICM42688P or MPU6500 via SPI to Pico 2
- [ ] Gyro/accel detection and initialization working
- [ ] Gyro sampling at target rate (4-8kHz)
- [ ] EXTI for gyro data-ready (BF `exti_pico.c` pattern — GPIO edge IRQ)

### Verification
- [ ] CLI `status` shows gyro/accel readings
- [ ] Configurator shows live sensor data when board is tilted

---

## Milestone 6: UART, GPS & Receiver Input (25-35 hrs) — ✅ COMPLETE (serial drivers)

**Subproject:** `rp2350-m06-uart-gps-rx`
**Completed:** 2026-02-19 | **Commit:** f6e4f314a1 | **Branch:** feature/rp2350-port
**Test:** All 4 UARTs open and pass loopback (0x00/0xFF/ramp) verified on hardware via serialpassthrough
**Hardware:** Pico 2 + debugprobe; GP0/1 (UART1), GP2/3 (UART2), GP12/13 (UART3), GP14/15 (UART4)
**BF reference:** `uart/serial_uart_pico.c` (137 LOC), `uart/uart_hw.c` (~200 LOC), `uart/uart_pio.c` (403 LOC)

**Serial driver complete.** GPS parsing and SBUS/CRSF receiver decoding are protocol-layer work
that does not require additional RP2350 platform drivers — those work above the HAL once UARTs are open.

### Hardware UARTs (`serial_uart_rp2350.c`)
- [ ] UART0 + UART1 — interrupt-driven RX/TX
  - BF `uart/uart_hw.c` pattern: `uart_set_irqs_enabled()`, `uart_is_readable()`
  - Configurable baud rate, parity, stop bits
- [ ] Dispatch layer: routes to hw UART or PIO UART based on port type
  - BF `serial_uart_pico.c` has `serialUART_hw()` vs `serialUART_pio()` dispatch

### PIO Software UARTs
- [ ] PIOUART0 + PIOUART1 using PIO block 1 (`PIO_UART_INDEX=1`)
  - BF `uart/uart_pio.c` (403 LOC): one PIO block shared by 2 software UARTs
  - TX + RX programs loaded once, shared across both UARTs
  - Up to 4 SMs: 1 TX + 1 RX per UART
- [ ] GPIO base handling for pins 16-47: use `pio_set_gpio_base()` (same gotcha as DShot)
- [ ] Interrupt-driven: RX FIFO not-empty, TX FIFO not-full
  - BF uses `pio_sm_set_enabled()` to start/stop SMs
- [ ] PIO TX/RX programs: port from BF `uart_tx_program.c` / `uart_rx_program.c`
  - These are pre-compiled PIO assembly (generated from `.pio` files)

### Signal Inversion
- [ ] Hardware inversion via `gpio_set_inover()` for SBUS (no external inverter needed)
  - RP2350 can invert any GPIO input — huge advantage over STM32

### GPS + Receiver
- [ ] GPS module connects on UART and provides position data
- [ ] Receiver (SBUS/CRSF) connects and provides channel data
  - INAV needs SBUS support (unlike BF which disabled most RX protocols on RP2350)
- [ ] Telemetry output on a UART

### Verification
- [ ] GPS tab shows satellite fix + position
- [ ] Receiver tab shows stick movement

---

## Milestone 7: Motor Output — DShot via PIO (25-35 hrs)

**Subproject:** `rp2350-m07-dshot-motors`
**Test:** Motors spin on bench (props off!), DShot telemetry (ERPM) visible in CLI
**Hardware:** Pico 2 + sensors + GPS + receiver + ESCs + motors
**BF reference:** `dshot_pico.c` (393 LOC), `dshot_bidir_pico.c` (~300 LOC), `dshot.pio`

### DShot via PIO (`pwm_output_rp2350.c`)
- [ ] PIO block 0 (`PIO_DSHOT_INDEX=0`) — 1 state machine per motor, max 4 motors
- [ ] PIO programs:
  - `dshot_600_program` for unidirectional (BF `dshot.pio`)
  - `dshot_600_bidir_program` for bidirectional telemetry
  - Programs loaded once, shared across all motor SMs
- [ ] GPIO base handling: `pio_set_gpio_base()` for motor pins 16-47 (BF `dshot_pico.c:294-302`)
- [ ] Synchronized output:
  - `dshotUpdateComplete()`: Stop all SMs → load TX FIFOs → restart all simultaneously
  - BF `dshot_pico.c` pattern ensures all motors update at exactly the same time
- [ ] Pin pulldown when idle: `gpio_set_pulls(pin, false, true)` (BF pattern)
- [ ] DShot600 primary protocol (DShot150/300 can be added later)

### Bidirectional DShot Telemetry
- [ ] GCR decoding from PIO RX FIFO (BF `dshot_bidir_pico.c`)
- [ ] `dshotDecodeTelemetry()` reads PIO FIFO, GCR decode, CRC check
- [ ] `pwmGetMotorErpm()` returns decoded ERPM values

### Motor Interface
- [ ] Wire up INAV motor output functions:
  - `motorDevInit()`, `pwmWriteMotor()`, `pwmWriteDshotCommand()`
  - Motor protocol selection (DShot150/300/600)
- [ ] Motor reordering support (BF `pwm_motor_pico.c` has `motorOutputReordering[]`)

### Verification
- [ ] Motors spin from throttle stick (props off!)
- [ ] ERPM visible in CLI or configurator via bidirectional DShot

---

## Milestone 8: Servo PWM & ADC — Battery Monitoring (15-20 hrs)

**Subproject:** `rp2350-m08-servo-adc`
**Test:** Servos respond to sticks; configurator shows battery voltage
**Hardware:** Pico 2 + servos + voltage/current sensor
**BF reference:** `pwm_servo_pico.c` (113 LOC), `adc_pico.c` (270 LOC)

### Servo PWM (`pwm_servo_rp2350.c`)
- [ ] Hardware PWM slices — 8 slices x 2 channels = 16 possible outputs
  - NOT PIO — uses RP2350's built-in PWM peripheral
- [ ] 50Hz servo frequency: prescaler=64, TOP count ~39063 (BF `pwm_servo_pico.c`)
  - ~1.953 counts/us at 125MHz/64
- [ ] `servoDevInit()`: `pwm_set_clkdiv()`, `pwm_set_wrap()`, `gpio_set_function(pin, GPIO_FUNC_PWM)`
- [ ] `servoWrite()`: takes microseconds, clamps to PWM_SERVO_MIN..PWM_SERVO_MAX
- [ ] Standard 1000-2000us pulse width range

### Non-DShot Motor PWM (`pwm_motor_pico.c` equivalent)
- [ ] Same hardware PWM slices for: Oneshot125, Oneshot42, Multishot, Brushed, standard PWM
  - BF `pwm_motor_pico.c` (216 LOC): `pulseScale`/`pulseOffset` mapping from 0-1000 range
  - Continuous update mode for brushed/PWM protocols

### ADC Driver (`adc_rp2350.c`)
- [ ] Round-robin ADC with DMA ring buffer (BF `adc_pico.c` pattern)
  - RP2350A: ADC on pins 26-29; RP2350B: pins 40-47
- [ ] DMA endless mode: `-1` transfer count with `channel_config_set_ring()` for power-of-2 ring buffer
- [ ] **Power-of-2 trick:** If 3 channels, add internal temp sensor as 4th padding channel
  - Ring buffer must be power-of-2 for DMA ring mode (BF `adc_pico.c`)
- [ ] Very slow sample rate: `adc_set_clkdiv(65535)` — ~10 samples/sec (fine for battery monitoring)
- [ ] `adcGetValue()` reads latest DMA-cached value from `adcValues[]` array

### Verification
- [ ] Servos respond to stick input (test with oscilloscope or real servo)
- [ ] Battery voltage reads correctly in configurator

---

## Milestone 9: I2C Sensors — Baro + Mag (15-20 hrs)

**Subproject:** `rp2350-m09-i2c-sensors`
**Test:** Configurator shows barometer altitude + magnetometer heading updating live
**Hardware:** Pico 2 + IMU + BMP280/BMP388 (I2C) + QMC5883L (I2C)
**BF reference:** `bus_i2c_pico.c` (489 LOC)

### I2C Driver (`bus_i2c_rp2350.c`)
- [ ] **Interrupt-driven, NOT DMA** — 16-byte FIFO batching (BF `bus_i2c_pico.c`)
- [ ] Two I2C devices: I2C0, I2C1
  - Pin validation: I2C0 on pins where `pin % 4 == 0/1`, I2C1 where `pin % 4 == 2/3`
- [ ] State machine: `I2C_STATE_IDLE` → `I2C_STATE_ACTIVE` → `I2C_STATE_READ_DATA`
- [ ] Write: preload TX FIFO with register address + data bytes + STOP on last byte
- [ ] Read: single-batch if len <= 15 (FIFO - 1 for reg address byte)
  - Multi-batch with `I2C_IC_DATA_CMD_RESTART_BITS` for reads > 15 bytes
  - RX_FULL interrupt for multi-batch reads
- [ ] Interrupts: STOP_DET, TX_ABRT, TX_OVER, RX_OVER, RX_FULL
- [ ] Direct register manipulation: `hw->data_cmd`, `hw->tar`, `hw->enable`, `hw->intr_mask`
- [ ] **CRITICAL:** FIFO threshold `hw->rx_tl = I2C_FIFO_BUFFER_DEPTH - 2` (BF `bus_i2c_pico.c:468`)
  - Prevents race condition between reading FIFO and new data arriving
- [ ] Speed modes: standard 100kHz, fast 400kHz via `i2c_set_baudrate()`
- [ ] Non-blocking API: `i2cWriteBuffer()`/`i2cReadBuffer()` start transfer, `i2cBusy()` polls completion
- [ ] Timeout handling for stuck bus

### Sensor Integration
- [ ] Barometer: BMP280/BMP388/DPS310 over I2C
- [ ] Magnetometer: QMC5883L/HMC5883L/IST8310 over I2C
  - **Note:** BF disables MAG on RP2350 (`#undef USE_MAG`), but INAV needs it for navigation
- [ ] Sensor detection and initialization

### Verification
- [ ] Configurator shows barometer altitude updating (cover sensor → altitude rises)
- [ ] Configurator shows magnetometer heading updating (rotate board → heading changes)

---

## Milestone 10: Stabilized Flight — First Flight (30-40 hrs)

**Subproject:** `rp2350-m10-first-flight`
**Test:** Quad or fixed-wing flies stable in ACRO/ANGLE mode with manual control
**Hardware:** Complete aircraft with RP2350-based FC

### Integration & Tuning
- [ ] PID loop running at target rate (4kHz minimum, 8kHz if CPU allows)
  - BF targets 8kHz gyro rate: `TASK_GYROPID_DESIRED_PERIOD 125` (125us = 8kHz)
  - INAV may target 4kHz (250us) initially — RP2350 at 150MHz should handle it
- [ ] Gyro → PID → motor/servo output pipeline verified end-to-end
- [ ] Arming/disarming works (stick commands + arming checks)
- [ ] Flight modes: ACRO, ANGLE, HORIZON functional
- [ ] Failsafe triggers correctly on receiver loss

### Bench Testing
- [ ] Board self-levels when tilted (ANGLE mode) — motors respond correctly
- [ ] PID tuning for target airframe
- [ ] Verify timing: cycle time consistent, no jitter

### First Flight
- [ ] **First flight outdoors** — start with conservative PID values
- [ ] Verify: stable controlled flight in ACRO/ANGLE mode

**This is the MVP — core flight controller works on RP2350.**

---

## Milestone 11: Navigation — RTH, Position Hold, Waypoints (25-35 hrs)

**Subproject:** `rp2350-m11-navigation`
**Test:** Aircraft executes RTH, holds position, flies 3-waypoint mission
**Hardware:** Same as M10

### Navigation Stack (Platform-Agnostic)
- [ ] GPS position estimation working with baro fusion
  - INAV's navigation code is above the HAL layer — should "just work"
- [ ] Position hold (POSHOLD) stable
- [ ] Return to Home (RTH) works end-to-end
  - GPS home position saved on arm
  - RTH altitude, landing detection
- [ ] Waypoint mission executes correctly
  - 3-waypoint test mission with varying altitudes

### Verification
- [ ] RTH returns aircraft to home position
- [ ] 3-waypoint mission flown autonomously
- [ ] Flight log shows clean navigation transitions

**INAV's key differentiator vs Betaflight works on RP2350.**

---

## Milestone 12: Feature Complete — OSD, Blackbox, LEDs, Polish (40-60 hrs)

**Subproject:** `rp2350-m12-feature-complete`
**Test:** Full-featured flight: OSD overlay, blackbox downloadable, LED strip, full configurator
**Hardware:** Same as M10 + MAX7456 OSD + SPI flash + LED strip
**BF reference:** `light_ws2811strip_pico.c` (242 LOC), `multicore.c` (134 LOC), `usb/usb_msc_pico.c`

### OSD
- [ ] MAX7456 OSD over SPI — should "just work" once SPI driver is solid (M5)
- [ ] Optional: dual-core OSD offload to core 1
  - BF `multicore.c` provides message queue (core0→core1 size 4, core1→core0 size 1)
  - Commands: FUNC (fire-and-forget), FUNC_BLOCKING (waits)

### Blackbox
- [ ] Blackbox logging to SPI flash with DMA (non-blocking writes)
- [ ] SD card support with MISO pull-up (already handled in M5 SPI driver)
- [ ] USB MSC for blackbox download (TinyUSB CDC+MSC switching)
  - BF `usb/usb_msc_pico.c` implements mass storage class

### LED Strip (`light_ws2811strip_rp2350.c`)
- [ ] WS2812 via PIO block 2 (`PIO_LEDSTRIP_INDEX=2`) + DMA
  - 4-instruction PIO program (inline in BF `light_ws2811strip_pico.c`)
  - DMA transfer from `led_data[]` buffer to PIO TX FIFO
- [ ] Color formats: GRB, RGB, GRBW
- [ ] Reset guard: 50us minimum between transfers (BF pattern)
- [ ] DMA completion interrupt sets transfer-complete flag

### Beeper
- [ ] Beeper via hardware PWM (same slices as servo/motor but different frequency)

### Math Optimization
- [ ] Linker wraps for pico_float + pico_double (should be in place from M1)
  - These use RP2350's hardware DCP for float math — significant speedup
  - Verify math functions use hardware acceleration (not software emulation)

### Persistent Data (`persistent_rp2350.c`)
- [ ] `.uninitialized_data.persistent` linker section (survives soft reset)
  - Magic value validation on read (BF `persistent.c` pattern)
  - Replaces STM32's RTC backup registers
  - Used for bootloader requests, reset reasons, crash recovery

### Polish
- [ ] Full flight testing across all features
- [ ] Documentation: target setup guide, pin mapping, known limitations
- [ ] Performance profiling: CPU load, DMA utilization, loop time consistency

### Verification
- [ ] OSD video overlay visible
- [ ] Blackbox log downloadable via USB MSC
- [ ] LED strip patterns working
- [ ] Full configurator feature set functional

**Full INAV feature parity on RP2350. Ready for upstream PR.**

---

## Final: Upstream PR

- [ ] Submit RFC to INAV community (Discord / GitHub Discussions)
- [ ] Address community feedback
- [ ] Submit PR to `iNavFlight/inav` on `maintenance-9.x` (or `maintenance-10.x`)
- [ ] Iterate on review feedback
- [ ] Merge

---

## Verification Summary

| Milestones | Verification Method |
|------------|---------------------|
| M1 | Build output: cmake configures, make produces .uf2 |
| M2 | Hardware: LED blinks at 1Hz on Pico 2 |
| M3 | Hardware: USB serial shows INAV boot messages |
| M4 | Software: INAV Configurator connects, shows board info |
| M5-M6 | Hardware: Configurator shows live sensor/GPS/receiver data |
| M7-M8 | Hardware: Motors spin, servos move, battery voltage reads |
| M9 | Hardware: Baro altitude + mag heading updating live |
| M10 | Flight: Stable ACRO/ANGLE mode flight |
| M11 | Flight: RTH + 3-waypoint autonomous mission |
| M12 | Flight: OSD video, blackbox download, LED patterns, full feature check |
