# M3: USB VCP & Debug Console — Reference

**Goal:** USB serial terminal shows INAV boot messages + MSP responds.
**BF reference:** `serial_usb_vcp_pico.c` (212 LOC), `usb/usb_cdc.c`, `usb/tusb_config.h`

> **About the search tool:** The `search.py` script at `~/Documents/planes/rpi_pico_2350_port/`
> searches thousands of pages of pre-project research — including a detailed implementation guide
> (PDF + MD, 3,000+ lines), Betaflight PR analysis, and a full Claude research session. Use it to
> quickly find relevant implementation details without reading everything.

## Quick Searches
```bash
cd ~/Documents/planes/rpi_pico_2350_port
./search.py USB
./search.py TinyUSB
./search.py --doc MD USB     # → sections at lines 675, 729, 1581
./search.py --doc CHAT VCP
./search.py --list-sections | grep -iE 'usb|vcp|cdc|msp'
```
Read sections:
- USB VCP: `offset=675, limit=100`
- USB MSC (for later reference): `offset=1581, limit=80`
- Interrupt mgmt / NVIC priority: `offset=737, limit=80`

---

## TinyUSB Integration

Pico SDK bundles TinyUSB — no separate install needed.

```cmake
# CMakeLists.txt additions for M3
target_link_libraries(RP2350_PICO
    pico_stdlib
    pico_stdio_usb
    tinyusb_device
    tinyusb_board
)
```

**CRITICAL:** `cdc_usb_init()` / `tusb_init()` MUST run on **core 0** (BF `serial_usb_vcp_pico.c`).

### USB Descriptors (`usb_descriptors.c`)
```c
// Vendor/Product strings
#define USB_VID   0xXXXX  // allocate for INAV or use generic CDC
#define USB_PID   0xXXXX
// Strings: "INAV", "RP2350_PICO"
// CDC endpoints: EP1 IN/OUT (data), EP2 IN (notification)
```

### TinyUSB Config (`tusb_config.h`)
```c
#define CFG_TUD_CDC          1
#define CFG_TUD_CDC_RX_BUFSIZE  256
#define CFG_TUD_CDC_TX_BUFSIZE  256
```

### TinyUSB Task Polling
```c
// Must call periodically from scheduler (low-priority task)
void usbTask(void) {
    tud_task();
}
```

---

## VCP Serial Port (`serial_usb_vcp_rp2350.c`)

Implement INAV's `serialPort_t` vtable:
```c
#include "tusb.h"

// Initialize VCP port
serialPort_t *usbVcpOpen(void) {
    tusb_init();
    // return &vcpPort;
}

// Write
void usbVcpWrite(serialPort_t *port, uint8_t ch) {
    tud_cdc_write(&ch, 1);
    tud_cdc_write_flush();
}

// Buffered write — flush on buffer full or endWrite()
void usbVcpWriteBuf(serialPort_t *port, const void *data, int count) {
    tud_cdc_write(data, count);
    tud_cdc_write_flush();
}

// Read
uint8_t usbVcpRead(serialPort_t *port) {
    uint8_t ch;
    tud_cdc_read(&ch, 1);
    return ch;
}

uint32_t usbVcpRxBytesWaiting(const serialPort_t *port) {
    return tud_cdc_available();
}

uint32_t usbVcpTxBytesFree(const serialPort_t *port) {
    return tud_cdc_write_available();
}
```

### RX Ring Buffer (TinyUSB callback → INAV)
```c
// TinyUSB calls this when data arrives
void tud_cdc_rx_cb(uint8_t itf) {
    uint8_t buf[64];
    uint32_t count = tud_cdc_read(buf, sizeof(buf));
    // push count bytes into INAV ring buffer
    for (uint32_t i = 0; i < count; i++) {
        serialRxBufPush(&vcpPort, buf[i]);
    }
}
```

---

## MSP Protocol (Basic)

```c
// MSP responds to version/board queries over USB VCP
// These are in INAV's existing MSP code — should work once
// the serialPort_t vtable is wired up correctly.

// Verify with:
// $ echo -n "$M<\x00\xfc\xfc" | nc -u localhost 5760
// Or just open INAV Configurator and watch for board name
```

### Key MSP messages for M3 verification:
- `MSP_API_VERSION` (1)
- `MSP_FC_VARIANT` (2)
- `MSP_FC_VERSION` (3)
- `MSP_BOARD_INFO` (4) — should return "RP2350_PICO"

---

## USB 1.1 vs 2.0 Note

RP2350 has USB 1.1 (Full Speed, 12 Mbps) vs STM32's USB 2.0 (High Speed, 480 Mbps).
- **Fine for INAV configurator** — MSP protocol is low bandwidth
- **Fine for blackbox download** — slower but workable
- Mentioned in PDF page 2-3

---

## Interrupt Priority for USB

From `inav_rp2350_detailed.md` offset=737:
- USB = **low priority** (lower than gyro, UART, SPI)
- Don't let USB interrupt preempt gyro DMA completion callbacks

---

## Testing

```bash
# After flashing:
# 1. Connect Pico 2 via USB
# 2. Check it appears as serial device:
ls /dev/ttyACM*   # or /dev/ttyUSB* on some systems
# 3. Open terminal:
picocom -b 115200 /dev/ttyACM0
# 4. Should see INAV boot messages
# 5. Try MSP: open INAV Configurator, connect
```
