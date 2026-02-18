# WASM Build Procedure

**Last Updated:** 2026-02-01
**Purpose:** Document the correct procedure for building SITL WASM to avoid trial-and-error

---

## Successful Build Commands

### Using inav-builder Agent (Recommended)

```
Use the Task tool with subagent_type="inav-builder"
Prompt: "Build SITL WASM target"
```

The agent will automatically use the correct cmake flags and handle the build process.

### Manual Build (for reference)

```bash
cd inav/build_wasm
cmake -DTOOLCHAIN=wasm -DSITL=ON ..
cmake --build . --target SITL -j4
```

**Output files:**
- `build_wasm/bin/SITL.wasm` (~938 KB)
- `build_wasm/bin/SITL.elf` (~236 KB)

---

## Deployment to Configurator

```bash
cp inav/build_wasm/bin/SITL.wasm inav-configurator/resources/sitl/
cp inav/build_wasm/bin/SITL.elf inav-configurator/resources/sitl/
```

---

## Key Build Parameters

### ✅ Correct Flags

- `-DTOOLCHAIN=wasm` - Specifies WebAssembly toolchain
- `-DSITL=ON` - Enables Software-In-The-Loop simulator target

### ❌ Common Mistakes to Avoid

- **DON'T** use `emcmake cmake` directly (toolchain detection handles this)
- **DON'T** use `-DEMSCRIPTEN=ON` (unused by project)
- **DON'T** use `-DSITL_BUILD=ON` (correct flag is `-DSITL=ON`)
- **DON'T** try `rm -rf build_wasm` (requires manual approval, usually unnecessary)

---

## Clean Build (if needed)

### Option 1: CMake clean (preferred)
```bash
cd inav/build_wasm
cmake --build . --target clean
```

### Option 2: Find-based cleanup (avoids rm -rf approval)
```bash
cd inav
find build_wasm -type f -delete
find build_wasm -type d -delete
```

### Option 3: Request manual approval
Ask user to approve `rm -rf inav/build_wasm` if clean rebuild required.

---

## Build Time Expectations

- **Incremental build:** ~30-60 seconds
- **Full build:** ~2-3 minutes
- **Clean build:** ~3-5 minutes

---

## Verification After Build

Check that source modifications are compiled:

```bash
# Compare timestamps
stat -c "%y %n" inav/src/main/target/SITL/serial_wasm.c
stat -c "%y %n" inav/build_wasm/bin/SITL.wasm

# WASM timestamp should be AFTER source file timestamp
```

---

## Recent Successful Builds

| Date | Time | Purpose | Result |
|------|------|---------|--------|
| 2026-02-01 | 13:13 | Deadlock fix (wasmSerialIsTransmitBufferEmpty) | ✅ Success |
| 2026-02-01 | 12:25 | Debug logging added | ✅ Success |
| 2026-01-31 | - | Phase 6 Task 1 completion | ✅ Success |

---

## Common Build Issues

### Issue: "emcmake: command not found"

**Cause:** Trying to use emcmake directly
**Solution:** Use `-DTOOLCHAIN=wasm` flag instead, or use inav-builder agent

### Issue: CMake says "EMSCRIPTEN unused"

**Cause:** Using `-DEMSCRIPTEN=ON` flag
**Solution:** Use `-DTOOLCHAIN=wasm` instead

### Issue: Build files already exist

**Cause:** Reusing build directory
**Solution:** This is fine! CMake will do incremental build. Only clean if needed.

---

## Notes for Future Development

1. **The inav-builder agent knows the correct procedure** - prefer using it over manual builds
2. **Incremental builds are fast** - no need to clean unless troubleshooting
3. **Always verify timestamps** - ensure source changes are compiled into binary
4. **WASM binaries are ~1MB** - reasonable for browser deployment
5. **Debug builds include console.log** - remember to clean up before PR

---

## Debugging WASM in Browser

**IMPORTANT:** WASM builds ALWAYS include debug symbols (`-g` and `-gsource-map` flags) to enable browser debugging.

### Why Debug Symbols Are Essential

Browser DevTools can show exactly which C source line crashes, making debugging much faster than guessing from memory addresses.

### Output Files

When building WASM SITL, you get:
- **SITL.wasm** (~940 KB) - Binary with debug symbols
- **SITL.elf** (~236 KB) - JavaScript glue code
- **SITL.wasm.map** (~549 KB) - Source map for line-level debugging

### Using Browser DevTools

1. **Open DevTools BEFORE connecting**
   - Press F12 (or Ctrl+Shift+I / Cmd+Option+I)

2. **View Source Files**
   - Go to **Sources** tab
   - Navigate to SITL.wasm in file tree
   - You'll see actual C source files with line numbers

3. **Set Breakpoints**
   - Click line numbers to set breakpoints
   - Execution will pause at that line
   - Inspect variables and call stack

4. **When Code Crashes**
   - Console shows exact C file and line number
   - Example: `at wasm_pg_runtime.c:79:9`
   - Full call stack with function names
   - No more guessing from `0x5c2aa` offsets!

### Example Stack Trace

**Without debug symbols:**
```
Uncaught RuntimeError: memory access out of bounds
    at SITL.wasm:0x5c2aa
```

**With debug symbols:**
```
Uncaught RuntimeError: memory access out of bounds
    at streambuf.c:79:9
    at fc_msp.c:3907:5
    at mspFcProcessCommand (fc_msp.c:4112:16)
```

### Performance Impact

Debug symbols add ~500 KB to binary size but DO NOT impact runtime performance. Always keep them enabled during development.

---

## Related Documentation

- Build system: `claude/projects/active/sitl-wasm-configurator/02-build-system/README.md`
- CMake configuration: `inav/cmake/sitl.cmake`
- WASM integration: `claude/projects/active/sitl-wasm-configurator/summary.md`
