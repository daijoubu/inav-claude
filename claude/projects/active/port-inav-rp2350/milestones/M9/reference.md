# M9: I2C Sensors — Baro + Mag — Reference

**Goal:** Configurator shows barometer altitude + magnetometer heading updating live.
**BF reference:** `bus_i2c_pico.c` (489 LOC)

> **About the search tool:** The `search.py` script at `~/Documents/planes/rpi_pico_2350_port/`
> searches thousands of pages of pre-project research — including a detailed implementation guide
> (PDF + MD, 3,000+ lines), Betaflight PR analysis, and a full Claude research session. Use it to
> quickly find relevant implementation details without reading everything.

## Quick Searches
```bash
cd ~/Documents/planes/rpi_pico_2350_port
./search.py I2C
./search.py --doc MD I2C    # → sections at lines 364, 375, 438
./search.py --doc PDF barometer
./search.py --doc PDF magnetometer
./search.py --doc CHAT I2C
./search.py --list-sections | grep -iE 'i2c|baro|mag|sensor'
```
Read sections:
- I2C HAL: `offset=364, limit=100`
- Common I2C Issues: `offset=438, limit=40`

---

## I2C Driver (`bus_i2c_rp2350.c`)

**IMPORTANT:** BF PR #14537 uses **interrupt-driven, non-blocking transfers**, NOT DMA.
The 16-byte TX FIFO is used to batch data, minimizing interrupt frequency.

### Initialization
```c
// I2C0 / I2C1
void i2cInit(I2CDevice device, uint16_t clockSpeed) {
    i2c_inst_t *i2c = (device == I2CDEV_1) ? i2c0 : i2c1;

    i2c_init(i2c, clockSpeed * 1000);   // 100000 or 400000

    gpio_set_function(SDA_PIN, GPIO_FUNC_I2C);
    gpio_set_function(SCL_PIN, GPIO_FUNC_I2C);
    gpio_pull_up(SDA_PIN);   // IMPORTANT: must enable pull-ups
    gpio_pull_up(SCL_PIN);

    // Enable interrupts
    i2c_hw_t *hw = i2c_get_hw(i2c);
    hw->enable = 0;  // disable briefly to configure
    hw->rx_tl = I2C_FIFO_BUFFER_DEPTH - 2;  // CRITICAL: rx threshold (BF bus_i2c_pico.c:468)
    hw->enable = 1;
}
```

### Pin Validation (important for I2C0/I2C1 assignment)
```
I2C0: pins where (pin % 4 == 0) or (pin % 4 == 1)
I2C1: pins where (pin % 4 == 2) or (pin % 4 == 3)
```

### State Machine
```
I2C_STATE_IDLE → I2C_STATE_ACTIVE → I2C_STATE_READ_DATA → I2C_STATE_IDLE
```

### Write Operation
```c
// Preload TX FIFO with register address + data bytes
// Set STOP bit on last byte
void i2cWriteBuffer(I2CDevice device, uint8_t addr, uint8_t reg,
                    uint8_t len, const uint8_t *data) {
    i2c_hw_t *hw = i2c_get_hw(i2c);
    hw->enable = 0;
    hw->tar = addr;  // set target address
    hw->enable = 1;

    // Write register address
    hw->data_cmd = I2C_IC_DATA_CMD_RESTART_BITS | reg;

    // Write data bytes, STOP on last
    for (int i = 0; i < len; i++) {
        uint32_t cmd = data[i];
        if (i == len - 1) cmd |= I2C_IC_DATA_CMD_STOP_BIT;
        hw->data_cmd = cmd;
    }
}
```

### Read Operation
```c
// Single batch if len <= 15 (FIFO - 1 for reg address byte)
// Multi-batch with RESTART for reads > 15 bytes (uses RX_FULL interrupt)
void i2cReadBuffer(I2CDevice device, uint8_t addr, uint8_t reg,
                   uint8_t len, uint8_t *data) {
    i2c_hw_t *hw = i2c_get_hw(i2c);
    hw->enable = 0;
    hw->tar = addr;
    hw->enable = 1;

    // Write register address (no stop yet)
    hw->data_cmd = reg;

    // Issue read commands
    for (int i = 0; i < len; i++) {
        uint32_t cmd = I2C_IC_DATA_CMD_CMD_BITS;  // read bit
        if (i == 0)       cmd |= I2C_IC_DATA_CMD_RESTART_BITS;
        if (i == len - 1) cmd |= I2C_IC_DATA_CMD_STOP_BIT;
        hw->data_cmd = cmd;
    }
    // Data arrives in RX FIFO → read via RX_FULL interrupt
}
```

### CRITICAL: RX FIFO Threshold
```c
hw->rx_tl = I2C_FIFO_BUFFER_DEPTH - 2;
// FIFO depth is 16. Threshold = 14.
// Prevents race condition between reading FIFO and new data arriving.
// (BF bus_i2c_pico.c:468)
```

### Interrupt Sources
```c
// Enable these interrupts:
hw->intr_mask = I2C_IC_INTR_MASK_M_STOP_DET_BITS |
                I2C_IC_INTR_MASK_M_TX_ABRT_BITS  |
                I2C_IC_INTR_MASK_M_TX_OVER_BITS  |
                I2C_IC_INTR_MASK_M_RX_OVER_BITS  |
                I2C_IC_INTR_MASK_M_RX_FULL_BITS;
// STOP_DET: transfer complete
// TX_ABRT: NACK or arbitration loss
// TX_OVER/RX_OVER: FIFO overflow
// RX_FULL: data ready (for multi-batch reads)
```

### Non-Blocking API
```c
void i2cWriteBuffer(device, addr, reg, len, data);  // starts transfer
void i2cReadBuffer(device, addr, reg, len, data);   // starts transfer
bool i2cBusy(I2CDevice device);                     // poll completion
```

---

## Common I2C Addresses

| Sensor | Address |
|--------|---------|
| BMP280 | 0x76 or 0x77 |
| BMP388 | 0x76 or 0x77 |
| MS5611 | 0x77 |
| DPS310 | 0x77 |
| HMC5883L mag | 0x1E |
| QMC5883L mag | 0x0D |
| IST8310 mag | 0x0C |

---

## Barometer Integration

INAV auto-detects barometers on boot (tries each known type):
```c
bool bmp280Detect(baroDev_t *baro) {
    uint8_t chipId;
    // Try both I2C addresses
    if (i2cRead(I2CDEV_1, 0x76, BMP280_CHIP_ID_REG, 1, &chipId) && chipId == 0x58) {
        // configure baro...
        return true;
    }
    return false;
}
```
BMP280 reads 6 bytes (3 for pressure, 3 for temperature) — single I2C transaction.

---

## Magnetometer Integration

**NOTE:** BF disables MAG on RP2350 (`#undef USE_MAG`), but **INAV needs it for navigation**.
Must keep `USE_MAG` enabled and ensure I2C driver handles concurrent baro+mag.

```c
// Read 6 bytes: X(H,L), Y(H,L), Z(H,L) or similar depending on sensor
uint8_t magData[6];
i2cReadBuffer(I2CDEV_1, MAG_I2C_ADDR, MAG_DATA_REG, 6, magData);
```

---

## Speed Modes

```c
// Some sensors need 100kHz (not 400kHz)
// Configure per-sensor if detection fails at fast speed
i2c_set_baudrate(i2c0, 100000);  // fallback to standard speed
```

---

## Troubleshooting I2C

| Problem | Solution |
|---------|----------|
| Sensor not detected | Check pull-ups (2.2kΩ–10kΩ), verify address, try 100kHz |
| Intermittent reads | Add delay after config writes; check for bus contention |
| Wrong data | Check endianness (MSB vs LSB first per sensor datasheet) |
| Bus lockup | Toggle SCL 9× to release stuck slave; call `i2c_deinit()` + `i2c_init()` |

---

## Verification

```bash
# Configurator → Sensors tab:
# - Barometer: cover sensor with finger → altitude should increase
# - Magnetometer: rotate board slowly → heading changes
# - Both should update live without glitches
```
