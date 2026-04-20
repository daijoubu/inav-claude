# M5: SPI & Gyro/Accelerometer Reading — Reference

**Goal:** Live gyro/accel data in configurator when board is tilted.
**BF reference:** `bus_spi_pico.c` (518 LOC), `dma_pico.c` (155 LOC)

> **About the search tool:** The `search.py` script at `~/Documents/planes/rpi_pico_2350_port/`
> searches thousands of pages of pre-project research — including a detailed implementation guide
> (PDF + MD, 3,000+ lines), Betaflight PR analysis, and a full Claude research session. Use it to
> quickly find relevant implementation details without reading everything.

## Quick Searches
```bash
cd ~/Documents/planes/rpi_pico_2350_port
./search.py SPI
./search.py DMA
./search.py --doc MD SPI    # → section at line 135
./search.py --doc PDF gyro
./search.py --doc CHAT "SPI+DMA"
./search.py --list-sections | grep -iE 'spi|dma|gyro|accel|exti'
```
Read sections:
- SPI HAL: `offset=135, limit=100`
- GPIO Interrupts (EXTI for gyro data-ready): `offset=534, limit=80`

---

## SPI Driver (`bus_spi_rp2350.c`)

### Initialization
```c
void spiInitDevice(SPIDevice device) {
    spi_inst_t *spi = (device == SPIDEV_1) ? spi0 : spi1;

    spi_init(spi, 10 * 1000 * 1000);  // 10 MHz default

    // Set GPIO functions
    gpio_set_function(sckPin,  GPIO_FUNC_SPI);
    gpio_set_function(mosiPin, GPIO_FUNC_SPI);
    gpio_set_function(misoPin, GPIO_FUNC_SPI);

    // CRITICAL: Enable MISO pullup (prevents SD card MISO float on shared bus)
    gpio_set_pulls(misoPin, true, false);  // BF bus_spi_pico.c:228

    // Fast slew rate for high-speed operation
    gpio_set_slew_rate(sckPin, GPIO_SLEW_RATE_FAST);
}
```

### Blocking Transfers
```c
// Full-duplex (gyro read: tx dummy bytes, rx data)
spi_write_read_blocking(spi, txBuf, rxBuf, len);

// Write-only (register write)
spi_write_blocking(spi, txBuf, len);

// Read-only (fill tx with 0xFF)
spi_read_blocking(spi, 0xFF, rxBuf, len);
```

### DMA Transfers (threshold: ≥ 8 bytes per BF)
```c
// Claim channels dynamically — NO static mapping needed (BF PR #14513)
uint dma_tx = dma_claim_unused_channel(true);
uint dma_rx = dma_claim_unused_channel(true);

// TX config
dma_channel_config c_tx = dma_channel_get_default_config(dma_tx);
channel_config_set_transfer_data_size(&c_tx, DMA_SIZE_8);
channel_config_set_dreq(&c_tx, spi_get_dreq(spi, true));  // TX DREQ
dma_channel_configure(dma_tx, &c_tx,
    &spi_get_hw(spi)->dr, txBuf, len, false);

// RX config
dma_channel_config c_rx = dma_channel_get_default_config(dma_rx);
channel_config_set_transfer_data_size(&c_rx, DMA_SIZE_8);
channel_config_set_dreq(&c_rx, spi_get_dreq(spi, false));  // RX DREQ
channel_config_set_read_increment(&c_rx, false);
channel_config_set_write_increment(&c_rx, true);
dma_channel_configure(dma_rx, &c_rx,
    rxBuf, &spi_get_hw(spi)->dr, len, false);

// CRITICAL: Acknowledge IRQ BEFORE callback (edge-triggered!) — BF PR #14514
dma_channel_set_irq0_enabled(dma_rx, true);
irq_set_exclusive_handler(DMA_IRQ_0, dmaIrqHandler);
irq_set_enabled(DMA_IRQ_0, true);

// In IRQ handler:
void dmaIrqHandler(void) {
    dma_channel_acknowledge_irq0(dma_rx);  // ACK FIRST
    gpio_put(csPin, 1);                    // CS high
    // THEN call callback
    if (completionCallback) completionCallback();
}

// Start both channels simultaneously
dma_start_channel_mask((1u << dma_tx) | (1u << dma_rx));
```

**CRITICAL pitfall:** Edge-triggered DMA IRQ — if you ACK *after* callback, you miss events
generated during callback execution. (BF `dma_pico.c:68-71`)

### CS Pin Management
**CRITICAL:** Never call `gpio_init()` on CS pin if already configured as SIO output.
(Handled in `IOConfigGPIO()` — see M2 reference.) CS pins must start HIGH.

### SPI Clock / Format
```c
spi_set_baudrate(spi, hz);           // Returns actual baudrate
spi_set_format(spi, 8, cpol, cpha, SPI_MSB_FIRST);  // for CPOL/CPHA modes
```

---

## DMA Driver (`dma_rp2350.c`)

- 16 DMA channels on RP2350
- Dynamic allocation: `dma_claim_unused_channel(false)` = optional, `true` = panic on failure
- Per-core IRQ routing: DMA_IRQ_0 on core 0, DMA_IRQ_1 on core 1
- Handler table indexed by channel number (array of function pointers)
- `USE_DMA_SPEC` is NOT needed — dynamic allocation replaces static mapping

---

## Gyro (EXTI Data-Ready)

```c
// Gyro data-ready pin → GPIO edge interrupt
gpio_set_irq_enabled_with_callback(GYRO_EXTI_PIN,
    GPIO_IRQ_EDGE_RISE, true, &gyroExtiHandler);

void gyroExtiHandler(uint gpio, uint32_t events) {
    if (gpio == GYRO_EXTI_PIN) {
        // Trigger SPI DMA read
        gyroDmaReadStart();
    }
}
```

Gyro read timeline at 8kHz (125μs budget):
1. Data-ready EXTI fires
2. CS low
3. Start SPI DMA (7 bytes: reg addr + 6 data)
4. DMA completes → IRQ → CS high → parse data
5. Total: must finish in <125μs

---

## IMU Wiring (Pico 2 Pinout)

Suggested connections for ICM42688P or MPU6500:
```
SPI0: GP18=SCK, GP19=MOSI, GP16=MISO
CS:   GP17 (or any free GPIO)
INT:  GP20 (gyro data-ready → EXTI)
```
Use `target.h` to define: `#define GYRO_1_SPI_INSTANCE SPI_DEV(0)`

---

## Success Criteria

- `WHO_AM_I` register returns `0x47` (ICM42688P) or `0x68` (MPU6000)
- Gyro values change when board is moved
- No DMA timeouts at 4kHz; ideally 8kHz
- Timing jitter < 10μs
- INAV Configurator shows live gyro/accel data on Sensors tab
