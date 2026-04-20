# M1: Build System & Empty Target — Reference

**Goal:** `cmake` configures, `make RP2350_PICO` produces a .uf2 binary (does nothing yet).
**BF reference:** `src/platform/PICO/mk/RP2350.mk` (584 LOC), `target/RP2350B/target.h`, `link/pico_rp2350_RunFromFLASH.ld`

> **About the search tool:** The `search.py` script at `~/Documents/planes/rpi_pico_2350_port/`
> searches thousands of pages of pre-project research — including a detailed implementation guide
> (PDF + MD, 3,000+ lines), Betaflight PR analysis, and a full Claude research session. Use it to
> quickly find relevant implementation details without reading everything.

## Quick Searches
```bash
cd ~/Documents/planes/rpi_pico_2350_port
./search.py CMake
./search.py --doc MD linker
./search.py --doc PDF boot
./search.py --doc PDF toolchain
./search.py --list-sections | grep -iE 'cmake|build|linker|toolchain'
```
Read sections: `offset=2003, limit=200` (CMake Configuration)

---

## Toolchain & CPU Flags

File: `cmake/cortex-m33.cmake`
```
-mthumb -mcpu=cortex-m33 -march=armv8-m.main+fp+dsp -mcmse -mfloat-abi=softfp
```
**Decision:** BF uses `softfp`; consider `hard` for INAV (better FP perf, but must match all libs).

## rp2350.cmake — Key Items

- **RP2350_DEFINITIONS:** `PICO_RP2350`, `PICO_BOARD="pico2"`, `PICO_COPY_TO_RAM=0`
- **SDK include dirs:** ~75 dirs (see `RP2350.mk:40-135`)
- **CRITICAL compile flag:** `-fno-builtin-memcpy` (`RP2350.mk:378`) — prevents unaligned `ldmia` crash
- **SDK objects:** MUST use `-O2 -ffast-math -fmerge-all-constants` WITHOUT LTO (`RP2350.mk:580-583`)
- **Linker wraps:** 37 pico_float + 50 pico_double + stdio + bit_ops (`RP2350.mk:136-252`)
  - These redirect math ops to RP2350's hardware DCP (Double Coprocessor) — significant speedup

```cmake
# cmake/rp2350_toolchain.cmake
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR ARM)
set(CMAKE_C_COMPILER arm-none-eabi-gcc)
set(CMAKE_CXX_COMPILER arm-none-eabi-g++)
set(CMAKE_ASM_COMPILER arm-none-eabi-gcc)
set(CMAKE_AR arm-none-eabi-ar)
set(CMAKE_OBJCOPY arm-none-eabi-objcopy)
set(CMAKE_OBJDUMP arm-none-eabi-objdump)
```

## Linker Script — Memory Layout

File: `src/main/target/link/rp2350_flash.ld`

```
FLASH:        0x10000000, 4032K   (code + rodata)
FLASH_CONFIG: 0x103F0000, 64K    (INAV settings — M4)
RAM:          0x20000000, 512K   (data + BSS + heap)
SCRATCH_X:    0x20080000, 4K     (core 1 stack)
SCRATCH_Y:    0x20081000, 4K     (core 0 stack)
```
- `.boot2` section: 256 bytes for boot stage 2
- Time-critical code → RAM via `> RAM AT> FLASH`
- `__config_start`/`__config_end` symbols for INAV config streamer

BF reference: `link/pico_rp2350_RunFromFLASH.ld` (346 LOC)

## Boot Stage 2

- `bs2_default_padded_checksummed.S` — must be exactly 256 bytes
- BF includes this pre-compiled; can also generate via Pico SDK
- Linker script reserves `.boot2` section for it

## Pico SDK Integration

- BF includes ~60 `.c`/`.S` SDK source files directly (not as a library)
- ~75 include directories from SDK
- SDK version: see `PICO/pico/version.h` in BF
- UF2 output: use `elf2uf2` tool from SDK or `uf2conv.py`

## platform.h Additions

Add `#elif defined(RP2350)` block to `src/main/platform.h`:
```c
typedef SPI0_Type     SPI_TypeDef;    // Pico SDK
typedef i2c_inst_t    I2C_TypeDef;
typedef uart_inst_t   USART_TypeDef;
typedef uint32_t      GPIO_TypeDef;   // single-port GPIO

#define DEFIO_PORT_PINS       48      // RP2350B (30 for RP2350A)
#define DEFIO_PORT_USED_COUNT 1       // single GPIO port
#define TASK_GYROPID_DESIRED_PERIOD 125  // 8kHz
```

## Target Directory: `src/main/target/RP2350_PICO/`

- `target.h`:
  - Enable: `USE_VCP`, `USE_SPI`, `USE_I2C`, `USE_ADC`, `USE_DSHOT`
  - Disable: `USE_SOFTSERIAL`, `USE_TRANSPONDER`, `USE_TIMER`, `USE_DSHOT_BITBANG`
  - PIO allocation: `PIO_DSHOT_INDEX 0`, `PIO_UART_INDEX 1`, `PIO_LEDSTRIP_INDEX 2`
  - Pico 2 onboard LED: GPIO 25
- `target.c` — system stubs (micros, millis, delay, systemReset — return 0 / no-op)
- `config.c` — empty default configuration
- `CMakeLists.txt` — `target_rp2350(RP2350_PICO)`

## Stub Drivers

Study SITL's approach for stub patterns. Key stubs needed:
- system, io, bus_spi, bus_i2c, dma, serial, adc, timer, exti, persistent

## Verification

```bash
cmake -DCMAKE_TOOLCHAIN_FILE=cmake/rp2350_toolchain.cmake -DTARGET=RP2350_PICO ..
make RP2350_PICO
# Should produce build/RP2350_PICO/inav_RP2350_PICO.uf2
```
