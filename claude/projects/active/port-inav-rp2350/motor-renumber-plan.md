# Motor Renumbering Plan — Match Betaflight RP2350A

**Status:** PLANNED — not yet implemented
**Goal:** Shift INAV motor pins from GP8-11 → GP10-13 to match the Betaflight RP2350A
reference target (`resource MOTOR 1 A10` … `resource MOTOR 4 A13`), without losing
any PIO capacity or servo outputs.

---

## Background

Betaflight's shipped RP2350A UF2 (2025.12.2) has these defaults confirmed by
running `resource` on real hardware:

```
resource MOTOR 1 A10   (GP10)
resource MOTOR 2 A11   (GP11)
resource MOTOR 3 A12   (GP12)
resource MOTOR 4 A13   (GP13)
resource LED 1 A25     (GP25)
```

INAV currently puts motors on GP8-11, with UART3 (PIO) on GP12/13. To match BF
we shift motors up by 2 pins and slide UART3 down into the freed slots.

---

## Current Layout

| GPIO | INAV use | PIO block |
|------|----------|-----------|
| GP0  | UART1 TX | hw uart0 |
| GP1  | UART1 RX | hw uart0 |
| GP2  | UART2 TX | hw uart1 (see UART2 note below) |
| GP3  | UART2 RX | hw uart1 |
| GP4  | SPI MISO | spi0 |
| GP5  | (free) | — |
| GP6  | SPI SCK  | spi0 |
| GP7  | SPI MOSI | spi0 |
| GP8  | **MOTOR1** | PIO0 SM0 |
| GP9  | **MOTOR2** | PIO0 SM1 |
| GP10 | **MOTOR3** | PIO0 SM2 |
| GP11 | **MOTOR4** | PIO0 SM3 |
| GP12 | UART3 TX | PIO1 SM0 |
| GP13 | UART3 RX | PIO1 SM1 |
| GP14 | UART4 TX | PIO1 SM2 |
| GP15 | UART4 RX | PIO1 SM3 |
| GP16 | Flash CS  | — |
| GP17 | Beeper    | — |
| GP18 | I2C1 SDA  | i2c1 |
| GP19 | I2C1 SCL  | i2c1 |
| GP20 | SERVO1    | PWM slice 10 CH1 |
| GP21 | SERVO2    | PWM slice 10 CH2 |
| GP22 | WS2812    | PIO2 SM0 |
| GP25 | LED0      | — |
| GP26 | ADC0 VBAT | — |
| GP27 | ADC1 CURR | — |
| GP28 | ADC2 RSSI | — |

timerHardware[] order (determines motor vs servo assignment):
1. GP8  (TIM4 CH1) — MOTOR1
2. GP9  (TIM4 CH2) — MOTOR2
3. GP10 (TIM5 CH1) — MOTOR3
4. GP11 (TIM5 CH2) — MOTOR4
5. GP12 (TIM6 CH1) — servo / dual UART3
6. GP13 (TIM6 CH2) — servo / dual UART3
7. GP14 (TIM7 CH1) — servo / dual UART4
8. GP15 (TIM7 CH2) — servo / dual UART4
9. GP20 (TIM10 CH1) — servo dedicated
10. GP21 (TIM10 CH2) — servo dedicated

---

## Proposed Layout (after renumber)

| GPIO | INAV use | Change? |
|------|----------|---------|
| GP8  | UART3 TX | **was MOTOR1** |
| GP9  | UART3 RX | **was MOTOR2** |
| GP10 | **MOTOR1** | was MOTOR3 |
| GP11 | **MOTOR2** | was MOTOR4 |
| GP12 | **MOTOR3** | was UART3 TX |
| GP13 | **MOTOR4** | was UART3 RX |
| GP14 | UART4 TX | unchanged |
| GP15 | UART4 RX | unchanged |

Everything else (GP0-7, GP16-29) unchanged.

timerHardware[] new order:
1. GP10 (TIM5 CH1) — MOTOR1  ← matches BF MOTOR1=A10
2. GP11 (TIM5 CH2) — MOTOR2  ← matches BF MOTOR2=A11
3. GP12 (TIM6 CH1) — MOTOR3  ← matches BF MOTOR3=A12
4. GP13 (TIM6 CH2) — MOTOR4  ← matches BF MOTOR4=A13
5. GP8  (TIM4 CH1) — servo / dual UART3
6. GP9  (TIM4 CH2) — servo / dual UART3
7. GP14 (TIM7 CH1) — servo / dual UART4
8. GP15 (TIM7 CH2) — servo / dual UART4
9. GP20 (TIM10 CH1) — servo dedicated
10. GP21 (TIM10 CH2) — servo dedicated

---

## PIO Analysis — Nothing Lost

### PIO0 (DShot motors)
- Before: GP8, GP9, GP10, GP11 — 4 SMs
- After:  GP10, GP11, GP12, GP13 — 4 SMs
- All pins in 0-31 range; gpio_base stays 0. No change in capacity.

### PIO1 (software UARTs)
- Before: UART3=GP12/13, UART4=GP14/15 — 4 SMs (2 per UART)
- After:  UART3=GP8/9,   UART4=GP14/15 — 4 SMs (2 per UART)
- All pins in 0-31 range; gpio_base stays 0. No change in capacity.
- PIO constraint satisfied: both UART pairs are in the same 0-31 window.

### Servo outputs
- Before: 6 capable (GP12/13 when UART3 off, GP14/15 when UART4 off, GP20/21 always)
- After:  6 capable (GP8/9 when UART3 off, GP14/15 when UART4 off, GP20/21 always)
- No change in count.

---

## Files to Edit

### 1. `src/main/target/RP2350_PICO/target.h`

Changes:
- Line 51: update comment "GP8–11 default to motors 1–4" → "GP10–13 default to motors 1–4"
- Lines 73-74: change UART3 comment from GP12/13 → GP8/9
- Lines 77-78: update reserved-pins comment
- Line 86: `UART3_TX_PIN  PA12` → `UART3_TX_PIN  PA8`
- Line 87: `UART3_RX_PIN  PA13` → `UART3_RX_PIN  PA9`
- Lines 172-174: update rp2350Pwm4/5/6 extern comments

### 2. `src/main/target/RP2350_PICO/target.c`

Changes in timerHardware[]:
- Reorder entries: TIM5(GP10/11) and TIM6(GP12/13) move to positions 1-4 (motors)
- TIM4(GP8/9) moves to positions 5-6 (servo/UART3 dual-use)
- TIM7 and TIM10 stay at positions 7-10
- Update comments throughout

No other files need changes — the DShot PIO driver reads pins from timerHardware[]
at runtime, and the PIO UART driver reads UART3_TX_PIN/UART3_RX_PIN from target.h.

---

## Follow-up Tasks (after renumber, see todo.md)

1. **Verify UART2 pin issue** — target.h says UART2→uart1 on GP2/3, but GP2/3 are
   RP2350 uart0 pins; uart1 TX starts at GP4. Verify serialUART2() opens the right
   hardware peripheral and loopback still works. Fix comment or pins as needed.

2. **Regenerate pinout diagram** — re-run
   `claude/projects/completed/rp2350-pin-assignment-plan/generate_pinout.py`
   with the updated pin assignments.
