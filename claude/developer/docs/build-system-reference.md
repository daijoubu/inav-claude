# Build System Reference

**Purpose:** Reference guide for understanding INAV's CMake build system, build types, compiler flags, and output artifacts.

**Last Updated:** 2026-01-14

---

## Table of Contents

1. [CMAKE_BUILD_TYPE Options](#cmake_build_type-options)
2. [How CMAKE_BUILD_TYPE Gets Set](#how-cmake_build_type-gets-set)
3. [Compiler Flags by Build Type](#compiler-flags-by-build-type)
4. [Optimization Levels by MCU Family](#optimization-levels-by-mcu-family)
5. [Output Files and Debug Information](#output-files-and-debug-information)
6. [Detecting Build Type from Artifacts](#detecting-build-type-from-artifacts)
7. [Practical Implications](#practical-implications)

---

## CMAKE_BUILD_TYPE Options

INAV supports three build types defined in `cmake/arm-none-eabi.cmake`:

| Build Type | Compiler Flags | Debug Symbols | Optimization | LTO | Use Case |
|------------|---------------|---------------|--------------|-----|----------|
| **Debug** | `-Og -g` | Yes (`-g`) | Minimal (`-Og`) | No | Active development, debugging |
| **Release** | `-DNDEBUG` | No | Target-specific (`-O2`/`-Os`) | Yes | Production releases |
| **RelWithDebInfo** | `-ggdb3 -DNDEBUG` | Yes (`-ggdb3`) | Target-specific (`-O2`/`-Os`) | Yes | **Default** - Optimized but debuggable |

### Key Differences:

**Debug:**
- Optimization: `-Og` (optimize for debugging experience)
- Asserts: Enabled (no `NDEBUG`)
- Debug symbols: Basic (`-g`)
- LTO: Disabled
- Binary size: Larger due to less optimization
- Build speed: Fastest

**Release:**
- Optimization: `-O2` or `-Os` (target-specific)
- Asserts: Disabled (`-DNDEBUG` defined)
- Debug symbols: None
- LTO: Enabled (Link-Time Optimization)
- Binary size: Smallest
- Build speed: Slowest (due to LTO)

**RelWithDebInfo (Default):**
- Optimization: `-O2` or `-Os` (target-specific)
- Asserts: Disabled (`-DNDEBUG` defined)
- Debug symbols: Enhanced (`-ggdb3` for GDB)
- LTO: Enabled
- Binary size: Same as Release
- Build speed: Slow (due to LTO)
- **Best of both worlds** - optimized firmware with debugging capability

---

## How CMAKE_BUILD_TYPE Gets Set

### Method 1: Default Value (Most Common)

From `cmake/arm-none-eabi.cmake:27-29`:
```cmake
if(CMAKE_BUILD_TYPE STREQUAL "")
    set(CMAKE_BUILD_TYPE RelWithDebInfo)
endif()
```

**Result:** If you don't specify, you get **RelWithDebInfo** (optimized + debug symbols).

### Method 2: Explicit Command Line

You can override at cmake configuration time:

```bash
cd inav/build
cmake -DCMAKE_BUILD_TYPE=Debug ..
make MATEKF405
```

Or:
```bash
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo ..
```

### Method 3: Current Build Scripts

**INAV's build scripts do NOT set CMAKE_BUILD_TYPE:**

- `build.sh` → Docker → `cmake/docker.sh` → `cmake -GNinja ..` (no flag = default)
- `claude/developer/scripts/build/build_sitl.sh` → `cmake -DSITL=ON ..` (no flag = default)

**Therefore:** Normal builds use the **default: RelWithDebInfo**

### Common Misconception:

**Q:** Does `make release` control optimization?
**A:** No! The `release` target just builds all hardware targets (excluding SKIP_RELEASES). The optimization is controlled by CMAKE_BUILD_TYPE.

From `cmake/main.cmake:139-141`:
```cmake
add_custom_target(release
    ${CMAKE_COMMAND} -E true
    DEPENDS ${release_targets}  # Just a list of targets to build
)
```

---

## Compiler Flags by Build Type

### Global Flags (All Build Types)

From `cmake/arm-none-eabi.cmake`:
```cmake
# Debug
set(arm_none_eabi_debug "-Og -g")

# Release
set(arm_none_eabi_release "-DNDEBUG")

# RelWithDebInfo
set(arm_none_eabi_relwithdebinfo "-ggdb3 ${arm_none_eabi_release}")
```

### Target-Specific Optimization (Release & RelWithDebInfo Only)

From `cmake/stm32.cmake:254-257`:
```cmake
if (IS_RELEASE_BUILD)
    target_compile_options(${elf_target} PRIVATE ${args_OPTIMIZATION})
    target_link_options(${elf_target} PRIVATE ${args_OPTIMIZATION})
endif()
```

Where `IS_RELEASE_BUILD` is defined in `CMakeLists.txt:71-73`:
```cmake
if(CMAKE_BUILD_TYPE STREQUAL "Release" OR CMAKE_BUILD_TYPE STREQUAL "RelWithDebInfo")
    set(IS_RELEASE_BUILD ON)
endif()
```

**Key point:** Both Release and RelWithDebInfo get optimization flags. Debug does NOT.

---

## Optimization Levels by MCU Family

Target-specific optimization is set per MCU family:

| MCU Family | Optimization Flag | Source File | Notes |
|------------|------------------|-------------|-------|
| **STM32F4** (most) | `-O2` | `cmake/stm32f4.cmake:95` | Default for F4 |
| **STM32F411** | `-Os` | `cmake/stm32f4.cmake:129` | Size-constrained (512KB flash) |
| **STM32F7** | `-O2` or `-Os` | `cmake/stm32f7.cmake:118-120` | Depends on flash size |
| **STM32H7** | `-O2` | `cmake/stm32h7.cmake:190` | Plenty of flash |
| **AT32F4** | `-O2` | `cmake/at32f4.cmake:69` | Performance-focused |

### F7 Logic Example:

From `cmake/stm32f7.cmake:118-120`:
```cmake
if(${size_letter} STREQUAL "G")
    set(opt -O2)  # 1MB flash - use speed optimization
else()
    set(opt -Os)  # <1MB flash - use size optimization
endif()
```

---

## Output Files and Debug Information

### Files Generated Per Target

For example, building `MATEKF405`:

```
inav/build/
├── obj/main/
│   ├── MATEKF405.elf          # ELF binary with debug sections
│   └── MATEKF405.map          # Linker map file
└── inav_9.0.0_MATEKF405.hex   # Intel HEX for flashing
└── inav_9.0.0_MATEKF405.bin   # Raw binary for flashing
```

### File Details:

#### 1. `.elf` File (ELF Binary)

**Location:** `build/obj/main/<TARGET>.elf`

**Size:**
- Debug: ~12 MB (with debug sections)
- Release: ~2 MB (no debug sections, but still ELF format)
- RelWithDebInfo: ~12 MB (with debug sections)

**Contains:**
- Loadable sections: `.text`, `.rodata`, `.data`, `.bss`
- Debug sections (if Debug/RelWithDebInfo): `.debug_info`, `.debug_line`, `.debug_frame`, etc.
- Symbol table
- Section metadata

**Used for:**
- GDB debugging
- Extracting symbols with `arm-none-eabi-nm`
- Disassembly with `arm-none-eabi-objdump`
- Creating .hex/.bin files via `objcopy`

**Conversion commands:**
```bash
# .elf → .hex
arm-none-eabi-objcopy -Oihex --set-start 0x08000000 input.elf output.hex

# .elf → .bin
arm-none-eabi-objcopy -Obinary input.elf output.bin
```

#### 2. `.map` File (Linker Map)

**Location:** `build/obj/main/<TARGET>.map`

**Generated via:** `-Wl,-Map,${map}` linker flag (see `cmake/stm32.cmake:221`)

**Size:** ~500 KB - 2 MB (text file)

**Contains:**
- Memory layout and section sizes
- **Symbol names and addresses** (functions, variables)
- Cross-reference information
- Total memory usage statistics

**Example content:**
```
Memory Map of the image

  Image Entry point : 0x08000c1d

  Global Symbols

  Symbol Name                    Value     Type    Size
  pidController                  0x08015678 Code   1234
  navigationPosHold              0x08016543 Code    456
```

**Used for:**
- Finding function addresses (human-readable)
- Analyzing memory usage
- Debugging without full debug symbols
- Understanding code layout

**Always generated:** Yes, regardless of CMAKE_BUILD_TYPE

#### 3. `.hex` File (Intel HEX Format)

**Location:** `build/inav_<version>_<TARGET>.hex`

**Size:** ~400 KB

**Contains:**
- **Only loadable sections** from .elf file
- Text representation of memory addresses + data
- NO debug sections
- NO symbol information

**Debug sections removed by:** `objcopy` automatically excludes non-allocatable sections

**Used for:**
- Flashing to flight controller
- Bootloader updates
- Combined bootloader+firmware images

#### 4. `.bin` File (Raw Binary)

**Location:** `build/inav_<version>_<TARGET>.bin`

**Size:** ~200 KB

**Contains:**
- Raw binary data of loadable sections
- NO debug sections
- NO symbol information
- NO address information (just contiguous data)

**Used for:**
- Direct DFU flashing
- Bootloader-less flashing
- Firmware analysis

---

## Detecting Build Type from Artifacts

### Summary Table:

| Method | Works With | Reliability | Information Gained |
|--------|-----------|-------------|-------------------|
| Check .elf debug sections | `.elf` only | High | Debug/RelWithDebInfo vs Release |
| Compare .elf size | `.elf` only | Medium | Rough estimate |
| Disassembly analysis | `.elf`, `.hex`, `.bin` | Medium | Optimization level (not build type) |
| Search for asserts | `.elf`, `.hex`, `.bin` | Medium | Debug vs Release/RelWithDebInfo |
| Check CMakeCache.txt | Build directory | High | Exact CMAKE_BUILD_TYPE |

### Method 1: Check .elf Debug Sections

```bash
# List sections in .elf file
arm-none-eabi-readelf -S obj/main/MATEKF405.elf | grep debug

# If you see .debug_* sections → Debug or RelWithDebInfo
# If no debug sections → Release
```

### Method 2: Compare .elf File Size

```bash
ls -lh obj/main/MATEKF405.elf

# ~12 MB → Debug or RelWithDebInfo (has debug sections)
# ~2 MB  → Release (no debug sections)
```

**Note:** .hex and .bin files are the same size regardless of build type (debug sections always stripped).

### Method 3: Disassembly Analysis

```bash
arm-none-eabi-objdump -d obj/main/MATEKF405.elf | less

# Look for optimization patterns:
# - Optimized: function inlining, loop unrolling, fewer instructions
# - Debug: clear stack frames, no inlining, 1:1 C-to-assembly mapping
```

**Limitation:** Can tell optimization level, but can't distinguish Release from RelWithDebInfo.

### Method 4: Search for Assert Strings

```bash
strings inav_9.0.0_MATEKF405.hex | grep -i assert

# Asserts present → Debug build (no NDEBUG)
# Asserts absent → Release or RelWithDebInfo (NDEBUG defined)
```

**Limitation:** Only distinguishes Debug from Release/RelWithDebInfo.

### Method 5: Check Build Directory (Most Reliable)

```bash
grep CMAKE_BUILD_TYPE inav/build/CMakeCache.txt

# Output: CMAKE_BUILD_TYPE:STRING=RelWithDebInfo
```

**Best method** if you have access to the build directory.

---

## Practical Implications

### For Development:

**Use Debug when:**
- Actively debugging with GDB
- Need to step through code line-by-line
- Variables need to be inspectable (not optimized away)
- Build speed matters more than execution speed

**Use RelWithDebInfo when (Default):**
- Normal development and testing
- Want optimized performance but may need to debug crashes
- Testing optimization-related issues
- Creating pre-release builds

**Use Release when:**
- Final production releases
- Size optimization is critical
- You won't need to debug this specific binary

### For Debugging:

**You NEED the .elf file to:**
- Use GDB for debugging
- Get source line numbers from addresses
- See variable names and types
- Step through source code

**You can use .map files to:**
- Find function addresses (without GDB)
- Analyze memory layout
- Get symbol names (but not types or line numbers)
- Debug production issues with limited info

**You CANNOT debug with only .hex/.bin:**
- These files have no debug information
- No symbol names, no line numbers, no types
- Can only disassemble raw instructions

### For Releases:

**Keep these files for each release:**
- ✅ `.elf` file (for post-release debugging)
- ✅ `.map` file (for analyzing crash addresses)
- ✅ `.hex` file (what users flash)
- ❌ Can discard build artifacts and object files

**Why keep .elf files:**
- Users report crashes with addresses from crash dumps
- You can map addresses back to source code using saved .elf
- Can debug issues months after release

**Storage example:**
```
releases/
└── 9.0.0/
    ├── binaries/
    │   └── inav_9.0.0_MATEKF405.hex  (for users)
    └── debug/
        ├── MATEKF405.elf              (for debugging)
        └── MATEKF405.map              (for quick lookups)
```

---

## Quick Reference

### Check Current Build Type:

```bash
grep CMAKE_BUILD_TYPE inav/build/CMakeCache.txt
```

### Change Build Type:

```bash
cd inav/build
cmake -DCMAKE_BUILD_TYPE=Debug ..
make clean
make <TARGET>
```

### Build Without Optimization:

```bash
cd inav/build
cmake -DCMAKE_BUILD_TYPE=Debug ..
make MATEKF405
```

### Build Optimized With Debug Symbols (Default):

```bash
cd inav/build
# No CMAKE_BUILD_TYPE specified = RelWithDebInfo
cmake ..
make MATEKF405
```

### Check If .elf Has Debug Symbols:

```bash
arm-none-eabi-readelf -S obj/main/MATEKF405.elf | grep debug
```

### Extract Symbol Address:

```bash
# From .elf file
arm-none-eabi-nm obj/main/MATEKF405.elf | grep pidController

# From .map file (human-readable)
grep pidController obj/main/MATEKF405.map
```

---

## Related Documentation

- [inav-builder agent](.claude/agents/inav-builder.md) - Build system automation
- [GCC Preprocessing Techniques](debugging/gcc-preprocessing-techniques.md) - Advanced compilation techniques
- [CRITICAL-BEFORE-CODE.md](../guides/CRITICAL-BEFORE-CODE.md) - Build workflow checklist

---

## Notes and Discoveries

### Link-Time Optimization (LTO)

From `cmake/main.cmake:86-90`:
```cmake
if(IS_RELEASE_BUILD AND NOT (CMAKE_HOST_APPLE AND SITL))
    set_target_properties(${exe} PROPERTIES
        INTERPROCEDURAL_OPTIMIZATION ON
    )
endif()
```

LTO is enabled for Release and RelWithDebInfo builds (except macOS SITL), providing additional size and performance optimizations by allowing the linker to optimize across compilation units.

### Debug Symbol Formats

- `-g`: Basic debug information (DWARF 2)
- `-ggdb3`: Enhanced debug information specifically for GDB (includes macro definitions)

RelWithDebInfo uses `-ggdb3` for the best debugging experience with GDB.

---

**Remember:** The default build (RelWithDebInfo) gives you optimized firmware that you can still debug. Keep the .elf files!
