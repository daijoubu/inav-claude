# FINDINGS: CAN Driver Circular Buffer Investigation

**Date:** 2026-02-15
**Project:** investigate-can-circular-buffer

## Phase 1: Find Implementations

### 1. STM32F7 CAN Driver Buffer

**File:** `inav/src/main/drivers/dronecan/libcanard/canard_stm32f7xx_driver.c`

A custom circular buffer implementation for receiving CAN frames:
- Size: 32 messages (`RX_BUFFER_SIZE`)
- Structure: `struct RxBuffer_t` with writeIndex, readIndex, and array of CanRxMsgTypeDef

### 2. INAV Common Circular Buffer Library

**Files:**
- Header: `inav/src/main/common/circular_queue.h`
- Implementation: `inav/src/main/common/circular_queue.c`

A generic circular buffer for arbitrary element types.

### 3. Other Usages in Codebase

The common circular queue is used in:
- `telemetry/smartport.c` - Telemetry data
- `telemetry/crsf.c` - CRSF protocol
- `fc/serial.c` - Serial communication
- Various other places needing queue functionality

## Phase 2: Document Current CAN Buffer

### Structure

```c
// From canard_stm32f7xx_driver.c
#define RX_BUFFER_SIZE 32

static struct RxBuffer_t {
    uint8_t writeIndex;
    uint8_t readIndex;
    CanRxMsgTypeDef rxMsg[RX_BUFFER_SIZE];
} RxBuffer;
```

### API

| Function | Description |
|----------|-------------|
| `rxBufferPushFrame()` | Add frame to buffer, returns -1 if full |
| `rxBufferPopFrame()` | Remove frame from buffer, returns -1 if empty |
| `rxBufferNumMessages()` | Count messages in buffer |

### Thread Safety

- **No explicit thread safety:** Uses simple index-based approach
- **Not volatile:** Indices are not marked volatile
- **No critical sections:** Direct read/write without protection
- **Note:** CAN interrupt (RX) pushes, main loop pops - potential race condition

### Element Size

- Fixed to `sizeof(CanRxMsgTypeDef)` - not generic

## Phase 3: Document Library Buffer

### Structure

```c
// From circular_queue.h
typedef struct circularBuffer_s {
    size_t head;
    size_t tail;
    size_t bufferSize;      // Total buffer bytes
    uint8_t * buffer;       // Pointer to data
    size_t elementSize;     // Size of each element
    size_t size;            // Count of elements
} circularBuffer_t;
```

### API

| Function | Description |
|----------|-------------|
| `circularBufferInit()` | Initialize buffer with memory |
| `circularBufferPushElement()` | Add element, drops if full |
| `circularBufferPopHead()` | Remove head element |
| `circularBufferIsFull()` | Check if full |
| `circularBufferIsEmpty()` | Check if empty |
| `circularBufferCountElements()` | Get element count |

### Thread Safety

- **No explicit thread safety:** Uses size counter
- **Not volatile:** Fields are not marked volatile
- **No critical sections:** Direct read/write without protection
- **Size tracking:** Maintains explicit count (safer than index comparison)

### Element Size

- **Generic:** Handles any element size via `elementSize` field

## Phase 4: Compare and Recommend

### Comparison Table

| Aspect | CAN Driver Buffer | Library Buffer |
|--------|------------------|----------------|
| Generic | No (fixed to CanRxMsgTypeDef) | Yes (any element type) |
| Size tracking | Index comparison | Explicit count field |
| Memory | Static array | Dynamic (caller provides) |
| Thread safety | None | None |
| Volatile | No | No |
| Overflow behavior | Returns error | Drops silently |
| API complexity | Simple | Simple |
| Unit tests | None | Unknown |

### Compatibility Issues

1. **Different approach:** CAN driver uses writeIndex/readIndex directly on array, library uses byte offsets
2. **Memory model:** CAN driver allocates internally, library requires external buffer
3. **Return values:** CAN driver returns -1 on full/empty, library checks IsFull/IsEmpty

### Switching Effort

**Low - but not recommended:**
- Replace `struct RxBuffer_t` with `circularBuffer_t`
- Replace push/pop functions with library equivalents
- Allocate `CanRxMsgTypeDef[32]` buffer externally
- ~30-60 minutes of work

### Recommendation: **Keep Current Implementation**

Reasons to keep the current CAN driver buffer:

1. **Simplicity:** The current implementation is simple and works
2. **Size known:** We know exactly what we're storing (CanRxMsgTypeDef)
3. **No benefit:** Switching to the library provides no real advantage
4. **Risk:** Changing working code introduces risk for no gain
5. **Performance:** Current implementation is efficient (direct array access)

The library buffer is better suited for:
- Variable-length data
- Dynamic buffer sizes
- Cases where the same code handles different data types

### Minor Improvements (Optional)

If desired, minor improvements to the CAN buffer:
1. Add `volatile` to indices for compiler optimization safety
2. Add critical section protection if needed
3. Use library for consistency (low priority)

## Summary

The CAN driver uses a simple custom circular buffer, while INAV has a generic circular queue library. Both have similar limitations (no thread safety). The recommendation is to **keep the current implementation** as it works well and switching provides no meaningful benefit.

The main difference is the CAN driver is specialized for CAN frames while the library is generic. For a specialized use case like this, the custom implementation is appropriate.
