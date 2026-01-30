# BLE Connection Performance Analysis

**Date:** 2026-01-29
**Issue:** User reports BLE works after fix but is slower than version 8.0.1
**Branch:** fix/ble-byte-counter
**Commits:**
- `3742221de` - Fix BLE byte counter regression (original fix)
- `545ed921f` - Remove debug logging (performance optimization)

---

## Executive Summary

BLE connection fix successfully restored byte counter functionality, but user reports slower performance compared to version 8.0.1. Analysis reveals the fix changed from using an instance property array to an inherited base class array. After removing debug logging (4 console.log statements), the remaining performance difference may be due to prototype chain lookup overhead when accessing the inherited `_onReceiveListeners` array.

---

## Version Evolution

### Version 8.0.0 / 8.0.1 (Working, Fast)

**Architecture:**
```javascript
// Base class: connection.js
addOnReceiveListener(callback) {
    this._onReceiveListeners.push(callback);
    this.addOnReceiveCallback(callback);  // ← Delegated to subclass
}

// BLE subclass: connectionBle.js
constructor() {
    super();
    this._onCharateristicValueChangedListeners = [];  // ← Instance property
}

addOnReceiveCallback(callback) {
    this._onCharateristicValueChangedListeners.push(callback);
}

// Data receive handler:
this._handleOnCharateristicValueChanged = event => {
    // ... build buffer ...
    this._onCharateristicValueChangedListeners.forEach(listener => {
        listener(info);  // ← Calls instance property array
    });
};
```

**Data Flow:**
1. Byte counter registered via `addOnReceiveListener()`
2. Base class calls `this.addOnReceiveCallback(callback)`
3. BLE's `addOnReceiveCallback()` pushes to `_onCharateristicValueChangedListeners`
4. On BLE notification: loop through `_onCharateristicValueChangedListeners`
5. Byte counter increments ✅

**Performance Characteristics:**
- Direct instance property access
- Single forEach loop per notification
- No logging overhead
- No prototype chain lookup

---

### Version 9.0.0 (Broken)

**Change:**
```javascript
// Base class: connection.js
addOnReceiveListener(callback) {
    this._onReceiveListeners.push(callback);
    // ✗ REMOVED: this.addOnReceiveCallback(callback);
    // Comment: "Don't call addOnReceiveCallback here - it would duplicate the push"
}

// BLE subclass: unchanged
addOnReceiveCallback(callback) {
    this._onCharateristicValueChangedListeners.push(callback);
}

// Data receive handler: unchanged
this._onCharateristicValueChangedListeners.forEach(listener => {
    listener(info);
});
```

**What Broke:**
1. Byte counter registered via `addOnReceiveListener()`
2. Goes into `_onReceiveListeners` only (base class doesn't call `addOnReceiveCallback()`)
3. BLE notification handler only checks `_onCharateristicValueChangedListeners`
4. Byte counter never called ✗
5. MSP parser also never called ✗

**Root Cause:**
The "duplicate push" comment was MISLEADING. It assumed all subclasses pushed to the same array, but:
- Serial's `addOnReceiveCallback()` pushes to `_onReceiveListeners` ✓
- BLE's `addOnReceiveCallback()` pushes to `_onCharateristicValueChangedListeners` ✗

Removing the delegation broke BLE but not Serial.

---

### Our Fix - Current (Working, Slower?)

**Change:**
```javascript
// BLE subclass: connectionBle.js
constructor() {
    super();
    // ✗ REMOVED: this._onCharateristicValueChangedListeners = [];
    // Now uses inherited _onReceiveListeners from base class
}

addOnReceiveCallback(callback) {
    this._onReceiveListeners.push(callback);  // ← Uses inherited property
}

// Data receive handler:
this._handleOnCharateristicValueChanged = event => {
    // ... build buffer ...
    this._onReceiveListeners.forEach(listener => {  // ← Uses inherited property
        listener(info);
    });
};
```

**Data Flow:**
1. Byte counter registered via `addOnReceiveListener()`
2. Goes into `_onReceiveListeners` (base class array)
3. BLE's `addOnReceiveCallback()` also uses `_onReceiveListeners`
4. On BLE notification: loop through `_onReceiveListeners`
5. Byte counter increments ✅

**Architecture Changes:**
- Matches Serial implementation pattern ✓
- Uses inherited property instead of instance property
- Eliminated separate listener array
- Cleaner, more maintainable code ✓

---

## Performance Comparison

### Execution Path Per BLE Notification

| Aspect | 8.0.1 (Fast) | Our Fix (Slow?) |
|--------|--------------|-----------------|
| **Array accessed** | `this._onCharateristicValueChangedListeners` (instance) | `this._onReceiveListeners` (inherited) |
| **Property lookup** | Direct instance property | Prototype chain traversal |
| **forEach() calls** | 1 | 1 |
| **Listeners invoked** | Same (MSP parser + byte counter) | Same (MSP parser + byte counter) |
| **Debug logging** | None | 4 statements (REMOVED in `545ed921f`) |

### Code Overhead Analysis

**8.0.1 hot path:**
```javascript
this._onCharateristicValueChangedListeners.forEach(listener => {
    listener(info);
});
```
- Direct property access
- ~2-5 CPU cycles for property lookup

**Our fix hot path (after removing logging):**
```javascript
this._onReceiveListeners.forEach(listener => {
    listener(info);
});
```
- Inherited property access (prototype chain lookup)
- ~5-15 CPU cycles for property lookup (estimated)

**BLE notification frequency:**
- Typical MSP exchange: 3-5 notifications
- Configuration tab load: 50-100+ MSP requests
- Result: 150-500+ property lookups during normal use

---

## Potential Performance Bottlenecks

### 1. ✅ Debug Logging (FIXED)

**Before (`3742221de`):**
- 2 console.log() in hot path (every notification)
- 2 console.log() in cold path (listener add/remove)
- String interpolation + property access overhead
- Logging to DevTools console (1-10ms per call on Windows)

**After (`545ed921f`):**
- All debug logging removed
- Should restore to near 8.0.1 performance

**Status:** FIXED - User can test if this resolves slowness

---

### 2. ❓ Inherited Property Access (UNCONFIRMED)

**Hypothesis:**
Accessing `this._onReceiveListeners` (inherited from base class) is slower than accessing `this._onCharateristicValueChangedListeners` (instance property).

**JavaScript Property Lookup:**
```
Instance property:  this._prop          → 1 lookup (object itself)
Inherited property: this._prop          → 2 lookups (object, then prototype)
                                           ↑ Slower by ~2-3x in tight loops
```

**Evidence:**
- BLE notifications are high-frequency (20-byte chunks)
- Each notification requires property lookup
- Prototype chain adds overhead in V8/Chromium

**Counterpoint:**
- Modern JS engines (V8) optimize prototype access heavily
- Difference might be negligible (~nanoseconds per lookup)
- User reports noticeable slowness, not micro-optimization level

**Status:** UNCONFIRMED - Need to test if this is significant

---

### 3. ❓ forEach() Performance on Inherited Array (UNLIKELY)

**Hypothesis:**
Calling `forEach()` on an inherited array might be slower than on an instance array.

**Reality:**
- `forEach()` operates on the array object itself, not the property
- Once property lookup completes, forEach performance is identical
- This is almost certainly NOT the cause

**Status:** UNLIKELY

---

### 4. ❓ Other Changes Between 8.0.1 and Current (UNKNOWN)

**Unknown factors:**
- Other changes in connection handling code
- Changes in MSP processing
- Changes in base Connection class
- Electron/Chromium version differences

**Status:** REQUIRES INVESTIGATION

---

## Performance Testing Results

### After Debug Logging Removal

**Commit:** `545ed921f`
**Changes:** Removed 4 console.log() statements (9 lines)

**Expected improvement:**
- 2 console.log() removed from hot path → significant improvement
- 2 console.log() removed from cold path → minor improvement
- Should restore to near 8.0.1 performance

**Actual results:** PENDING USER TESTING

---

## Next Steps

### Immediate (User Testing)

1. **User tests current fix** (`545ed921f`)
   - If performance restored → logging was the issue ✓
   - If still slow → investigate inherited property overhead

### If Still Slow (Further Investigation)

2. **Benchmark inherited vs instance property access**
   ```javascript
   // Test 1: Instance property (8.0.1 pattern)
   class BleInstance {
       constructor() {
           this._listeners = [];
       }
       notify() {
           this._listeners.forEach(l => l());  // Direct lookup
       }
   }

   // Test 2: Inherited property (our fix pattern)
   class Base {
       constructor() {
           this._listeners = [];
       }
   }
   class BleInherited extends Base {
       notify() {
           this._listeners.forEach(l => l());  // Prototype lookup
       }
   }

   // Benchmark: 10,000 iterations
   ```

3. **Profile with Chrome DevTools**
   - Record performance during BLE connection
   - Compare 8.0.1 vs current fix
   - Identify specific hot spots

4. **Consider hybrid approach**
   - Keep fix architecture (use base class array)
   - Add instance property cache:
     ```javascript
     constructor() {
         super();
         this._listenerCache = this._onReceiveListeners;  // Cache reference
     }

     notify() {
         this._listenerCache.forEach(l => l());  // Direct access
     }
     ```

5. **Git bisect between 8.0.1 and 9.0.0**
   - Find exact commit that changed performance
   - May reveal other unrelated changes

---

## Recommendations

### Priority 1: User Testing
**Action:** User tests current code (`545ed921f`) after debug logging removal
**Timeline:** Immediate
**Expected outcome:** Should resolve slowness if logging was the primary cause

### Priority 2: If Still Slow
**Action:** Create minimal benchmark comparing instance vs inherited property access
**Timeline:** 1 hour
**Goal:** Quantify overhead of prototype chain lookup

### Priority 3: If Benchmark Shows Significant Overhead
**Action:** Implement instance property cache while preserving fix architecture
**Timeline:** 30 minutes
**Risk:** Low - adds caching layer, doesn't change logic

---

## Conclusion

**Primary suspect:** Debug logging (4 console.log statements in hot path)
- **Status:** FIXED in commit `545ed921f`
- **Confidence:** HIGH - logging in hot path causes 1-10ms overhead per call

**Secondary suspect:** Inherited property access (prototype chain lookup)
- **Status:** UNCONFIRMED - requires benchmarking
- **Confidence:** MEDIUM - plausible but V8 optimizes well

**Tertiary suspects:** Other changes between versions, Electron updates
- **Status:** UNKNOWN - requires git bisect investigation
- **Confidence:** LOW - less likely given targeted fix

**Next action:** Wait for user testing results on `545ed921f`

---

## Files Modified

| Commit | File | Changes | Purpose |
|--------|------|---------|---------|
| `3742221de` | `js/connection/connectionBle.js` | +18, -8 | Original fix with debug logging |
| `545ed921f` | `js/connection/connectionBle.js` | -9 | Remove debug logging |

**Net change:** +9 lines (fix overhead for using base class array)

---

**Last Updated:** 2026-01-29
**Status:** Awaiting user testing on performance after logging removal
