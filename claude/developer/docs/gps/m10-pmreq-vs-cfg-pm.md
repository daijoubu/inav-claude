# UBX-RXM-PMREQ vs CFG-PM: Understanding Power Management

**Source:** u-blox M10 SPG 5.10 Interface Description (UBX-21035062-R03)
**Page References:** Page 116 (UBX-RXM-PMREQ), Page 147 (CFG-PM)

---

## Two Different Power Management Mechanisms

The M10 has two different ways to interact with power management:

### 1. UBX-RXM-PMREQ (Command Message)
**Type:** Runtime command
**Class:** 0x02 (RXM - Receiver Manager)
**ID:** 0x41
**Page:** 116

**Purpose:** Request an immediate power management action

**Use Case:**
- Put receiver into backup mode (sleep)
- Request specific power save states
- Triggered by external events or application logic

**Payload:**
- `version` (U1): Message version (0x00)
- `duration` (U4): Duration in milliseconds
- `flags` (X4): Task flags
  - bit 1: `backup` - Set to 1 to put receiver into backup mode
  - bit 2: `force` - Force the action

**Example Usage:**
```c
// Put receiver to sleep for 10 seconds
UBX-RXM-PMREQ:
  version = 0
  duration = 10000 (ms)
  flags.backup = 1
```

**When to use:** Shutting down the receiver to save power, not for performance tuning.

---

### 2. CFG-PM (Configuration Settings)
**Type:** Persistent configuration
**Configuration Group:** CFG-PM
**Page:** 147

**Purpose:** Configure ongoing power management behavior

**Use Case:**
- Set default power mode (FULL vs power save modes)
- Configure cyclic tracking parameters
- Define power save mode thresholds

**Key Configuration: CFG-PM-OPERATEMODE**
- Key ID: 0x20d00001 (E1)
- Values:
  - 0 = FULL (normal operation, no power save)
  - 1 = PSMOO (ON/OFF operation)
  - 2 = PSMCT (cyclic tracking)

**Example Usage:**
```c
// Configure receiver to always run in full power mode
UBX-CFG-VALSET:
  key = 0x20d00001 (CFG-PM-OPERATEMODE)
  value = 0 (FULL)
```

**When to use:** Setting the default operating mode for maximum performance.

---

## Key Differences

| Aspect | UBX-RXM-PMREQ | CFG-PM |
|--------|---------------|--------|
| **Type** | Runtime command | Configuration setting |
| **Persistence** | Temporary action | Persistent (saved to flash) |
| **Purpose** | Put receiver to sleep NOW | Define normal operating mode |
| **Frequency** | On-demand as needed | Set once, applies always |
| **Class** | 0x02 (RXM) | 0x06 (CFG) |
| **Method** | Direct message | Via VALSET/VALGET |

---

## Relevance to INAV GPS Configuration

### UBX-RXM-PMREQ: ❌ Not Relevant

**Reason:** INAV wants the GPS receiver to stay awake and active at all times during flight. We never want to put it into backup mode.

**Potential use:** Could be used for ground power saving when aircraft is disarmed, but not currently implemented.

---

### CFG-PM-OPERATEMODE: ✅ Potentially Relevant

**Reason:** Ensures GPS runs in FULL power mode for maximum performance.

**Current status:**
- Default is FULL (0) according to documentation
- INAV does not explicitly set this
- M10 likely already running in FULL mode

**Action needed:**
- ⚠️ Could add explicit CFG-PM-OPERATEMODE = FULL configuration as defensive measure
- ✅ Not strictly necessary if defaults are correct
- ✅ Would ensure consistent behavior across different M10 variants/firmware

---

## Recommendation for INAV

### Option 1: Trust the Default (Current Behavior)
- Assume M10 ships with CFG-PM-OPERATEMODE = FULL
- Don't configure it explicitly
- **Pro:** Simpler, less configuration messages
- **Con:** Relies on manufacturer defaults

### Option 2: Set Explicitly (Defensive)
- Always set CFG-PM-OPERATEMODE = FULL during initialization
- **Pro:** Guaranteed high performance mode
- **Con:** Extra configuration message, minimal benefit if already default

### Option 3: Query Then Set
- Query current CFG-PM-OPERATEMODE
- If not FULL, set to FULL
- **Pro:** Only configure if needed
- **Con:** More complex, requires VALGET support

---

## Conclusion

**UBX-RXM-PMREQ** is **not relevant** for INAV's GPS performance optimization. It's for putting the receiver to sleep, which is the opposite of what we want during flight.

**CFG-PM-OPERATEMODE** is **potentially useful** as a defensive measure to ensure full power mode, but since the default is already FULL, it's not strictly necessary for solving the update rate / signal quality issues.

**The real issue** (from Jetrell's testing and datasheet analysis) is that:
1. M10 is likely already in FULL power mode by default
2. The constellation-specific rate limits are **processing/signal quality constraints**, not power mode restrictions
3. Solution: Use lower update rates (6-8Hz) with multiple constellations to avoid overloading the GPS module

---

**Document Status:** Analysis complete
**Recommendation:** Focus on update rate optimization (CFG-RATE-MEAS), not power mode configuration
**Date:** 2026-01-16
