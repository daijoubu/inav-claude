# M6: UART, GPS & Receiver Input — Reference

**Goal:** GPS tab shows satellite count + position; Receiver tab shows channel values moving.
**BF reference:** `uart/serial_uart_pico.c` (137 LOC), `uart/uart_hw.c` (~200 LOC), `uart/uart_pio.c` (403 LOC)

> **About the search tool:** The `search.py` script at `~/Documents/planes/rpi_pico_2350_port/`
> searches thousands of pages of pre-project research — including a detailed implementation guide
> (PDF + MD, 3,000+ lines), Betaflight PR analysis, and a full Claude research session. Use it to
> quickly find relevant implementation details without reading everything.

## Quick Searches
```bash
cd ~/Documents/planes/rpi_pico_2350_port
./search.py UART
./search.py --doc MD UART   # → sections at lines 221, 231, 311, 322
./search.py --doc PDF SBUS
./search.py --doc PDF CRSF
./search.py --doc CHAT PIO UART
./search.py --list-sections | grep -iE 'uart|serial|gps|receiver|sbus|crsf|pio'
```
Read sections:
- UART HAL: `offset=221, limit=130`
- PIO UARTs: `offset=322, limit=60`

---

## Hardware UARTs (`serial_uart_rp2350.c`)

RP2350 has 2 hardware UARTs (UART0, UART1).

```c
// Initialize
uart_init(uart0, 115200);
uart_set_format(uart0, 8, 1, UART_PARITY_NONE);

// Set GPIO pins
gpio_set_function(TX_PIN, GPIO_FUNC_UART);
gpio_set_function(RX_PIN, GPIO_FUNC_UART);

// Enable interrupts
uart_set_irqs_enabled(uart0,
    true,   // RX interrupt
    false); // TX interrupt (use TX empty IRQ separately if needed)

// Interrupt handler
void uart0_irq_handler(void) {
    while (uart_is_readable(uart0)) {
        uint8_t ch = uart_getc(uart0);
        // Push into INAV ring buffer
        uartRxBufPush(&uart0Port, ch);
    }
}
irq_set_exclusive_handler(UART0_IRQ, uart0_irq_handler);
irq_set_enabled(UART0_IRQ, true);
```

### Dispatch Layer
BF `serial_uart_pico.c` routes to hw UART or PIO UART:
```c
serialPort_t *serialUART(UARTDevice_e device, ...) {
    if (device == UARTDEV_1 || device == UARTDEV_2) {
        return serialUART_hw(device, ...);   // UART0/UART1
    } else {
        return serialUART_pio(device, ...);  // PIOUART0/PIOUART1
    }
}
```

---

## Signal Inversion (SBUS)

**RP2350 huge advantage:** hardware GPIO inversion — no external inverter circuit needed!

```c
// SBUS: 100000 baud, 8E2, inverted
uart_init(uart1, 100000);
uart_set_format(uart1, 8, 2, UART_PARITY_EVEN);

// Invert RX signal in GPIO — that's it!
gpio_set_function(SBUS_RX_PIN, GPIO_FUNC_UART);
gpio_set_inover(SBUS_RX_PIN, GPIO_OVERRIDE_INVERT);

// STM32F4 required an external hardware inverter circuit.
// RP2350 does it in GPIO controller — gpio_set_inover().
```

---

## Common UART Protocol Configs

| Protocol | Baud | Format | Inversion | Usage |
|----------|------|--------|-----------|-------|
| GPS (UBLOX) | 115200 | 8N1 | No | Position/velocity |
| SBUS | 100000 | 8E2 | Yes (gpio_set_inover) | Receiver input |
| CRSF | 420000 | 8N1 | No | Receiver + telemetry |
| SmartPort | 57600 | 8N1 | Half-duplex | Telemetry output |
| MAVLink | 57600 | 8N1 | No | Telemetry output |
| MSP | 115200 | 8N1 | No | Configurator |

---

## PIO Software UARTs (`uart_pio.c` port)

For more than 2 UARTs, use PIO block 1 (`PIO_UART_INDEX=1` from target.h).

BF `uart/uart_pio.c` (403 LOC): one PIO block shared by 2 software UARTs (PIOUART0, PIOUART1).

```c
// BF-verified PR #14635, #14664
// Load TX and RX programs once, shared across both UARTs
uint offset_tx = pio_add_program(pio1, &uart_tx_program);
uint offset_rx = pio_add_program(pio1, &uart_rx_program);

// PIOUART0: SM0=TX, SM1=RX
// PIOUART1: SM2=TX, SM3=RX
uart_tx_program_init(pio1, 0, offset_tx, TX0_PIN, baud);
uart_rx_program_init(pio1, 1, offset_rx, RX0_PIN, baud);
```

### GPIO Base Handling for Pins 16-47
**CRITICAL:** For PIO programs accessing pins 16+, must call `pio_set_gpio_base()`.
Same gotcha as DShot (see M7). RP2350 PIO can only directly address 32 consecutive pins.
```c
// If any pin > 31, set GPIO base:
pio_set_gpio_base(pio1, 16);  // base = 16, so pins 16-47 accessible
```

### Interrupt-Driven Operation
```c
// RX FIFO not-empty → read bytes
// TX FIFO not-full → write bytes
// Start/stop SM: pio_sm_set_enabled(pio, sm, true/false)
```

### Port Numbering Note (BF PR #14664)
- Process SOFTSERIAL ports before PIOUART in port numbering
- Guard against zero-length arrays when `SERIAL_PIOUART_COUNT == 0`
- Use type-based routing (`serialType()` checks) rather than direct lookups

---

## DMA for UART RX (Circular Buffer)

```c
// Configure RX DMA with ring buffer for continuous GPS receive
dma_channel_config cfg = dma_channel_get_default_config(rx_dma);
channel_config_set_transfer_data_size(&cfg, DMA_SIZE_8);
channel_config_set_read_increment(&cfg, false);   // Read from UART DR (fixed)
channel_config_set_write_increment(&cfg, true);    // Write to buffer
channel_config_set_ring(&cfg, true, 8);            // 256-byte (2^8) ring buffer
channel_config_set_dreq(&cfg, uart_get_dreq(uart0, false));

dma_channel_configure(rx_dma, &cfg,
    rxBuffer,               // Destination (ring)
    &uart_get_hw(uart0)->dr, // Source (UART data register)
    256,                    // Transfer count (wraps)
    true);                  // Start immediately
```

---

## GPS Integration

- Connect GPS to UART0 (or UART1)
- INAV's GPS parsing code (UBLOX/NMEA) is platform-agnostic — works once UART RX data flows
- Configure in INAV: `serial_config` → port → GPS
- GPS auto-baud detection or set 115200 fixed in target.h

## Receiver Integration

- SBUS: UART1 with inversion (see above)
- CRSF: UART with 420000 baud, no inversion
- INAV needs SBUS (unlike BF which disabled most RX protocols on RP2350)
- Telemetry output can share CRSF UART (half-duplex)

## Verification

```bash
# GPS: Configurator → GPS tab → satellites should count up after fix
# Receiver: Configurator → Receiver tab → move sticks → channel values move
# CLI: 'status' shows GPS satellites, receiver link
```
