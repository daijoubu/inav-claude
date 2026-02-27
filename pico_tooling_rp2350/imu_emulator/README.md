# MPU-6000 SPI Slave Emulator

Raspberry Pi Pico firmware that emulates an MPU-6000 IMU over SPI. An INAV
flight controller sees it as a real IMU — useful for driver validation, HITL
testing, and unblocking M5 of the RP2350 port without real IMU hardware.

## Wiring

### To RP2350 INAV target (feature/rp2350-port)

The RP2350_PICO target assigns SPI0 to GP4–7 for the gyro bus
(`SPI1_MISO=PA4/GP4`, `SPI1_SCK=PA6/GP6`, `SPI1_MOSI=PA7/GP7`).
GP5 is the natural SPI0 CSn; the INT pin is TBD in target.h.

```
Pico emulator (GP)    RP2350 INAV target (GP)
------------------    -----------------------
GP19  SPI0 TX  ——→   GP4   SPI0 MISO
GP17  SPI0 CSn ←——   GP5   SPI0 CSn  (add to target.h as gyro CS)
GP18  SPI0 SCK ←——   GP6   SPI0 SCK
GP16  SPI0 RX  ←——   GP7   SPI0 MOSI
GP20  INT out  ——→   GP?   GYRO_EXTI  (choose a free GPIO, add to target.h)
GND            ——    GND
```

### Generic wiring (any INAV FC)

```
Pico (emulator)          INAV FC (SPI master)
---------------          --------------------
GP16  SPI0 RX  ←————————  FC SPI MOSI
GP17  SPI0 CSn ←————————  FC SPI CS   (active low)
GP18  SPI0 SCK ←————————  FC SPI SCK
GP19  SPI0 TX  ————————→  FC SPI MISO
GP20  GPIO out ————————→  FC INT / EXTI pin (data ready)
GND            ————————   GND
```

SPI protocol: Mode 0 (CPOL=0, CPHA=0), MSB first, up to ~10 MHz.

## Flashing

1. Hold BOOTSEL on the Pico and plug in USB → appears as a USB drive
2. Copy `build/mpu6000_emu.uf2` to the drive
3. Pico reboots into emulator firmware automatically

To restore debugprobe firmware: flash debugprobe.uf2 the same way.

## USB Command Interface

Open `/dev/ttyACM0` (any baud rate) with a terminal (e.g. `picocom /dev/ttyACM0`):

```
gyro X Y Z          Set gyro LSBs (int16). Scale: 16.4 LSB/dps at ±2000 dps
                    Example: gyro 164 0 0  → 10 dps around X axis

accel X Y Z         Set accel LSBs (int16). Scale: 2048 LSB/g at ±16g
                    Default: accel_z = 2048 (1g pointing down)
                    Example: accel 0 0 2048

temp T              Set raw temperature (int16)

raw ADDR VAL        Write any register (hex values)
                    Example: raw 75 68  → set WHO_AM_I to 0x68

status              Print current sensor values and key register state
```

## What INAV Checks During Detection

INAV's `mpu6000DeviceDetect()` performs these SPI transactions:

1. **Write** `PWR_MGMT_1` (0x6B) = 0x80 — soft reset
2. **Read** `WHO_AM_I` (0x75) — must return **0x68**
3. **Read** `PRODUCT_ID` (0x0C) — must return a valid revision ID

The emulator pre-populates both registers with the correct values.

## Register Map

Key registers pre-configured at startup:

| Register | Addr | Value | Meaning                          |
|----------|------|-------|----------------------------------|
| WHO_AM_I | 0x75 | 0x68  | MPU-6000 identity                |
| PRODUCT_ID | 0x0C | 0x54 | Rev C4 — valid product ID      |
| PWR_MGMT_1 | 0x6B | 0x40 | Sleep mode (INAV wakes it up)  |
| ACCEL_Z  | 0x3F–0x40 | 2048 | 1g pointing down             |
| INT_STATUS | 0x3A | 0x01 | Data ready flag always set     |

Burst read from 0x3B returns 14 bytes: ACCEL_XYZ + TEMP + GYRO_XYZ.

## Emulated Sensor Ranges

Default INAV MPU-6000 init sets:
- Gyro: ±2000 dps → **16.4 LSB/dps** → 1000 dps = 16400 raw
- Accel: ±16g → **2048 LSB/g** → 1g = 2048 raw

## Building from Source

```bash
cd imu_emulator
cmake -DPICO_BOARD=pico -S . -B build
make -j$(nproc) -C build
# Output: build/mpu6000_emu.uf2
```

Requires pico-sdk with TinyUSB submodule initialized:
```bash
cd ../pico-sdk
git submodule update --init lib/tinyusb
```
