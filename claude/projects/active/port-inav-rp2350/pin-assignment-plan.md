# RP2350 Pico 2 Pin Assignment Plan

> **Selected Option: C (Balanced All-Rounder)** — This is the option currently planned for implementation. See the [Comparison Summary](#comparison-summary) and [Recommendation](#recommendation) sections for details.

**Project:** Port INAV to RP2350 (Pico 2)
**Milestone:** M5–M8 preparation (SPI, I2C, ADC, motors)
**Date:** 2026-02-19
**Author:** Developer agent

---

## Background

The RP2350_PICO INAV target is in progress (M1 + M2 complete). The current `target.h` is a stub with no SPI, I2C, ADC, or motor outputs defined. This report documents three viable pin assignment options to guide M5–M8 implementation.

---

## Pico 2 GPIO Capability Summary

The Raspberry Pi Pico 2 (RP2350) provides 29 usable GPIO pins (GP0–GP28). Each pin supports multiple peripherals via the SIO multiplexer.

### ADC pins — fully fixed

Only three pins support analog input on RP2350:

| GP | ADC Channel | INAV Function |
|----|-------------|---------------|
| GP26 | ADC0 | VBAT |
| GP27 | ADC1 | CURRENT |
| GP28 | ADC2 | RSSI (or BEEPER when digital RSSI) |

These are fixed in all options.

### LED — fully fixed

| GP | Function | Reason |
|----|----------|--------|
| GP25 | LED0 | Onboard LED — hardwired to GP25 on Pico 2 PCB |

### Hardware UART pin families

| Bus | Valid TX/RX pin pairs |
|-----|----------------------|
| UART0 | GP0/1, GP4/5, GP8/9, GP12/13, GP16/17 |
| UART1 | GP2/3, GP6/7, GP10/11, GP14/15, GP18/19 |

**⚠️ Bug in current target.h**: UART2 is currently assigned to GP4/5, which maps to UART0 hardware — not UART1. The intended assignment should use GP2/3 (UART1 hardware). This must be corrected in M5 implementation.

### SPI buses

| Bus | MISO/CSn/SCK/MOSI | Notes |
|-----|-------------------|-------|
| SPI0 | GP4/5/6/7 | Clean group; preferred for gyro |
| SPI1 | GP8–11 or GP12–15 | GP24–27 blocked by LED/ADC |

**Resolution adopted in all options**: Share SPI0 for both gyro and flash using separate GPIO chip-select pins. This avoids the need to configure SPI1 and reduces bus complexity.

### I2C buses

| Bus | Valid SDA/SCL pairs |
|-----|---------------------|
| I2C0 | GP0/1, GP4/5, GP8/9, GP12/13, GP16/17, GP20/21 |
| I2C1 | GP2/3, GP6/7, GP10/11, GP14/15, GP18/19, GP22/23 |

### PIO blocks (RP2350 has 3 PIO blocks, 4 state machines each)

| PIO block | State machines | Planned use |
|-----------|----------------|-------------|
| PIO0 | SM0–SM3 | DShot motors (1 SM per motor) |
| PIO1 | SM0–SM3 | Software UARTs (UART3 + UART4, 2 SMs each) |
| PIO2 | SM0–SM3 | WS2812 LED strip (SM0); SMs 1–3 spare |

### PWM slices

Adjacent GP pairs share a PWM slice and must run at the same frequency:
- GP0/1 → slice 0, GP2/3 → slice 1, GP4/5 → slice 2, GP6/7 → slice 3
- GP8/9 → slice 4, GP10/11 → slice 5, GP12/13 → slice 6, GP14/15 → slice 7
- GP16/17 → slice 8, GP18/19 → slice 9, GP20/21 → slice 10
- GP22/23 → slice 11, GP24/25 → slice 12, GP26/27 → slice 13

---

## INAV Target Function Checklist

Surveyed from MATEKF405, MATEKF722, and SPEEDYBEEF7 targets:

| Function | Typical count | Notes |
|----------|--------------|-------|
| Motor outputs | 4–8 | DShot preferred; all surveyed targets use USE_DSHOT |
| Servo outputs | 4–6 | PWM; often dual-use with UART pins |
| Hardware UARTs | 5–6 + VCP | GPS, receiver, telemetry, MSP, ESC sensor |
| SPI buses | 2–3 | Gyro (SPI1 on STM32 → SPI0 on RP2350), OSD, flash |
| I2C buses | 1–2 | Baro + mag on I2C1; external I2C2 on better boards |
| ADC channels | 3 | VBAT, current, RSSI — universal |
| LED strip | 1 pin | WS2811/2812; timer+DMA on STM32 → PIO2 on Pico |
| Beeper | 1 pin | Active buzzer; often INVERTED flag |
| Gyro INT/EXTI | 1 pin | Data-ready interrupt; polling acceptable |
| LED0/LED1 | 1–2 pins | Status LEDs |

**Note on OSD**: Pico 2 has no analog video path. `USE_MSP_OSD` already present in target.h is correct — MSP OSD is delivered over a UART to an external OSD chip.

---

## Option A — Multirotor Focus (8 DShot motors, 3 serial ports)

**Trade-off**: PIO1 repurposed from software UARTs to DShot motors 5–8. Loses UART3/UART4. Only 2 hardware UARTs + VCP = 3 serial ports total.

| GP | INAV Pin | Function | Hardware | Notes |
|----|----------|----------|----------|-------|
| GP0 | PA0 | UART1 TX | UART0 TX | MSP / configurator |
| GP1 | PA1 | UART1 RX | UART0 RX | |
| GP2 | PA2 | UART2 TX | UART1 TX | GPS or receiver |
| GP3 | PA3 | UART2 RX | UART1 RX | HW inversion-free → SBUS without inverter |
| GP4 | PA4 | SPI0 MISO | SPI0 RX | Gyro + flash shared bus |
| GP5 | PA5 | GYRO CS | SPI0 CSn | Gyro chip select |
| GP6 | PA6 | SPI0 SCK | SPI0 SCK | |
| GP7 | PA7 | SPI0 MOSI | SPI0 TX | |
| GP8 | PA8 | MOTOR1 | PIO0 SM0 | DShot 300/600 |
| GP9 | PA9 | MOTOR2 | PIO0 SM1 | DShot |
| GP10 | PA10 | MOTOR3 | PIO0 SM2 | DShot |
| GP11 | PA11 | MOTOR4 | PIO0 SM3 | DShot |
| GP12 | PA12 | MOTOR5 | PIO1 SM0 | DShot (PIO1 repurposed) |
| GP13 | PA13 | MOTOR6 | PIO1 SM1 | DShot |
| GP14 | PA14 | MOTOR7 | PIO1 SM2 | DShot |
| GP15 | PA15 | MOTOR8 | PIO1 SM3 | DShot |
| GP16 | PB0 | I2C0 SDA | I2C0 | Baro + mag |
| GP17 | PB1 | I2C0 SCL | I2C0 | |
| GP18 | PB2 | I2C1 SDA | I2C1 | External sensors (pitot, rangefinder) |
| GP19 | PB3 | I2C1 SCL | I2C1 | |
| GP20 | PB4 | FLASH CS | GPIO | SPI flash CS (shares SPI0 bus) |
| GP21 | PB5 | GYRO INT | GPIO (EXTI) | IMU data-ready interrupt |
| GP22 | PB6 | LED STRIP | PIO2 SM0 | WS2812 |
| GP23 | PB7 | BEEPER | GPIO | Active buzzer |
| GP24 | PB8 | LED1 | GPIO | Second status LED |
| GP25 | PB9 | LED0 | GPIO | Onboard (fixed) |
| GP26 | PB10 | VBAT | ADC0 | Battery voltage |
| GP27 | PB11 | CURRENT | ADC1 | Current sensor |
| GP28 | PB12 | RSSI | ADC2 | Analog RSSI input |

**Rationale**: Designed for racing quads and hexacopters. All 8 DShot outputs use clean PIO with no PWM slice sharing issues. Full dual I2C bus (rare for a Pico target). Shared SPI for both gyro and blackbox flash. Only 3 total serial ports — GPS + receiver must share the 2 hardware ports, acceptable for single-function racing builds. No driver changes required beyond the existing PIO DShot implementation.

---

## Option B — Long-Range / Telemetry Focus (4 DShot motors, 6 serial ports)

**Trade-off**: UART5 placed on PIO2 SMs 1–2 alongside LED strip on SM0. No dedicated servo PWM outputs (dual-use GP12–15 available). No second I2C.

| GP | INAV Pin | Function | Hardware | Notes |
|----|----------|----------|----------|-------|
| GP0 | PA0 | UART1 TX | UART0 TX | MSP / configurator |
| GP1 | PA1 | UART1 RX | UART0 RX | |
| GP2 | PA2 | UART2 TX | UART1 TX | GPS primary |
| GP3 | PA3 | UART2 RX | UART1 RX | HW inversion-free → SBUS without inverter |
| GP4 | PA4 | SPI0 MISO | SPI0 RX | Gyro + flash shared bus |
| GP5 | PA5 | GYRO CS | SPI0 CSn | |
| GP6 | PA6 | SPI0 SCK | SPI0 SCK | |
| GP7 | PA7 | SPI0 MOSI | SPI0 TX | |
| GP8 | PA8 | MOTOR1 | PIO0 SM0 | DShot |
| GP9 | PA9 | MOTOR2 | PIO0 SM1 | DShot |
| GP10 | PA10 | MOTOR3 | PIO0 SM2 | DShot |
| GP11 | PA11 | MOTOR4 | PIO0 SM3 | DShot |
| GP12 | PA12 | UART3 TX | PIO1 SM0 | Receiver (CRSF/SBUS) — dual-use: SERVO3 (PWM 6A) |
| GP13 | PA13 | UART3 RX | PIO1 SM1 | HW inversion-free → SBUS — dual-use: SERVO4 (PWM 6B) |
| GP14 | PA14 | UART4 TX | PIO1 SM2 | Telemetry (FrSky/LTM/MAVLink) — dual-use: SERVO5 (PWM 7A) |
| GP15 | PA15 | UART4 RX | PIO1 SM3 | — dual-use: SERVO6 (PWM 7B) |
| GP16 | PB0 | UART5 TX | PIO2 SM1 | Extra port (ESC telemetry / MSP OSD) |
| GP17 | PB1 | UART5 RX | PIO2 SM2 | ⚠️ Requires UART5 on PIO2 driver extension |
| GP18 | PB2 | I2C1 SDA | I2C1 | Baro + mag |
| GP19 | PB3 | I2C1 SCL | I2C1 | |
| GP20 | PB4 | FLASH CS | GPIO | SPI flash CS |
| GP21 | PB5 | BEEPER | GPIO | Active buzzer |
| GP22 | PB6 | LED STRIP | PIO2 SM0 | WS2812 |
| GP23 | PB7 | GYRO INT | GPIO (EXTI) | Data-ready interrupt |
| GP24 | PB8 | LED1 | GPIO | Optional second status LED |
| GP25 | PB9 | LED0 | GPIO | Onboard (fixed) |
| GP26 | PB10 | VBAT | ADC0 | |
| GP27 | PB11 | CURRENT | ADC1 | |
| GP28 | PB12 | RSSI / BEEPER | ADC2 / GPIO | Dual-use: ADC when analog RSSI used |

**Dual-use pins (NEXUSX pattern)**:

| GP | Primary | Alternate | Condition |
|----|---------|-----------|-----------|
| GP12/13 | UART3 TX/RX | SERVO3/4 (PWM 6A/6B) | When UART3 unassigned in ports tab |
| GP14/15 | UART4 TX/RX | SERVO5/6 (PWM 7A/7B) | When UART4 unassigned |
| GP28 | RSSI ADC | BEEPER | When using digital RSSI (CRSF) |

**Rationale**: Long-range fixed-wing or rover/boat deployments requiring CRSF receiver + FrSky telemetry + GPS + MSP + ESC telemetry + spare port. Six serial ports covers all combinations. Suitable for MAVLink ground station telemetry, multiple GPS redundancy, or DJI FPV OSD alongside GPS.

**⚠️ Driver note**: UART5 on PIO2 requires extending the software UART driver beyond the current PIO1-only implementation. PIO2 SM0 is already used for LED strip; SMs 1–2 are available but require driver changes.

---

## Option C — Balanced All-Rounder ✅ RECOMMENDED

**Trade-off**: Best balance between quad (4 DShot motors) and fixed-wing (dedicated + dual-use servo outputs). Five serial ports covers typical deployment. No additional driver changes beyond existing PIO UART implementation.

| GP | INAV Pin | Function | Hardware | Notes |
|----|----------|----------|----------|-------|
| GP0 | PA0 | UART1 TX | UART0 TX | MSP / configurator |
| GP1 | PA1 | UART1 RX | UART0 RX | |
| GP2 | PA2 | UART2 TX | UART1 TX | Receiver (CRSF/SBUS) |
| GP3 | PA3 | UART2 RX | UART1 RX | HW inversion-free → SBUS without inverter |
| GP4 | PA4 | SPI0 MISO | SPI0 RX | Gyro + flash shared bus |
| GP5 | PA5 | GYRO CS | SPI0 CSn | Gyro chip select |
| GP6 | PA6 | SPI0 SCK | SPI0 SCK | |
| GP7 | PA7 | SPI0 MOSI | SPI0 TX | |
| GP8 | PA8 | MOTOR1 | PIO0 SM0 | DShot 300/600 |
| GP9 | PA9 | MOTOR2 | PIO0 SM1 | DShot |
| GP10 | PA10 | MOTOR3 | PIO0 SM2 | DShot |
| GP11 | PA11 | MOTOR4 | PIO0 SM3 | DShot |
| GP12 | PA12 | UART3 TX | PIO1 SM0 | GPS — dual-use: SERVO3 (PWM 6A) |
| GP13 | PA13 | UART3 RX | PIO1 SM1 | — dual-use: SERVO4 (PWM 6B) |
| GP14 | PA14 | UART4 TX | PIO1 SM2 | Telemetry/extra — dual-use: SERVO5 (PWM 7A) |
| GP15 | PA15 | UART4 RX | PIO1 SM3 | — dual-use: SERVO6 (PWM 7B) |
| GP16 | PB0 | FLASH CS | GPIO | SPI flash CS (blackbox on SPI0 bus) |
| GP17 | PB1 | BEEPER | GPIO | Active buzzer |
| GP18 | PB2 | I2C1 SDA | I2C1 | Baro + mag |
| GP19 | PB3 | I2C1 SCL | I2C1 | |
| GP20 | PB4 | SERVO1 | PWM slice 10A | Fixed-wing aileron or elevator |
| GP21 | PB5 | SERVO2 | PWM slice 10B | Shares slice 10 with GP20 — same freq OK for servos |
| GP22 | PB6 | LED STRIP | PIO2 SM0 | WS2812 |
| GP23 | PB7 | GYRO INT | GPIO (EXTI) | IMU data-ready interrupt |
| GP24 | PB8 | LED1 | GPIO | Second status LED |
| GP25 | PB9 | LED0 | GPIO | Onboard (fixed) |
| GP26 | PB10 | VBAT | ADC0 | Battery voltage |
| GP27 | PB11 | CURRENT | ADC1 | Current sensor |
| GP28 | PB12 | RSSI / BEEPER | ADC2 / GPIO | Dual-use |

**Dual-use pins (NEXUSX pattern)**:

| GP | Primary | Alternate | Condition |
|----|---------|-----------|-----------|
| GP12/13 | UART3 TX/RX | SERVO3/4 (PWM 6A/6B) | When UART3 unassigned in ports tab |
| GP14/15 | UART4 TX/RX | SERVO5/6 (PWM 7A/7B) | When UART4 unassigned |
| GP28 | RSSI ADC | BEEPER | When using digital RSSI (CRSF) |

**Rationale**: Serves quadcopters (4 DShot motors, UART3/4 for GPS + telemetry) and fixed-wing aircraft (SERVO1–6 via GP20/21 and UART3/4 dual-use) equally well. Two GP20/21 servo outputs are always available regardless of UART assignments. Four additional servo outputs become available when UARTs 3/4 are not needed. Full sensor coverage with I2C1 for baro + mag, shared SPI0 for gyro + blackbox. Requires no driver changes beyond what M1–M2 already deliver.

---

## Comparison Summary

| Feature | Option A: Max Motors | Option B: Max UARTs | Option C: Balanced ✅ |
|---------|---------------------|--------------------|-----------------------|
| DShot motor outputs | **8** | 4 | 4 |
| Dedicated servo/PWM outputs | 0 | 0 | **2** |
| Total servo outputs (incl dual-use) | 0 | 4 | **6** |
| Serial ports (incl VCP) | 3 | **6** | 5 |
| Hardware UARTs | 2 | 2 | 2 |
| PIO UARTs | 0 | **3** | 2 |
| SPI buses used | 1 (shared) | 1 (shared) | 1 (shared) |
| I2C buses | **2** | 1 | 1 |
| ADC channels | 3 | 3 | 3 |
| LED strip | Yes | Yes | Yes |
| Beeper | Yes | Yes | Yes |
| Gyro INT | Yes | Yes | Yes |
| Driver changes needed | None | PIO2 UART extension | **None** |
| Best use case | 8-motor racing/hex | Long-range telemetry | **General purpose** |

---

## Recommendation

**Option C (Balanced All-Rounder)** is recommended for the RP2350_PICO INAV target.

Reasons:
1. **Widest use case coverage** — works as a quad test platform (4 DShot) and a fixed-wing platform (6 servo outputs via GP20/21 + dual-use).
2. **No driver changes required** — PIO0 for DShot, PIO1 for UART3/4 software serial, PIO2 SM0 for LED strip. All within the existing driver model from M1–M2.
3. **Five serial ports** — adequate for GPS + receiver + telemetry + MSP + spare. The most common INAV fixed-wing scenario is 4 ports.
4. **NEXUSX-proven dual-use pattern** — the UART↔servo dual-use mechanism is already tested in the NEXUSX target and works cleanly in INAV configurator.
5. **Clean SPI layout** — GP4–7 as SPI0 with GPIO chip selects on GP5 (gyro) and GP16 (flash) avoids any SPI1 complexity.

Option A is better for dedicated racing quad development if >4 motors are needed. Option B is better for fixed-wing long-range with many peripherals. For a general-purpose Pico 2 target, Option C is the right starting point.

---

## Second Core (Core 1) for DShot / UART — Feasibility Analysis

The RP2350 has two Cortex-M33 cores. This section evaluates whether core 1 could serve as an alternative or supplement to PIO state machines for driving DShot motor protocol and software UARTs — analogously to how dedicated UART hardware works on STM32.

### Short answer: No for DShot and high-speed UART; PIO is the right tool.

### Timing Precision

At 192 MHz the RP2350 core has a 5.21 ns cycle time. DShot600 needs a 1.67 µs bit period (320 cycles). A tight bit-bang loop on core 1 requires roughly 520 cycles per bit including GPIO writes and delay polling — already over budget before any interrupt or cache miss. PIO handles DShot600 in exactly 40 cycles per bit (using delay suffixes in the PIO instruction set) with ±5 ns jitter. Core 1 bit-banging produces ±20–100 ns jitter, exceeding the ESC frame acceptance tolerance by 20–100×.

For UART, 100 kbps (SBUS) is feasible on core 1 (1920 cycles per bit, very loose), and CRSF at 420 kbps is marginal. At 3.75 Mbps (ESC telemetry high-speed), there are only ~51 cycles per bit — a single L1 cache miss (~40 cycles) causes frame loss, making it unreliable.

| Protocol | Bit period | Core 1 verdict | PIO verdict |
|----------|-----------|----------------|-------------|
| DShot300 | 3.33 µs | Marginal, no synchrony | ✓ |
| **DShot600** | **1.67 µs** | **✗ Not feasible** | **✓** |
| UART 100 kbps (SBUS) | 10 µs | ✓ Feasible | ✓ |
| UART 420 kbps (CRSF) | 2.38 µs | Marginal, fragile | ✓ |
| UART 3.75 Mbps | 267 ns | ✗ Not feasible | ✓ |

### Synchronization of Multiple Motors

PIO allows all four motors to start their DShot frame simultaneously via a single `pio_set_sm_mask_enabled()` call — hardware-atomic, zero skew. Core 1 has no equivalent: it can only drive one GPIO bit-stream at a time, so a 4-motor DShot driver would require 4 separate core-1 loops (impossible with one core) or serialized per-motor passes (introduces inter-motor timing skew, defeating DShot's synchronization requirement).

### Inter-Core Communication Overhead

Sending a motor command from core 0 to core 1 via the hardware FIFO (mailbox) costs approximately 170–220 cycles (~1 µs). For a DShot frame of ~26.7 µs this is a 3–4% overhead and acceptable in isolation, but it means core 1 must then still bit-bang the timing-critical part, which it cannot do reliably for DShot600.

For UART RX at 420 kbps, the mailbox latency (~1 µs) is already larger than a single bit period (2.38 µs), making this path unworkable for interrupt-driven character forwarding.

### INAV Scheduler Compatibility

INAV uses a single-threaded cooperative scheduler with no thread-safe queues, spinlocks, or mutexes in the firmware. Core 1 would need either:
- **Fire-and-forget message queue** (requires Betaflight-style multicore API not yet in INAV)
- **Spinlock-protected shared state** (requires adding synchronization primitives)
- **Fully independent loop** (no shared state — limits usefulness)

Betaflight's RP2350 port has a `core1_main()` with a `// TODO: call scheduler here` comment — confirming that even Betaflight has not solved the scheduler integration question. Betaflight currently uses core 1 only for flash writes and one-off DMA IRQ handling, not for continuous I/O drivers.

### What Core 1 Is Suitable For

Core 1 is genuinely useful for non-time-critical background work that would otherwise block the main scheduler:

| Task | Suitable for core 1? | Notes |
|------|---------------------|-------|
| DShot 300/600 motor output | ✗ | Timing too tight; no multi-motor sync |
| Software UART TX/RX at ≥420 kbps | ✗ | Cache jitter drops frames |
| Software UART TX at 100 kbps | Marginal | PIO is still better |
| Blackbox SPI flash writes | ✓ | Slow, non-time-critical |
| OSD frame rendering / encoding | ✓ | Background compute task |
| Telemetry packet assembly | ✓ | Doesn't need µs precision |
| WS2812 LED strip | ✗ | PIO handles this cleanly |

### Conclusion

The current plan (PIO0 → DShot, PIO1 → UART3/4, PIO2 → LED strip) is the correct architecture. Core 1 is not a viable alternative for either DShot or UART at the speeds INAV requires. Future use of core 1 for blackbox flash offload or background telemetry encoding would be worthwhile but is independent of the pin assignment decisions in this document.

---

## Known Bug: UART2 Pin Assignment in target.h

The current `inav/src/main/target/RP2350_PICO/target.h` assigns:

```c
// UART2 (currently incorrect)
// GP4/GP5 used — these belong to UART0, not UART1
```

UART2 in INAV maps to hardware UART1 on RP2350. GP4/5 are UART0 pins. The correct pins for UART2 are **GP2 (TX) / GP3 (RX)**, which are UART1 hardware. All three options in this report use GP2/3 for UART2. This bug must be corrected as part of M5 UART implementation.

---

## Next Steps (M5–M8)

| Milestone | Task | Key files |
|-----------|------|-----------|
| M5 | Add UART1/2 hardware config | `target.h`, `target.c` |
| M5 | Fix UART2 GP4/5 → GP2/3 bug | `target.h` |
| M6 | Add SPI0 config (gyro + flash) | `target.h`, `target.c` |
| M6 | Add I2C1 config (baro + mag) | `target.h` |
| M7 | Add ADC VBAT/current/RSSI | `target.h` |
| M8 | Add DShot motor outputs (PIO0) | `target.h`, `target.c` |
| M8 | Add UART3/4 PIO software serial (PIO1) | `target.h`, `target.c` |
| M8 | Add GP20/21 servo PWM outputs | `target.h` |
| M8 | Add LED strip (PIO2 SM0) | `target.h` |
