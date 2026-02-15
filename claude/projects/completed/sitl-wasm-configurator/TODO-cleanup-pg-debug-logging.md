# TODO: Clean Up Parameter Group Debug Logging

After WASM PG initialization testing is complete, remove debug logging added during profile pointer troubleshooting.

## Files to Clean Up

### 1. inav/src/main/target/SITL/wasm_pg_runtime.c

**Remove extensive console.log statements:**

- **Lines 39-43**: Remove wasmPgEnsureAllocated entry logging
  ```c
  // REMOVE:
  #ifdef __EMSCRIPTEN__
      #include <emscripten.h>
      EM_ASM({
          console.log('[WASM_PG] wasmPgEnsureAllocated called: pgn=' + $0);
      }, reg ? pgN(reg) : 0);
  #endif
  ```

- **Lines 47-49**: Remove NULL reg logging
  ```c
  // REMOVE:
  #ifdef __EMSCRIPTEN__
      EM_ASM({ console.error('[WASM_PG] reg is NULL!'); });
  #endif
  ```

- **Lines 56-60**: Remove profile status logging
  ```c
  // REMOVE:
  #ifdef __EMSCRIPTEN__
      EM_ASM({
          console.log('[WASM_PG] pgn=' + $0 + ' isProfile=' + $1 + ' address=' + $2 + ' ptr=' + $3);
      }, pgN(reg), isProfile, (int)reg->address, (int)reg->ptr);
  #endif
  ```

- **Lines 70-73**: Remove profile ptr validation warning
  ```c
  // REMOVE:
  #ifdef __EMSCRIPTEN__
      EM_ASM({
          console.warn('[WASM_PG] Profile address allocated but ptr invalid! Fixing... pgn=' + $0 + ' ptr=' + $1 + ' *ptr=' + $2);
      }, pgN(reg), (int)reg->ptr, reg->ptr ? (int)*reg->ptr : 0);
  #endif
  ```

- **Lines 89-92**: Remove ptr fix confirmation
  ```c
  // REMOVE:
  #ifdef __EMSCRIPTEN__
      EM_ASM({
          console.log('[WASM_PG] Fixed ptr: ' + $0 + ' -> ' + $1);
      }, (int)reg->ptr, (int)*reg->ptr);
  #endif
  ```

- **Lines 96-99**: Remove profile already allocated logging
  ```c
  // REMOVE:
  #ifdef __EMSCRIPTEN__
      EM_ASM({
          console.log('[WASM_PG] Profile already allocated, returning *reg->ptr, ptr=' + $0 + ' *ptr=' + $1);
      }, (int)reg->ptr, reg->ptr ? (int)*reg->ptr : 0);
  #endif
  ```

- **Lines 105-108**: Remove system already allocated logging
  ```c
  // REMOVE:
  #ifdef __EMSCRIPTEN__
      EM_ASM({
          console.log('[WASM_PG] System already allocated, returning address=' + $0);
      }, (int)reg->address);
  #endif
  ```

- **Lines 120-124**: Remove profile allocation logging
  ```c
  // REMOVE:
  #ifdef __EMSCRIPTEN__
      #include <emscripten.h>
      EM_ASM({
          console.log('[WASM_PG] Allocating profile PG: pgn=' + $0 + ' size=' + $1 + ' totalSize=' + $2);
      }, pgN(reg), regSize, totalSize);
  #endif
  ```

- **Lines 133-136**: Remove calloc failure logging
  ```c
  // REMOVE:
  #ifdef __EMSCRIPTEN__
      EM_ASM({
          console.error('[WASM_PG] calloc failed! storage=' + $0 + ' copyStorage=' + $1);
      }, (int)storage, (int)copyStorage);
  #endif
  ```

- **Lines 148-151**: Remove profile ptr check logging
  ```c
  // REMOVE:
  #ifdef __EMSCRIPTEN__
      EM_ASM({
          console.log('[WASM_PG] Profile ptr check: reg->ptr=' + $0);
      }, (int)reg->ptr);
  #endif
  ```

- **Lines 157-159**: Remove currentPtr allocation failure
  ```c
  // REMOVE:
  #ifdef __EMSCRIPTEN__
      EM_ASM({ console.error('[WASM_PG] Failed to allocate currentPtr!'); });
  #endif
  ```

- **Lines 164-167**: Remove allocated currentPtr logging
  ```c
  // REMOVE:
  #ifdef __EMSCRIPTEN__
      EM_ASM({
          console.log('[WASM_PG] Allocated new currentPtr: ' + $0 + ' -> ' + $1);
      }, (int)currentPtr, (int)storage);
  #endif
  ```

- **Lines 172-175**: Remove initialized ptr logging
  ```c
  // REMOVE:
  #ifdef __EMSCRIPTEN__
      EM_ASM({
          console.log('[WASM_PG] Initialized existing ptr: ' + $0 + ' -> ' + $1);
      }, (int)reg->ptr, (int)storage);
  #endif
  ```

**Keep only the functional code:**
- Pointer validation and repair logic (lines 69-94)
- Allocation logic for new PGs
- Reset template loading

### 2. inav/src/main/io/settings.c

**Lines 252-268**: Simplify settingGetValuePointer() error handling

Current:
```c
void *settingGetValuePointer(const setting_t *val)
{
    const pgRegistry_t *pg = pgFind(settingGetPgn(val));
#ifdef __EMSCRIPTEN__
    extern void* wasmPgEnsureAllocated(const pgRegistry_t *reg);
    if (!pg) {
        #include <emscripten.h>
        EM_ASM({
            console.error('[SETTINGS] pg is NULL for pgn=' + $0);
        }, settingGetPgn(val));
        return NULL;
    }
    void* result = wasmPgEnsureAllocated(pg);
    if (!result) {
        EM_ASM({
            console.error('[SETTINGS] settingGetValuePointer: allocation failed for pgn=' + $0);
        }, pgN(pg));
        return NULL;
    }
#endif
    if (!pg) {
        return NULL;
    }
    return pg->address + getValueOffset(val);
}
```

Replace with:
```c
void *settingGetValuePointer(const setting_t *val)
{
    const pgRegistry_t *pg = pgFind(settingGetPgn(val));
#ifdef __EMSCRIPTEN__
    extern void* wasmPgEnsureAllocated(const pgRegistry_t *reg);
    if (!pg) {
        return NULL;
    }
    void* result = wasmPgEnsureAllocated(pg);
    if (!result) {
        return NULL;
    }
#endif
    if (!pg) {
        return NULL;
    }
    return pg->address + getValueOffset(val);
}
```

**Lines 272-281**: Simplify settingGetCopyValuePointer() similarly

### 3. inav/src/main/fc/fc_msp.c

**Lines 3907-3918**: Remove debug logging from mspFcWriteSettingCommand()

Current:
```c
const void *ptr = settingGetValuePointer(setting);
#ifdef __EMSCRIPTEN__
if (!ptr) {
    #include <emscripten.h>
    char nameBuf[SETTING_MAX_NAME_LENGTH];
    settingGetName(setting, nameBuf);
    EM_ASM({
        console.error('[MSP] Setting value pointer is NULL: index=' + $0 + ' pgn=' + $1 + ' name=' + UTF8ToString($2));
    }, settingGetIndex(setting), settingGetPgn(setting), nameBuf);
    return false;
}
#endif
```

Replace with:
```c
const void *ptr = settingGetValuePointer(setting);
if (!ptr) {
    return false;
}
```

## When to Clean Up

- ✅ Profile pointer fix tested and verified
- ✅ Settings save/load working correctly
- ⏳ Before creating PR for Phase 6 Task 1 completion
- ⏳ After final integration testing

## Rationale

The debug logging was essential for:
1. Identifying the profile pointer initialization bug
2. Verifying the fix worked correctly
3. Understanding the PG initialization flow

But should be removed for production because:
- Reduces console noise in browser
- Improves performance (EM_ASM calls have overhead)
- Cleaner codebase for review
- Professional presentation

## Notes

- **Keep** the pointer validation and repair logic itself
- **Keep** NULL checks for robustness
- **Remove** only the console.log/console.error/console.warn statements
- **Consider** keeping one or two critical error logs if they help with future debugging

---

**Created:** 2026-02-02
**Status:** Ready for cleanup
**Related:** Phase 6 Task 1 completion
