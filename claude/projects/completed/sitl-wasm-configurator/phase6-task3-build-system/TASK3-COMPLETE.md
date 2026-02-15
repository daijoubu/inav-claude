# Phase 6 Task 3: Build System Integration - COMPLETE

**Date:** 2026-02-01
**Status:** ✅ COMPLETE
**Time Spent:** ~1 hour

---

## Summary

Build system integration for WASM SITL binaries is complete. The WASM files are committed to the configurator repository and will be packaged automatically by Electron Forge.

---

## Solution: Check Files Into Git

**Decision:** WASM binaries (`SITL.wasm` and `SITL.elf`) are committed to the `inav-configurator` repository at `resources/sitl/`.

**Rationale:**
- Works for all build environments (local, CI, external contributors)
- No special build scripts needed in configurator repo
- Electron Forge automatically packages `resources/sitl/` via `extraResource` config
- Simple and reliable

**Trade-offs:**
- ✅ Works everywhere (CI, local, external builds)
- ✅ No dependencies on firmware repo structure
- ✅ No additional build steps required
- ⚠️ Binary files in git (~1.2 MB total)
- ⚠️ Manual update required when firmware changes

---

## Files Modified

### inav-configurator Repository

**Modified:**
- `forge.config.js` - Added `'resources/sitl'` to `extraResource` array

**Committed:** (already present, just updated)
- `resources/sitl/SITL.wasm` (936 KB)
- `resources/sitl/SITL.elf` (233 KB)

**No changes to:**
- `package.json` - No build scripts added (keeps configurator repo standalone)

### Developer Workspace (Internal Only)

**Created:**
- `claude/developer/scripts/build/copy-wasm-to-configurator.js` - Internal script for updating WASM files when firmware changes

---

## Build Process

### For Configurator Developers (No Firmware Changes)

Just use configurator normally - WASM files are already committed:

```bash
cd inav-configurator
npm install
npm start       # Development mode
npm run package # Package app
npm run make    # Create distributables
```

**WASM files are automatically included** via Electron Forge `extraResource` configuration.

### For Firmware Developers (Updating WASM)

When firmware changes and WASM needs updating:

1. **Build INAV firmware with WASM:**
   ```bash
   cd inav
   mkdir -p build_wasm && cd build_wasm
   cmake -DTOOLCHAIN=wasm -DSITL=ON ..
   cmake --build . --target SITL
   ```

2. **Copy WASM to configurator (internal script):**
   ```bash
   node claude/developer/scripts/build/copy-wasm-to-configurator.js
   ```

3. **Commit updated WASM files:**
   ```bash
   cd inav-configurator
   git add resources/sitl/SITL.wasm resources/sitl/SITL.elf
   git commit -m "Update WASM SITL binaries"
   ```

---

## Packaging Verification

**Electron Forge Configuration:**

```javascript
// forge.config.js
export default {
  packagerConfig: {
    extraResource: [
      'resources/public/sitl',  // Native SITL binaries (platform-specific)
      'resources/sitl'           // WASM SITL binaries (cross-platform) ← ADDED
    ],
  },
  // ...
}
```

**What happens during build:**
1. Electron Forge copies `resources/sitl/` to app package
2. At runtime, `wasm_sitl_loader.js` loads from `resources/sitl/SITL.wasm` and `SITL.elf`
3. Works in development (`npm start`) and production (packaged app)

---

## Runtime Path Resolution

**Development mode:**
```
resources/sitl/SITL.wasm  → inav-configurator/resources/sitl/SITL.wasm
```

**Production (packaged):**
```
resources/sitl/SITL.wasm  → <app-package>/resources/sitl/SITL.wasm
```

Electron Forge handles the path resolution automatically.

---

## Alternatives Considered

### Option 1: Build Script in Configurator Repo ❌

```javascript
// package.json
"prebuild": "npm run copy-wasm"
```

**Rejected because:**
- Assumes `../inav/build_wasm/bin/` exists
- Only works with our local directory structure
- Breaks for external contributors and CI
- Adds complexity to configurator repo

### Option 2: Download From GitHub Releases ❌

**Rejected because:**
- Requires release infrastructure
- Network dependency during build
- More complex error handling
- Overkill for 1.2 MB files

### Option 3: Check Into Git ✅ CHOSEN

**Advantages:**
- Works everywhere
- No build dependencies
- Simple and reliable
- Standard practice for pre-built binaries

---

## When to Update WASM Binaries

Update WASM binaries when:
- MSP protocol changes
- Parameter groups change (PG system)
- Serial interface changes
- SITL firmware features change
- Debugging firmware issues

**Not needed when:**
- Only configurator UI changes
- Only JavaScript/CSS changes
- Only documentation changes

---

## Task 3 Checklist

- [x] ~~Create `scripts/copy-wasm-binaries.js`~~ (moved to internal workspace)
- [x] ~~Add build hooks to `package.json`~~ (not needed - files committed)
- [x] Add `resources/sitl/` to `forge.config.js` extraResource
- [x] Verify WASM files exist in configurator repo
- [x] Create internal copy script for firmware developers
- [x] Test that files are packaged correctly
- [x] Document the process

---

## Next Steps

**Task 4: UI Integration** - Add "SITL (Browser)" connection button to configurator UI

---

## References

- Electron Forge packaging: `forge.config.js`
- WASM loader: `inav-configurator/js/wasm_sitl_loader.js`
- Internal copy script: `claude/developer/scripts/build/copy-wasm-to-configurator.js`
