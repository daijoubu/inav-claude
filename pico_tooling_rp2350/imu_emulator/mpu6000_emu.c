/*
 * MPU-6000 SPI Slave Emulator for Raspberry Pi Pico
 *
 * Emulates an MPU-6000 IMU over SPI so an INAV flight controller can
 * detect it and read sensor data — no real IMU hardware required.
 *
 * Useful for:
 *   - Validating INAV SPI driver (RP2350 M5)
 *   - Injecting arbitrary gyro/accel values for testing
 *   - Fault injection and edge-case testing
 *
 * SPI Protocol (MPU-6000 Mode 0: CPOL=0, CPHA=0, MSB first):
 *   CS low → [addr byte: bit7=R/W, bits6:0=reg] → [data bytes ...] → CS high
 *   Burst read: CS stays low, address auto-increments
 *
 * Wiring to INAV flight controller:
 *   Pico GP16 (SPI0 RX / MOSI-in)  → FC SPI MOSI
 *   Pico GP17 (SPI0 CSn)           → FC SPI CS
 *   Pico GP18 (SPI0 SCK)           → FC SPI SCK
 *   Pico GP19 (SPI0 TX / MISO-out) → FC SPI MISO
 *   Pico GP20 (GPIO out)           → FC INT pin (data ready)
 *   Pico GND                       → FC GND
 *
 * USB command interface (open /dev/ttyACM0 at any baud):
 *   gyro X Y Z          — set gyro LSBs (int16, 16.4 LSB/dps at ±2000dps)
 *   accel X Y Z         — set accel LSBs (int16, 2048 LSB/g at ±16g)
 *   temp T              — set raw temp (int16)
 *   raw ADDR VAL        — write any register (hex: raw 75 68)
 *   status              — print current sensor values
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "pico/stdlib.h"
#include "hardware/spi.h"
#include "hardware/gpio.h"
#include "hardware/irq.h"
#include "hardware/timer.h"
#include "pico/mutex.h"

// ---------------------------------------------------------------------------
// Pin assignments
// ---------------------------------------------------------------------------
#define PIN_MISO        19   // SPI0 TX  → FC MISO
#define PIN_CS          17   // SPI0 CSn ← FC CS (active low)
#define PIN_SCK         18   // SPI0 SCK ← FC SCLK
#define PIN_MOSI        16   // SPI0 RX  ← FC MOSI
#define PIN_INT         20   // data-ready interrupt output → FC INT

#define SPI_PORT        spi0

// ---------------------------------------------------------------------------
// MPU-6000 register addresses (subset needed by INAV)
// ---------------------------------------------------------------------------
#define REG_PRODUCT_ID      0x0C
#define REG_SMPLRT_DIV      0x19
#define REG_CONFIG          0x1A
#define REG_GYRO_CONFIG     0x1B
#define REG_ACCEL_CONFIG    0x1C
#define REG_INT_PIN_CFG     0x37
#define REG_INT_ENABLE      0x38
#define REG_INT_STATUS      0x3A   // DATA_RDY_INT bit
#define REG_ACCEL_XOUT_H    0x3B   // burst read starts here (14 bytes)
#define REG_ACCEL_XOUT_L    0x3C
#define REG_ACCEL_YOUT_H    0x3D
#define REG_ACCEL_YOUT_L    0x3E
#define REG_ACCEL_ZOUT_H    0x3F
#define REG_ACCEL_ZOUT_L    0x40
#define REG_TEMP_OUT_H      0x41
#define REG_TEMP_OUT_L      0x42
#define REG_GYRO_XOUT_H     0x43
#define REG_GYRO_XOUT_L     0x44
#define REG_GYRO_YOUT_H     0x45
#define REG_GYRO_YOUT_L     0x46
#define REG_GYRO_ZOUT_H     0x47
#define REG_GYRO_ZOUT_L     0x48
#define REG_SIGNAL_PATH_RST 0x68
#define REG_USER_CTRL       0x6A
#define REG_PWR_MGMT_1      0x6B
#define REG_PWR_MGMT_2      0x6C
#define REG_WHO_AM_I        0x75

// Identity values INAV checks during detection
#define MPU6000_WHO_AM_I_VAL    0x68
#define MPU6000_PRODUCT_ID_VAL  0x54   // Rev C4 — valid product ID

// INT_STATUS: data ready flag
#define INT_STATUS_DATA_RDY     0x01

// PWR_MGMT_1 reset bit
#define PWR_MGMT1_RESET         0x80

// ---------------------------------------------------------------------------
// Register map — 128 bytes covers all MPU-6000 registers (0x00–0x7F)
// ---------------------------------------------------------------------------
static volatile uint8_t reg_map[128];

// Sensor values (protected by mutex for USB-command updates)
static mutex_t sensor_mutex;
static int16_t gyro_x  = 0;
static int16_t gyro_y  = 0;
static int16_t gyro_z  = 0;
static int16_t accel_x = 0;
static int16_t accel_y = 0;
static int16_t accel_z = 2048;  // 1g at ±16g full scale (2048 LSB/g)
static int16_t temp_raw = 0;    // raw temp; 0 → ~36.5°C

// ---------------------------------------------------------------------------
// SPI transaction state (updated in CS GPIO interrupt + SPI RX interrupt)
// ---------------------------------------------------------------------------
static volatile bool    txn_active    = false;
static volatile uint8_t txn_reg_addr  = 0;
static volatile bool    txn_is_read   = false;
static volatile int     txn_byte_idx  = 0;  // 0 = address byte not yet received

// ---------------------------------------------------------------------------
// Sensor register update — call whenever gyro/accel/temp values change
// ---------------------------------------------------------------------------
static void update_sensor_regs(void) {
    // Accel XYZ (big-endian)
    reg_map[REG_ACCEL_XOUT_H] = (uint8_t)((accel_x >> 8) & 0xFF);
    reg_map[REG_ACCEL_XOUT_L] = (uint8_t)(accel_x & 0xFF);
    reg_map[REG_ACCEL_YOUT_H] = (uint8_t)((accel_y >> 8) & 0xFF);
    reg_map[REG_ACCEL_YOUT_L] = (uint8_t)(accel_y & 0xFF);
    reg_map[REG_ACCEL_ZOUT_H] = (uint8_t)((accel_z >> 8) & 0xFF);
    reg_map[REG_ACCEL_ZOUT_L] = (uint8_t)(accel_z & 0xFF);
    // Temperature
    reg_map[REG_TEMP_OUT_H]   = (uint8_t)((temp_raw >> 8) & 0xFF);
    reg_map[REG_TEMP_OUT_L]   = (uint8_t)(temp_raw & 0xFF);
    // Gyro XYZ (big-endian)
    reg_map[REG_GYRO_XOUT_H]  = (uint8_t)((gyro_x >> 8) & 0xFF);
    reg_map[REG_GYRO_XOUT_L]  = (uint8_t)(gyro_x & 0xFF);
    reg_map[REG_GYRO_YOUT_H]  = (uint8_t)((gyro_y >> 8) & 0xFF);
    reg_map[REG_GYRO_YOUT_L]  = (uint8_t)(gyro_y & 0xFF);
    reg_map[REG_GYRO_ZOUT_H]  = (uint8_t)((gyro_z >> 8) & 0xFF);
    reg_map[REG_GYRO_ZOUT_L]  = (uint8_t)(gyro_z & 0xFF);

    // Data ready flag always set (data available)
    reg_map[REG_INT_STATUS] |= INT_STATUS_DATA_RDY;
}

// ---------------------------------------------------------------------------
// Register map initialisation — power-on-reset state + identity registers
// ---------------------------------------------------------------------------
static void reg_map_init(void) {
    memset((void *)reg_map, 0x00, sizeof(reg_map));

    // Identity
    reg_map[REG_WHO_AM_I]    = MPU6000_WHO_AM_I_VAL;
    reg_map[REG_PRODUCT_ID]  = MPU6000_PRODUCT_ID_VAL;

    // Power-on state: sleeping with internal oscillator
    reg_map[REG_PWR_MGMT_1] = 0x40;   // SLEEP=1

    // Populate sensor registers with initial values
    update_sensor_regs();
}

// ---------------------------------------------------------------------------
// SPI RX interrupt handler — called for each received byte
//
// Timing note (1 MHz SPI, 133 MHz Pico):
//   Each byte = 8 µs.  Interrupt fires ~end-of-byte.  We have the full next
//   byte period (~8 µs = ~1064 cycles) to load the TX FIFO before the
//   hardware needs the next byte.  At 1 MHz this is very comfortable.
// ---------------------------------------------------------------------------
static void spi_rx_irq_handler(void) {
    // Drain all bytes currently in the RX FIFO
    while (spi_is_readable(SPI_PORT)) {
        uint8_t rx = (uint8_t)spi_get_hw(SPI_PORT)->dr;   // read clears RX FIFO

        if (txn_byte_idx == 0) {
            // --- Address byte ---
            txn_is_read  = (rx & 0x80) != 0;
            txn_reg_addr = rx & 0x7F;
            txn_byte_idx = 1;

            // For reads: pre-load first data byte into TX FIFO.
            // The byte sent DURING the address phase (byte 0 of slave TX)
            // is a don't-care — master ignores it.  Byte 1 is the real data.
            if (txn_is_read) {
                // Write register value to TX FIFO now; hardware will use it
                // for the next byte it shifts out.
                spi_get_hw(SPI_PORT)->dr = reg_map[txn_reg_addr & 0x7F];
            } else {
                spi_get_hw(SPI_PORT)->dr = 0x00;  // dummy TX during write data phase
            }

        } else {
            // --- Data byte(s) ---
            if (txn_is_read) {
                // Master sent dummy; we already sent reg_map[addr] above.
                // Pre-load NEXT address for burst reads.
                uint8_t next_addr = (txn_reg_addr + txn_byte_idx) & 0x7F;
                spi_get_hw(SPI_PORT)->dr = reg_map[next_addr];
            } else {
                // Write: store received data, handle special registers
                uint8_t write_addr = (txn_reg_addr + (txn_byte_idx - 1)) & 0x7F;
                uint8_t val = rx;

                if (write_addr == REG_PWR_MGMT_1 && (val & PWR_MGMT1_RESET)) {
                    // Soft reset: re-initialise register map
                    reg_map_init();
                } else {
                    reg_map[write_addr] = val;
                }
                spi_get_hw(SPI_PORT)->dr = 0x00;
            }
            txn_byte_idx++;
        }
    }
}

// ---------------------------------------------------------------------------
// CS GPIO interrupt — falling edge = transaction start, rising = end
// ---------------------------------------------------------------------------
static void cs_gpio_irq_handler(uint gpio, uint32_t events) {
    if (events & GPIO_IRQ_EDGE_FALL) {
        // Transaction starting.  Flush TX FIFO and prime with 0x00 so the
        // hardware doesn't underrun before we know the address.
        // (The real response is loaded in spi_rx_irq_handler once addr is known.)
        while (spi_is_writable(SPI_PORT)) {
            spi_get_hw(SPI_PORT)->dr = 0x00;
        }
        txn_byte_idx = 0;
        txn_active   = true;
    } else if (events & GPIO_IRQ_EDGE_RISE) {
        txn_active   = false;
        txn_byte_idx = 0;
        // Clear INT_STATUS data-ready (reading it clears it in real MPU-6000)
        reg_map[REG_INT_STATUS] |= INT_STATUS_DATA_RDY;
    }
}

// ---------------------------------------------------------------------------
// 1 kHz repeating timer — pulse the INT (data-ready) pin
// ---------------------------------------------------------------------------
static bool int_pin_timer_callback(struct repeating_timer *t) {
    (void)t;
    // Toggle INT high briefly — real MPU-6000 INT is latched or pulsed
    // depending on INT_PIN_CFG.  Pulse high for ~50 µs.
    gpio_put(PIN_INT, 1);
    busy_wait_us_32(50);
    gpio_put(PIN_INT, 0);
    return true;  // keep repeating
}

// ---------------------------------------------------------------------------
// USB command parser
// ---------------------------------------------------------------------------
static void process_command(const char *line) {
    char cmd[16];
    int a, b, c;

    if (sscanf(line, "%15s", cmd) != 1) {
        return;
    }

    if (strcmp(cmd, "gyro") == 0 && sscanf(line, "%*s %d %d %d", &a, &b, &c) == 3) {
        mutex_enter_blocking(&sensor_mutex);
        gyro_x = (int16_t)a;
        gyro_y = (int16_t)b;
        gyro_z = (int16_t)c;
        update_sensor_regs();
        mutex_exit(&sensor_mutex);
        printf("gyro set: %d %d %d\n", a, b, c);

    } else if (strcmp(cmd, "accel") == 0 && sscanf(line, "%*s %d %d %d", &a, &b, &c) == 3) {
        mutex_enter_blocking(&sensor_mutex);
        accel_x = (int16_t)a;
        accel_y = (int16_t)b;
        accel_z = (int16_t)c;
        update_sensor_regs();
        mutex_exit(&sensor_mutex);
        printf("accel set: %d %d %d\n", a, b, c);

    } else if (strcmp(cmd, "temp") == 0 && sscanf(line, "%*s %d", &a) == 1) {
        mutex_enter_blocking(&sensor_mutex);
        temp_raw = (int16_t)a;
        update_sensor_regs();
        mutex_exit(&sensor_mutex);
        printf("temp set: %d\n", a);

    } else if (strcmp(cmd, "raw") == 0 && sscanf(line, "%*s %x %x", &a, &b) == 2) {
        if (a >= 0 && a < 128) {
            reg_map[a] = (uint8_t)b;
            printf("reg[0x%02X] = 0x%02X\n", a, b);
        } else {
            printf("error: address 0x%02X out of range\n", a);
        }

    } else if (strcmp(cmd, "status") == 0) {
        printf("gyro:  %6d %6d %6d  (LSB, 16.4 LSB/dps @ ±2000dps)\n",
               gyro_x, gyro_y, gyro_z);
        printf("accel: %6d %6d %6d  (LSB, 2048 LSB/g @ ±16g)\n",
               accel_x, accel_y, accel_z);
        printf("temp:  %d raw\n", temp_raw);
        printf("WHO_AM_I: 0x%02X  PRODUCT_ID: 0x%02X\n",
               reg_map[REG_WHO_AM_I], reg_map[REG_PRODUCT_ID]);
        printf("INT_STATUS: 0x%02X  PWR_MGMT_1: 0x%02X\n",
               reg_map[REG_INT_STATUS], reg_map[REG_PWR_MGMT_1]);

    } else {
        printf("commands:\n");
        printf("  gyro X Y Z          set gyro LSBs (int16)\n");
        printf("  accel X Y Z         set accel LSBs (int16; accel_z=2048 = 1g)\n");
        printf("  temp T              set raw temp (int16)\n");
        printf("  raw ADDR VAL        write register (hex)\n");
        printf("  status              show current values\n");
    }
}

// ---------------------------------------------------------------------------
// main
// ---------------------------------------------------------------------------
int main(void) {
    stdio_init_all();

    // Short delay for USB to enumerate
    sleep_ms(1500);

    printf("\nMPU-6000 emulator starting...\n");

    // --- Register map ---
    mutex_init(&sensor_mutex);
    reg_map_init();

    // --- SPI slave setup ---
    // Baud rate is ignored in slave mode; set it anyway
    spi_init(SPI_PORT, 1000000);
    spi_set_slave(SPI_PORT, true);
    spi_set_format(SPI_PORT,
                   8,           // 8-bit words
                   SPI_CPOL_0,  // Mode 0: clock idles LOW
                   SPI_CPHA_0,  // data sampled on rising edge
                   SPI_MSB_FIRST);

    gpio_set_function(PIN_MISO, GPIO_FUNC_SPI);
    gpio_set_function(PIN_SCK,  GPIO_FUNC_SPI);
    gpio_set_function(PIN_MOSI, GPIO_FUNC_SPI);
    gpio_set_function(PIN_CS,   GPIO_FUNC_SPI);

    // Enable SPI RX interrupt (RXIM = bit 2 of IMSC)
    spi_get_hw(SPI_PORT)->imsc = SPI_SSPIMSC_RXIM_BITS;
    irq_set_exclusive_handler(SPI0_IRQ, spi_rx_irq_handler);
    irq_set_enabled(SPI0_IRQ, true);

    // --- CS GPIO edge interrupt for transaction framing ---
    // We monitor the raw GPIO even though it's also assigned to SPI function.
    gpio_set_irq_enabled_with_callback(PIN_CS,
        GPIO_IRQ_EDGE_FALL | GPIO_IRQ_EDGE_RISE,
        true,
        &cs_gpio_irq_handler);

    // --- INT pin (data-ready output) ---
    gpio_init(PIN_INT);
    gpio_set_dir(PIN_INT, GPIO_OUT);
    gpio_put(PIN_INT, 0);

    // 1 kHz repeating timer for data-ready pulses
    struct repeating_timer int_timer;
    add_repeating_timer_ms(-1, int_pin_timer_callback, NULL, &int_timer);

    printf("MPU-6000 emulator ready.\n");
    printf("WHO_AM_I=0x%02X, PRODUCT_ID=0x%02X\n",
           reg_map[REG_WHO_AM_I], reg_map[REG_PRODUCT_ID]);
    printf("accel_z=%d (1g), type 'status' for help.\n\n", accel_z);

    // --- Main loop: USB command interface ---
    char line_buf[64];
    int  line_pos = 0;

    while (true) {
        int ch = getchar_timeout_us(0);
        if (ch == PICO_ERROR_TIMEOUT) {
            tight_loop_contents();
            continue;
        }

        if (ch == '\r' || ch == '\n') {
            if (line_pos > 0) {
                line_buf[line_pos] = '\0';
                process_command(line_buf);
                line_pos = 0;
            }
        } else if (ch == '\b' || ch == 127) {
            if (line_pos > 0) {
                line_pos--;
            }
        } else if (line_pos < (int)sizeof(line_buf) - 1) {
            line_buf[line_pos++] = (char)ch;
        }
    }

    return 0;
}
