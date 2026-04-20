# Project: Port INAV to RP2350 (Raspberry Pi Pico 2)

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Feature / Platform Port (Master Project — 12 Milestones)
**Created:** 2026-02-15
**Estimated Effort:** 300-400 hours (phased across 12 milestones)
**Branch:** `feature/rp2350-port` from `maintenance-9.x`

## Overview

Port INAV flight controller firmware to the RP2350 (Raspberry Pi Pico 2) chip. The RP2350's dual Cortex-M33 cores at 150MHz, 520KB SRAM, PIO state machines, and low cost make it a viable alternative to STM32. Betaflight has already completed a port (55 merged PRs, July-Nov 2025).

## Discussion

- [iNavFlight/inav#10401](https://github.com/iNavFlight/inav/discussions/10401)

## Key Insight: ~70% of INAV Code Unchanged

GPS parsing, receiver protocols, baro/mag drivers, navigation, PID, servo mixing, OSD are all above the HAL layer. Only platform-specific driver files need to be written.

## Approach: INAV-Pattern Platform Drivers

Create new `*_rp2350.c` driver files (like existing `*_stm32f4xx.c`, `*_at32f43x.c`), plus:
- `cmake/rp2350.cmake` with `target_rp2350()` function
- `src/main/target/RP2350_PICO/` target directory
- RP2350 linker script and startup code

## 12 Milestones — Each a Separate Subproject Assignment

| # | Milestone | Test Criteria | Est. Hours | Subproject |
|---|-----------|---------------|------------|------------|
| 1 | Build System & Empty Target | `make RP2350_PICO` produces .uf2 | 20-30 | `rp2350-m01-build-system` |
| 2 | System Tick, GPIO & LED Blink | LED blinks at 1Hz on Pico 2 | 15-20 | `rp2350-m02-gpio-led` |
| 3 | USB VCP & Debug Console | Serial terminal shows INAV boot messages | 15-25 | `rp2350-m03-usb-vcp` |
| 4 | Configurator Connects | INAV Configurator shows board name + firmware version | 20-30 | `rp2350-m04-configurator` |
| 5 | SPI & Gyro/Accel Reading | Live gyro data in configurator when tilted | 25-35 | `rp2350-m05-spi-gyro` |
| 6 | UART, GPS & Receiver | GPS tab shows fix, receiver tab shows stick input | 25-35 | `rp2350-m06-uart-gps-rx` |
| 7 | Motor Output (DShot via PIO) | Motors spin, DShot telemetry (ERPM) in CLI | 25-35 | `rp2350-m07-dshot-motors` |
| 8 | Servo PWM & ADC | Servos respond to sticks, battery voltage in configurator | 15-20 | `rp2350-m08-servo-adc` |
| 9 | I2C Sensors (Baro + Mag) | Baro altitude + mag heading updating live | 15-20 | `rp2350-m09-i2c-sensors` |
| 10 | Stabilized Flight (First Flight) | Stable ACRO/ANGLE mode flight | 30-40 | `rp2350-m10-first-flight` |
| 11 | Navigation (RTH, WP) | RTH + 3-waypoint mission autonomous | 25-35 | `rp2350-m11-navigation` |
| 12 | Feature Complete (OSD, BB, LEDs) | Full INAV feature parity on RP2350 | 40-60 | `rp2350-m12-feature-complete` |

**Total:** ~270-385 hours

## Betaflight Source Code Analysis (2026-02-15)

**Full analysis:** `betaflight-analysis.md` in this directory.

BF's RP2350 platform is ~4500 LOC across ~30 files in `betaflight/src/platform/PICO/`. Key architectural findings from reading the actual source:

### PIO Block Allocation
| PIO | Usage | SMs Used |
|-----|-------|----------|
| PIO 0 | DShot motors (1 SM/motor) | Up to 4 |
| PIO 1 | Software UARTs (PIOUART0/1) | Up to 4 |
| PIO 2 | WS2812 LED strip | 1 |

### Memory Layout (Linker Script)
```
FLASH:        0x10000000, 4032K   (code + rodata)
FLASH_CONFIG: 0x103F0000, 64K    (settings)
RAM:          0x20000000, 512K   (data + BSS + heap)
SCRATCH_X:    0x20080000, 4K     (core 1 stack)
SCRATCH_Y:    0x20081000, 4K     (core 0 stack)
```

### Compiler Flags
```
-mthumb -mcpu=cortex-m33 -march=armv8-m.main+fp+dsp -mcmse -mfloat-abi=softfp
-fno-builtin-memcpy  (alignment workaround)
```

### Files to Create (INAV equivalents of BF platform files)

| INAV File | BF Source | LOC | Complexity |
|-----------|-----------|-----|------------|
| `system_rp2350.c` | `system.c` | 270 | Low |
| `io_rp2350.c` | `io_pico.c` | 198 | Low |
| `bus_spi_rp2350.c` | `bus_spi_pico.c` | 518 | Medium |
| `bus_i2c_rp2350.c` | `bus_i2c_pico.c` | 489 | High |
| `dma_rp2350.c` | `dma_pico.c` | 155 | Medium |
| `serial_uart_rp2350.c` | `uart/*.c` | 740 | High |
| `serial_usb_vcp_rp2350.c` | `serial_usb_vcp_pico.c` | 212 | Low |
| `pwm_output_rp2350.c` | `dshot_pico.c`+`pwm_motor_pico.c` | 609 | High |
| `pwm_servo_rp2350.c` | `pwm_servo_pico.c` | 113 | Low |
| `adc_rp2350.c` | `adc_pico.c` | 270 | Medium |
| `flash_rp2350.c` | `config_flash.c` | 72 | Low |
| `exti_rp2350.c` | `exti_pico.c` | 126 | Low |
| `light_ws2811strip_rp2350.c` | `light_ws2811strip_pico.c` | 242 | Medium |
| `persistent_rp2350.c` | `persistent.c` | 71 | Low |
| `rp2350_flash.ld` | `pico_rp2350_RunFromFLASH.ld` | 346 | Medium |
| `cmake/rp2350.cmake` | `mk/RP2350.mk` | 584 | High |

## Known Gotchas (Confirmed in BF Source Code)

| Issue | Where in BF Source | Solution |
|-------|-------------------|----------|
| memcpy generates unaligned ldmia | `RP2350.mk:378` | `-fno-builtin-memcpy` compiler flag |
| gpio_init() resets output level | `io_pico.c:145-149` | Only call when `GPIO_FUNC_NULL`, not when already SIO |
| DMA IRQ edge-triggered | `dma_pico.c:68-71` | Acknowledge IRQ BEFORE callback dispatch |
| SD card MISO floats | `bus_spi_pico.c:228` | `gpio_set_pulls(miso, true, false)` |
| Flash write blocks all cores | `config_flash.c:55-56` | `save_and_disable_interrupts()`, TODO: `flash_safe_execute()` |
| I2C FIFO race condition | `bus_i2c_pico.c:468` | Set `rx_tl = FIFO_DEPTH - 2` |
| PIO pin range limited to 32 pins | `dshot_pico.c:294-302` | Use `pio_set_gpio_base()` for pins 16-47 |
| Pico SDK objects can't use LTO | `RP2350.mk:580-583` | Compile SDK with `-O2` not `-flto` |
| Math functions need wrapping | `RP2350.mk:136-252` | 87 linker wraps for pico_float + pico_double |

## Hardware Needed (Per Milestone)

- **M1-M4:** Raspberry Pi Pico 2 only (USB + LED)
- **M5:** + IMU breakout (ICM42688P or MPU6500, SPI)
- **M6:** + GPS module (u-blox M8N/M10) + RC receiver (ELRS/CRSF or SBUS) — UARTs testable with bare Pico 2 + serial adapter
- **M7:** + ESCs + motors (props off for bench testing) — DShot signal testable with oscilloscope/logic analyzer
- **M8:** + Servos + voltage/current sensor — PWM testable with bare Pico 2 + servo or oscilloscope
- **M9:** + Barometer (BMP280/BMP388, I2C) + Magnetometer (QMC5883L, I2C)
- **M10+:** Full flight hardware, custom PCB or carrier board

## Manager Notes

### Task Assignment — Include Milestone Reference File

When assigning each milestone to the developer, include the corresponding reference file from:

```
claude/projects/active/port-inav-rp2350/milestones/M<N>/reference.md
```

Full paths (M1–M12):
- M1: `claude/projects/active/port-inav-rp2350/milestones/M1/reference.md`
- M2: `claude/projects/active/port-inav-rp2350/milestones/M2/reference.md`
- M3: `claude/projects/active/port-inav-rp2350/milestones/M3/reference.md`
- M4: `claude/projects/active/port-inav-rp2350/milestones/M4/reference.md`
- M5: `claude/projects/active/port-inav-rp2350/milestones/M5/reference.md`
- M6: `claude/projects/active/port-inav-rp2350/milestones/M6/reference.md`
- M7: `claude/projects/active/port-inav-rp2350/milestones/M7/reference.md`
- M8: `claude/projects/active/port-inav-rp2350/milestones/M8/reference.md`
- M9: `claude/projects/active/port-inav-rp2350/milestones/M9/reference.md`
- M10: `claude/projects/active/port-inav-rp2350/milestones/M10/reference.md`
- M11: `claude/projects/active/port-inav-rp2350/milestones/M11/reference.md`
- M12: `claude/projects/active/port-inav-rp2350/milestones/M12/reference.md`

In the task assignment email, tell the developer: "Read `<path>` before starting this milestone."

## References

- **Port plan:** `/home/raymorris/Documents/planes/rpi_pico_2350_port/inav_rp2350_port_plan.md`
- **Detailed guide:** `/home/raymorris/Documents/planes/rpi_pico_2350_port/inav_rp2350_detailed.md`
- **BF PR list:** `/home/raymorris/Documents/planes/rpi_pico_2350_port/bf_prs.txt`
- **Accuracy analysis:** `/home/raymorris/Documents/planes/rpi_pico_2350_port/accuracy_analysis.md`
- **INAV CMake modules:** `inav/cmake/stm32.cmake`, `inav/cmake/at32.cmake`, `inav/cmake/sitl.cmake`
- **INAV driver pattern:** `inav/src/main/drivers/*_stm32f4xx.c`, `*_at32f43x.c`
- **INAV target example:** `inav/src/main/target/SITL/`, `inav/src/main/target/KAKUTEF4/`
- **BF RP2350 PRs:** https://github.com/betaflight/betaflight/pulls?q=label:RPI+is:closed
