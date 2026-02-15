# TODO: Clean Up Debug Logging

After WASM serial connection testing is complete, remove all debug logging added during development.

## Files to Clean Up

### 1. inav/src/main/target/SITL/serial_wasm.c
**Lines to remove/modify:**

- **Lines 49-57**: Remove debug logging from `notifySerialDataAvailable()`
  ```c
  // REMOVE these console.log calls:
  console.log('[WASM DEBUG] notifySerialDataAvailable called!');
  console.log('[WASM DEBUG] Calling Module.wasmSerialDataCallback');
  console.log('[WASM DEBUG] No callback registered!');
  ```
  Keep only:
  ```c
  EM_JS(void, notifySerialDataAvailable, (), {
      if (Module.wasmSerialDataCallback) {
          Module.wasmSerialDataCallback();
      }
  });
  ```

- **Lines 262-268**: Remove debug logging from `serialReadByte()`
  ```c
  // REMOVE:
  static int readCount = 0;
  ...
  readCount++;
  if (readCount <= 5) {
      EM_ASM({ ... });
  }
  ```

### 2. inav/src/main/target/SITL/wasm_msp_bridge.c
**Lines to remove:**

- **Lines 85-93**: Remove call counter and debug logging from `wasmMspProcess()`
  ```c
  // REMOVE:
  static int callCount = 0;
  static int lastRxBytes = 0;
  callCount++;

  if (callCount <= 3) {
      EM_ASM({ ... });
  }

  if (wasmMspPort == NULL) {
      EM_ASM({ console.log('[WASM DEBUG] Initializing WASM MSP port'); });
      wasmMspInit();
  }
  ```

- **Lines 100-111**: Remove RX/TX buffer status logging
  ```c
  // REMOVE all the buffer status logging code
  ```

### 3. inav-configurator/js/connection/connectionWasm.js
**Lines to remove:**

- **Line 196**: Remove `console.log('[WASM Connection] _onSerialDataAvailable called');`
- **Line 201**: Remove `console.log('[WASM Connection] Available bytes:', available);`
- **Line 203**: Remove `console.log('[WASM Connection] No bytes available, returning');`
- **Lines 216-217**: Remove byte reading logs
- **Line 227**: Remove `console.log('[WASM Connection] Listeners notified');`

Keep only the essential structure:
```javascript
_onSerialDataAvailable() {
    const module = this._loader.getModule();
    const available = module._serialAvailable();
    if (available <= 0) {
        return;
    }

    const responseBytes = new Uint8Array(available);
    for (let i = 0; i < available; i++) {
        const byte = module._serialReadByte();
        if (byte >= 0) {
            responseBytes[i] = byte;
        }
    }

    this._onReceiveListeners.forEach(listener => {
        listener({
            connectionId: this._connectionId,
            data: responseBytes.buffer
        });
    });
}
```

## When to Clean Up

- After Phase 6 Task 5 (Testing & Validation) is complete
- Before creating the final pull request
- When all WASM connection issues are resolved

## Notes

The debug logging was instrumental in identifying and fixing the connection flow, but should be removed for production to:
- Reduce console noise
- Improve performance (EM_ASM calls have overhead)
- Clean up the codebase

---
Created: 2026-02-01
Status: Pending (waiting for testing completion)
