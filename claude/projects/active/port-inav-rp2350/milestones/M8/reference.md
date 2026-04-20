# M8: Servo PWM & ADC — Battery Monitoring — Reference

**Goal:** Servos respond to sticks; configurator shows battery voltage.
**BF reference:** `pwm_servo_pico.c` (113 LOC), `adc_pico.c` (270 LOC)

> **About the search tool:** The `search.py` script at `~/Documents/planes/rpi_pico_2350_port/`
> searches thousands of pages of pre-project research — including a detailed implementation guide
> (PDF + MD, 3,000+ lines), Betaflight PR analysis, and a full Claude research session. Use it to
> quickly find relevant implementation details without reading everything.

## Quick Searches
```bash
cd ~/Documents/planes/rpi_pico_2350_port
./search.py ADC
./search.py --doc PDF servo
./search.py --doc PDF PWM
./search.py --doc MD ADC
./search.py --list-sections | grep -iE 'adc|servo|pwm|battery|voltage'
# Also check plan file for ADC/servo details:
grep -n -i 'adc\|servo\|pwm\|battery' ~/Documents/planes/rpi_pico_2350_port/inav_rp2350_port_plan.md | head -30
```
Read sections: `./search.py --doc MD ADC` → get line number → read that section

---

## Servo PWM (`pwm_servo_rp2350.c`)

Uses RP2350 **hardware PWM** (NOT PIO — different from motor DShot).
- 8 PWM slices × 2 channels = 16 possible servo outputs

### 50Hz Servo Timing
```c
// At 125 MHz system clock:
// prescaler = 64 → 125MHz / 64 = ~1.953 MHz tick
// TOP = 39063 → ~39063 / 1953 = ~20ms period (50Hz)
// ~1.953 counts/μs

void servoDevInit(const servoDevConfig_t *config) {
    for (int i = 0; i < servoCount; i++) {
        uint pin = servoPin[i];
        uint slice = pwm_gpio_to_slice_num(pin);
        uint channel = pwm_gpio_to_channel(pin);

        gpio_set_function(pin, GPIO_FUNC_PWM);

        pwm_config cfg = pwm_get_default_config();
        pwm_config_set_clkdiv(&cfg, 64.0f);   // prescaler
        pwm_config_set_wrap(&cfg, 39063);      // TOP → 50Hz
        pwm_init(slice, &cfg, true);
    }
}

void servoWrite(uint8_t servoIndex, uint16_t us) {
    // Clamp to valid servo range
    us = constrain(us, PWM_SERVO_MIN, PWM_SERVO_MAX);
    // Convert μs to PWM counts: counts = us * 1.953
    uint16_t counts = (uint16_t)(us * 1953 / 1000);
    uint pin = servoPin[servoIndex];
    pwm_set_gpio_level(pin, counts);
}
```

### Servo Range
```c
#define PWM_SERVO_MIN    750   // μs
#define PWM_SERVO_MAX   2250   // μs
// Standard: 1000-2000μs
```

---

## Non-DShot Motor PWM (same hardware)

BF `pwm_motor_pico.c` (216 LOC): same PWM slices for Oneshot125, Oneshot42, Multishot, Brushed, standard PWM.

```c
// pulseScale / pulseOffset mapping from INAV's 0-1000 throttle range to PWM counts
// Continuous update mode for brushed/PWM protocols
// (DShot is handled by PIO — M7)
```

---

## ADC Driver (`adc_rp2350.c`)

### Overview
- **Round-robin ADC with DMA ring buffer** (BF `adc_pico.c` pattern)
- RP2350A: ADC pins 26-29 (4 channels)
- RP2350B: ADC pins 40-47 (8 channels)
- Very slow sample rate (~10 samples/sec) — fine for battery monitoring

### Channels
```c
#define VBAT_ADC_CHANNEL    0   // ADC0 = GPIO26 (RP2350A) or GPIO40 (RP2350B)
#define CURRENT_ADC_CHANNEL 1   // ADC1 = GPIO27
#define RSSI_ADC_CHANNEL    2   // ADC2 = GPIO28
// Internal temp sensor = ADC4 (for power-of-2 padding if needed)
```

### DMA Ring Buffer (CRITICAL: power-of-2 trick)
```c
// DMA ring mode requires power-of-2 buffer size.
// If 3 channels → add internal temp sensor as 4th channel for 2^2 = 4 buffer size.
// (BF adc_pico.c padding trick)

#define ADC_CHANNEL_COUNT  3   // real channels
#define ADC_DMA_CHANNELS   4   // padded to power-of-2 (includes temp sensor)

static uint16_t adcDmaBuf[ADC_DMA_CHANNELS];  // power-of-2 size

void adcInit(void) {
    adc_init();

    // Enable channels
    adc_gpio_init(26 + VBAT_ADC_CHANNEL);
    adc_gpio_init(26 + CURRENT_ADC_CHANNEL);
    adc_gpio_init(26 + RSSI_ADC_CHANNEL);
    adc_set_temp_sensor_enabled(true);  // 4th "padding" channel

    // Round-robin: sample all 4 channels continuously
    adc_set_round_robin(0x0F);  // channels 0-3

    // VERY slow: ~10 samples/sec (battery doesn't need speed)
    adc_set_clkdiv(65535);     // BF adc_pico.c

    // DMA ring buffer (endless mode)
    uint dma_ch = dma_claim_unused_channel(true);
    dma_channel_config cfg = dma_channel_get_default_config(dma_ch);
    channel_config_set_transfer_data_size(&cfg, DMA_SIZE_16);
    channel_config_set_read_increment(&cfg, false);
    channel_config_set_write_increment(&cfg, true);
    channel_config_set_dreq(&cfg, DREQ_ADC);

    // Ring: write_size_bits = log2(ADC_DMA_CHANNELS * 2) = log2(8) = 3
    channel_config_set_ring(&cfg, true, 3);  // 2^3 = 8-byte ring

    dma_channel_configure(dma_ch, &cfg,
        adcDmaBuf,
        &adc_hw->result,
        0xFFFFFFFF,  // "endless" (-1 transfers, wraps in ring)
        true);       // start immediately

    adc_run(true);  // start free-running
}

// Read latest ADC value (always fresh from DMA)
uint16_t adcGetValue(uint8_t channel) {
    return adcDmaBuf[channel];
}
```

### Voltage Calculation
```c
// 12-bit ADC, 3.3V reference → 3.3V / 4096 = 0.000806V per count
// With voltage divider (e.g. 10k/1k for 3S battery):
// Adjust in INAV configurator: Battery → Scale

float getBatteryVoltage(void) {
    uint16_t raw = adcGetValue(VBAT_ADC_CHANNEL);
    return raw * (3.3f / 4096.0f) * VOLTAGE_DIVIDER_RATIO;
}
```

---

## CMake Libraries Needed

```cmake
target_link_libraries(RP2350_PICO
    hardware_pwm
    hardware_adc
    hardware_dma
)
```

---

## Verification

```bash
# Servo:
# - Connect oscilloscope to servo output pin
# - Should see 50Hz PWM, pulse width 1000-2000μs
# - Move stick → pulse width changes
# - Or connect real servo → should physically move

# Battery:
# Configurator → Power & Battery tab
# Connect battery via voltage divider → voltage reading appears
# Disconnect → reads 0 (or near-zero)
```

---

## Notes

- PWM slices are shared between servos and non-DShot motor PWM — manage slice assignment carefully
- Beeper (M12) also uses hardware PWM but at a different frequency
- ADC's `adcGetValue()` is always non-blocking (reads from DMA-cached buffer)
