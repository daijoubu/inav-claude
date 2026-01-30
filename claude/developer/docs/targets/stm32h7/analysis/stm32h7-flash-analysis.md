# STM32H7 Flash Write Behavior Analysis

## Documentation Examined

**File:** `~/Documents/planes/inavflight/claude/developer/docs/targets/stm32h7/stm32h743vi.pdf`
**Extracted Text:** `~/Documents/planes/inavflight/claude/developer/docs/targets/stm32h7/stm32h743vi.txt`
**Document:** STM32H742xI/G STM32H743xI/G Datasheet (DS12110 Rev 10)
**Date:** March 2023

## Key Findings from Datasheet

### 1. Read-While-Write Support (Page 1, Line 17)

**Direct Quote:**
> "Up to 2 Mbytes of flash memory with readwhile-write support"

**Location:** Features section, Memories subsection
**Significance:** STM32H7 explicitly supports read-while-write operations

### 2. Dual-Bank Architecture (Line 3836)

**Direct Quote:**
> "The flash memory is divided into two independent banks. Each bank is organized as follows:
> • A user flash memory block of 512 Kbytes (STM32H7xxxG) or 1-Mbyte (STM32H7xxxI) containing eight user sectors of 128 Kbytes (4 K flash memory words)"

**STM32H743xI Configuration:**
- **Bank 1:** 1 MB (8 sectors × 128 KB)
- **Bank 2:** 1 MB (8 sectors × 128 KB)
- **Total:** 2 MB flash

### 3. Cache Architecture (Line 3752)

**Direct Quote:**
> "Harvard architecture with L1 caches (16 Kbytes of I-cache and 16 Kbytes of D-cache)"

**Cache Configuration:**
- **Instruction Cache (I-Cache):** 16 KB
- **Data Cache (D-Cache):** 16 KB
- **Architecture:** Harvard (separate instruction/data paths)

### 4. Flash Timing Specifications (Table 53, Lines 33670-33800)

**Programming Time (tprog) - 266-bit flash word:**
- x8 parallelism: 290 µs (typ), 580 µs (max)
- x16 parallelism: 180 µs (typ), 360 µs (max)
- x32 parallelism: 130 µs (typ), 260 µs (max)
- x64 parallelism: 100 µs (typ), 200 µs (max)

**Sector Erase Time (tERASE128KB) - 128 KB sector:**
- x8 parallelism: 2.0 s (typ), 4.0 s (max)
- x16 parallelism: 1.8 s (typ), 3.6 s (max)
- x32 parallelism: 1.1 s (typ), 2.2 s (max)
- x64 parallelism: 1.0 s (typ), 2.0 s (max)

**Note:** These are the physical flash operation times, NOT necessarily CPU blocking times.

## Missing Information from Datasheet

The datasheet does NOT explicitly document:

1. ❌ Whether CPU execution is blocked during same-bank flash operations
2. ❌ Whether read-while-write works within the same bank or only across banks
3. ❌ Whether cache allows continued execution during flash writes
4. ❌ Specific behavior of HAL_FLASHEx_Erase() and HAL_FLASH_Program() blocking

**What we need:** STM32H7 Reference Manual (RM0433) - Flash Memory Controller section

## Code Analysis

### H7 Config Implementation (`config_streamer_stm32h7.c`)

```c
// Line 103: Sector erase
HAL_FLASHEx_Erase(&EraseInitStruct, &SECTORError);

// Line 120: Flash program
HAL_FLASH_Program(FLASH_TYPEPROGRAM_FLASHWORD, c->address, (uint32_t)buffer);
```

### F7 Config Implementation (`config_streamer_stm32f7.c`)

```c
// Line 126: Sector erase
HAL_FLASHEx_Erase(&EraseInitStruct, &SECTORError);

// Line 132: Flash program
HAL_FLASH_Program(FLASH_TYPEPROGRAM_WORD, c->address, (uint64_t)*buffer);
```

**Observation:** Both use identical HAL functions. The blocking behavior difference must be in the HAL implementation or hardware capability.

## Hypotheses (Require Reference Manual Verification)

### Hypothesis 1: Dual-Bank Read-While-Write
The H7's "read-while-write support" may allow:
- **CPU executes from Bank 1** → **Config write to Bank 2** → No blocking
- **CPU executes from Bank 2** → **Config write to Bank 1** → No blocking
- **CPU executes from Bank X** → **Config write to Bank X** → May block?

### Hypothesis 2: Cache Allows Continued Execution
The 16 KB I-Cache may buffer enough code to keep interrupts (DShot ISR) running during brief flash operations:
- **Flash word write:** 100-200 µs → May not block with cache
- **Flash sector erase:** 1-2 seconds → Likely blocks even with cache

### Hypothesis 3: Different HAL Implementation
The STM32H7 HAL may use:
- Non-blocking flash operations (polling-based)
- DMA-assisted flash writes
- Hardware that allows AXI bus access during flash operations

## Critical Questions for Reference Manual

1. **Does STM32H743xI support same-bank read-while-write?**
   - Need: RM0433 Section 4 (Flash Memory)

2. **Can CPU execute cached code during flash erase/program?**
   - Need: RM0433 Flash Controller behavior during operations

3. **Does HAL_FLASHEx_Erase() block CPU execution?**
   - Need: STM32H7 HAL source code or application note

4. **Where is config stored on H7 targets?**
   - If config is in Bank 2 and firmware in Bank 1 → True RWW
   - If config is in same bank as firmware → May block

## Conclusion (Preliminary)

**Based on datasheet alone:**

The STM32H743xI has architectural features that SHOULD prevent the ESC spinup issue:
1. ✅ Explicit "read-while-write support" 
2. ✅ Dual-bank architecture (2 × 1 MB)
3. ✅ L1 caches (16 KB I-Cache + 16 KB D-Cache)
4. ✅ Harvard architecture (separate I/D buses)

**However, we CANNOT definitively answer whether H7 should have the ESC spinup issue without:**
- STM32H7 Reference Manual (RM0433) Flash section
- Verification of which bank holds config on H7 targets
- HAL source code analysis of blocking behavior

**Recommendation:** Download RM0433 and search for:
- "read while write"
- "RWW"
- "flash program" + "CPU"
- "flash erase" + "blocking"
- Flash memory controller wait states during operations

## CRITICAL FINDING: Config Location on STM32H743xI

**Source:** `/home/raymorris/Documents/planes/inavflight/inav/src/main/target/link/stm32_flash_h743xi.ld`

**Memory Layout (Lines 35-39):**
```
0x08000000 to 0x081FFFFF 2048K full flash,
0x08000000 to 0x0801FFFF  128K isr vector, startup code,    // Sector 0
0x08020000 to 0x0803FFFF  128K config,                      // Sector 1
0x08040000 to 0x081FFFFF 1792K firmware,                    // Sectors 2-15
```

**Flash Bank Boundaries:**
- **Bank 1:** `0x08000000 - 0x080FFFFF` (1 MB, Sectors 0-7)
- **Bank 2:** `0x08100000 - 0x081FFFFF` (1 MB, Sectors 8-15)

**Config Storage Location:**
- **Address:** `0x08020000 - 0x0803FFFF` (128 KB)
- **Sector:** Sector 1 (128 KB sector)
- **Bank:** Bank 1 (SAME BANK AS FIRMWARE ENTRY POINT\!)

## Analysis: Same-Bank Flash Write

**The config is stored in Bank 1, which also contains:**
1. ISR vector table (`0x08000000 - 0x0801FFFF`, Sector 0)
2. Startup code (Sector 0)
3. First 896 KB of firmware (`0x08040000 - 0x080FFFFF`, Sectors 2-7)

**The firmware code executing during settings save is likely:**
- Running from Bank 1 (firmware starts at `0x08040000`)
- Cached in I-Cache (16 KB) and D-Cache (16 KB)

**Critical Question:** Does STM32H7 support **same-bank** read-while-write, or only **cross-bank** RWW?

### If Same-Bank RWW is Supported:
✅ CPU can execute from Bank 1 Sector 2+ while writing to Bank 1 Sector 1
✅ No ESC spinup issue expected
✅ Matches observed behavior (no bug on H7 hardware)

### If Only Cross-Bank RWW is Supported:
❌ CPU execution would block when writing to Bank 1 config
❌ ESC spinup issue SHOULD occur
❌ Does NOT match observed behavior

## Updated Conclusion

**The fact that we CANNOT reproduce the ESC spinup issue on STM32H743xI suggests:**

**EITHER:**
1. STM32H7 supports **same-bank read-while-write** (most likely)
2. The 16 KB I-Cache is sufficient to keep DShot ISR running during the ~1-2 second flash erase
3. HAL_FLASHEx_Erase() on H7 is implemented differently (non-blocking)

**Most Probable Explanation:**
The STM32H7's flash controller allows the CPU to continue executing cached code even during same-bank flash operations. The combination of:
- Harvard architecture (separate I/D buses)
- Large L1 caches (16 KB I-Cache + 16 KB D-Cache)
- Advanced flash controller with true RWW support

...allows uninterrupted code execution during flash writes.

**Authoritative Answer Requires:**
- STM32H7 Reference Manual (RM0433) Section 4: Embedded Flash Memory
- Specifically: Flash read operations while program/erase is ongoing
- ST Application Note AN5361 or similar covering H7 flash characteristics

