# DroneCAN DSDL Codec Management Guide

**Version:** 1.0
**Date:** 2026-02-13
**Status:** Complete
**For:** INAV Flight Controller Firmware

---

## Section 1: Current DSDL Version & Generation Info

### DroneCAN/DSDL Repository

| Property | Value |
|----------|-------|
| **Repository** | https://github.com/DroneCAN/DSDL |
| **Original Commit** | Added 2026-01-24 |
| **Generator Tool** | dsdlc (part of libcanard) |
| **Generated Files** | 119 .c files + 138 .h files (~8,219 lines) |
| **Location in INAV** | `src/main/drivers/dronecan/dsdlc_generated/` |

### Tool Information

| Property | Details |
|----------|---------|
| **Tool Name** | dsdlc (DSDL Compiler) |
| **Language** | Python 3.9+ |
| **Repository** | https://github.com/dronecan/libcanard |
| **Installation** | `pip install pydsdl` |
| **Purpose** | Generates C encode/decode functions from UAVCAN/DSDL definitions |

### Current Implementation

The DSDL files were generated once and committed to the repository. They cover a comprehensive set of DroneCAN and UAVCAN messages, with all 119 source files actively compiled into the build.

---

## Section 2: Currently Used Messages

### Overview

**Total Generated Files:** 257
- **Compiled Source Files:** 119 (all actively used)
- **Header Files:** 138 (101 exposed via umbrella header)
- **Total Lines of Code:** ~8,219 (all compiled)

### Message Categories

All generated code falls into these categories:

#### DroneCAN Protocol Messages (4)
- `dronecan.protocol.CanStats` - CAN bus statistics
- `dronecan.protocol.FlexDebug` - Debug messages
- `dronecan.protocol.GlobalTime` - Time synchronization
- `dronecan.protocol.Stats` - Protocol statistics

#### DroneCAN Remote ID Messages (7)
- `dronecan.remoteid.ArmStatus` - Arming status for Remote ID
- `dronecan.remoteid.BasicID` - Basic aircraft identification
- `dronecan.remoteid.Location` - Aircraft location
- `dronecan.remoteid.OperatorID` - Operator identification
- `dronecan.remoteid.SecureCommand` (req/res) - Secure commands
- `dronecan.remoteid.SelfID` - Self identification
- `dronecan.remoteid.System` - System information

#### DroneCAN Sensor Messages (4)
- `dronecan.sensors.hygrometer.Hygrometer` - Humidity sensor
- `dronecan.sensors.magnetometer.MagneticFieldStrengthHiRes` - High-res magnetometer
- `dronecan.sensors.rc.RCInput` - RC receiver input
- `dronecan.sensors.rpm.RPM` - Motor RPM data

#### UAVCAN Equipment Messages (50+)
- **Actuator:** ArrayCommand, Command, Status
- **AHRS:** MagneticFieldStrength, MagneticFieldStrength2, RawIMU, Solution
- **Air Data:** AngleOfAttack, IndicatedAirspeed, RawAirData, Sideslip, StaticPressure, StaticTemperature, TrueAirspeed
- **Camera Gimbal:** AngularCommand, GEOPOICommand, Mode, Status
- **Device:** Temperature
- **ESC:** RawCommand, RPMCommand, Status, StatusExtended
- **GNSS:** Auxiliary, ECEFPositionVelocity, Fix, Fix2, RTCMStream
- **Hardpoint:** Command, Status
- **ICE:** FuelTankStatus, reciprocating/CylinderStatus, reciprocating/Status
- **Indication:** BeepCommand, LightsCommand, RGB565, SingleLightCommand
- **Power:** BatteryInfo, CircuitStatus, PrimaryPowerSupplyStatus
- **Range Sensor:** Measurement
- **Safety:** ArmingStatus

#### UAVCAN Standard Protocol Messages (30+)
- **Access:** AccessCommandShell (req/res)
- **Core:** CANIfaceStats, DataTypeKind, GetDataTypeInfo (req/res), GetNodeInfo (req/res), GetTransportStats (req/res), GlobalTimeSync, HardwareVersion, NodeStatus, Panic, RestartNode (req/res), SoftwareVersion
- **Debug:** KeyValue, LogLevel, LogMessage
- **Dynamic Node ID:** Allocation, server/AppendEntries (req/res), server/Discovery, server/Entry, server/RequestVote (req/res)
- **Enumeration:** Begin (req/res), Indication
- **File Transfer:** BeginFirmwareUpdate (req/res), Delete (req/res), EntryType, Error, GetDirectoryEntryInfo (req/res), GetInfo (req/res), Path, Read (req/res), Write (req/res)
- **Parameters:** Empty, ExecuteOpcode (req/res), GetSet (req/res), NumericValue, Value
- **Tunnel:** Broadcast, Call (req/res), Protocol, SerialConfig, Targetted

#### UAVCAN Standard Messages (10+)
- `uavcan.CoarseOrientation` - Coarse orientation estimate
- `uavcan.navigation.GlobalNavigationSolution` - Global nav solution
- `uavcan.Timestamp` - Global timestamp

### INAV Feature Usage

| INAV Feature | Uses Messages | Key Messages |
|---|---|---|
| **GPS** | DroneCAN GNSS | Fix2, Fix, Auxiliary |
| **Battery Monitoring** | Power system | BatteryInfo |
| **Node Management** | Protocol/Core | NodeStatus, GetNodeInfo |
| **Remote ID** | Regulatory | Various remoteid.* |
| **Sensor Integration** | Equipment | Temperature, RPM, RCInput, Hygrometer |

---

## Section 3: Adding New DroneCAN Messages

### Overview

To extend INAV with support for new DroneCAN messages, follow these steps:

### Step 1: Identify the Message

**Determine what data you need:**
- Sensor readings? Check `dronecan.sensors.*` or `uavcan.equipment.*`
- Protocol/configuration? Check `dronecan.protocol.*` or `uavcan.protocol.*`
- Vendor-specific? Check vendor namespace in DSDL repo

**Browse DSDL Repository:**

```bash
# Clone repository (if not already done)
git clone https://github.com/DroneCAN/DSDL.git

# Find messages in a category
find . -path "*equipment/power*" -name "*.uavcan"

# Or search by name
find . -name "*Temperature*" -o -name "*battery*"
```

**Example: Adding Temperature Sensor Support**

```bash
# Search for temperature messages
find DSDL -iname "*temperature*"

# Result: uavcan/equipment/device/Temperature.uavcan

# Examine the message
cat DSDL/uavcan/equipment/device/Temperature.uavcan
```

### Step 2: Generate C Code

**Install dsdlc tool:**

```bash
# Using pip (recommended)
pip install pydsdl

# Or from repository
git clone https://github.com/dronecan/libcanard.git
cd libcanard && pip install .
```

**Verify installation:**

```bash
dsdlc --help
```

**Generate C code for your message:**

```bash
# Generate code for a specific message
dsdlc --output generated DSDL/uavcan/equipment/device/

# Result: generated/include/ and generated/src/ directories
```

**Result files:**
```
generated/
├── include/
│   └── uavcan.equipment.device.Temperature.h
└── src/
    └── uavcan.equipment.device.Temperature.c
```

### Step 3: Integrate into INAV

**Copy generated files to INAV:**

```bash
# Copy header file
cp generated/include/uavcan.equipment.device.Temperature.h \
   inav/src/main/drivers/dronecan/dsdlc_generated/include/

# Copy source file
cp generated/src/uavcan.equipment.device.Temperature.c \
   inav/src/main/drivers/dronecan/dsdlc_generated/src/
```

**Update CMake configuration:**

Edit `inav/cmake/dsdlc_generated.cmake` and add to `DSDLC_GENERATED_SRC`:

```cmake
set(DSDLC_GENERATED_SRC
    # ... existing messages ...

    # Add new message (alphabetically sorted)
    uavcan.equipment.device.Temperature.c

    # ... rest of list ...
)
```

**Update umbrella header (if needed):**

If you want the message exposed through `dronecan_msgs.h`, edit:
`inav/src/main/drivers/dronecan/dsdlc_generated/include/dronecan_msgs.h`

Add to includes section:

```c
#include "uavcan.equipment.device.Temperature.h"
```

### Step 4: Use in Code

**Include the umbrella header:**

```c
#include "drivers/dronecan/dsdlc_generated/include/dronecan_msgs.h"
```

Or include specific message (if not in umbrella):

```c
#include "drivers/dronecan/dsdlc_generated/include/uavcan.equipment.device.Temperature.h"
```

**Use the generated struct and functions:**

```c
// Declare message struct
struct uavcan_equipment_device_Temperature temp_msg = {};

// Set values
temp_msg.kelvin = 298.15f;  // 25°C

// Encode to send
uint8_t buffer[64];
uint32_t encoded_size = uavcan_equipment_device_Temperature_encode(
    &temp_msg,
    buffer
);

// Decode from received message
bool decode_ok = uavcan_equipment_device_Temperature_decode(
    transfer,  // CanardRxTransfer from CAN bus
    &temp_msg
);
```

### Step 5: Build and Test

**Build INAV with new message support:**

```bash
# Using inav-builder agent (recommended)
# Or manually:
cmake -DCMAKE_BUILD_TYPE=Release -DUSE_DRONECAN=ON -S inav -B build
cmake --build build
```

**Verify no compilation errors:**

The build should complete without errors. If you get compilation errors:
- Check that file names match exactly (case-sensitive)
- Verify cmake/dsdlc_generated.cmake syntax
- Confirm all #include paths are correct

**Test the feature:**

Once built, test that:
- The flight controller receives the new message type
- Data is correctly decoded
- Any INAV features using the data work properly

---

## Section 4: Naming Convention Reference

### Mapping DSDL Names to C Code

The dsdlc tool uses a **deterministic naming pattern**. Once you know the DSDL message name, you can predict the C code structure:

### Pattern: Dots → Underscores

| Element | DSDL | C Code |
|---------|------|--------|
| **Namespace** | `dronecan.sensors.rc` | `dronecan_sensors_rc` |
| **Message Name** | `RCInput` | `RCInput` (CamelCase preserved) |
| **Full Struct** | `dronecan.sensors.rc.RCInput` | `dronecan_sensors_rc_RCInput` |

### Generated C Names

| Purpose | Pattern | Example |
|---------|---------|---------|
| **Header File** | Keep original filename | `dronecan.sensors.rc.RCInput.h` |
| **C Struct** | `struct <namespace_message>` | `struct dronecan_sensors_rc_RCInput` |
| **Encode Function** | `<namespace_message>_encode()` | `dronecan_sensors_rc_RCInput_encode()` |
| **Decode Function** | `<namespace_message>_decode()` | `dronecan_sensors_rc_RCInput_decode()` |
| **Max Size Macro** | `<NAMESPACE_MESSAGE>_MAX_SIZE` | `DRONECAN_SENSORS_RC_RCINPUT_MAX_SIZE` |

### Quick Reference Examples

| DSDL Message | Header to Include | C Struct | Encode Function |
|---|---|---|---|
| `uavcan.equipment.power.BatteryInfo` | `uavcan.equipment.power.BatteryInfo.h` | `struct uavcan_equipment_power_BatteryInfo` | `uavcan_equipment_power_BatteryInfo_encode()` |
| `dronecan.sensors.rc.RCInput` | `dronecan.sensors.rc.RCInput.h` | `struct dronecan_sensors_rc_RCInput` | `dronecan_sensors_rc_RCInput_encode()` |
| `uavcan.protocol.NodeStatus` | `uavcan.protocol.NodeStatus.h` | `struct uavcan_protocol_NodeStatus` | `uavcan_protocol_NodeStatus_encode()` |
| `uavcan.protocol.dynamic_node_id.Allocation` | `uavcan.protocol.dynamic_node_id.Allocation.h` | `struct uavcan_protocol_dynamic_node_id_Allocation` | `uavcan_protocol_dynamic_node_id_Allocation_encode()` |

---

## Section 5: File Organization

### Current Structure

```
inav/src/main/drivers/dronecan/dsdlc_generated/
├── include/                    # Header files (138 total)
│   ├── dronecan_msgs.h        # Umbrella header (exposes 101 messages)
│   ├── dronecan.protocol.*.h
│   ├── dronecan.remoteid.*.h
│   ├── dronecan.sensors.*.h
│   ├── uavcan.*.h
│   └── ... (more headers)
└── src/                        # Source files (119 total)
    ├── dronecan.protocol.*.c
    ├── dronecan.remoteid.*.c
    ├── dronecan.sensors.*.c
    ├── uavcan.*.c
    └── ... (more source files)
```

### CMake Configuration

**File:** `inav/cmake/dsdlc_generated.cmake`

- Defines `DSDLC_GENERATED_DIR` - location of generated files
- Lists all `.c` files to compile in `DSDLC_GENERATED_SRC`
- Defines include directory in `DSDLC_GENERATED_DIRS`

**Integration point:** `inav/src/main/CMakeLists.txt` includes this file

### Include Path Configuration

Generated headers are included via:

```c
#include "drivers/dronecan/dsdlc_generated/include/dronecan_msgs.h"
```

The path is configured in `inav/cmake/main.cmake`:

```cmake
${MAIN_SRC_DIR}/drivers/dronecan/dsdlc_generated/include
```

---

## Section 6: Reference & Tools

### DroneCAN/DSDL Repository

- **Official Repository:** https://github.com/DroneCAN/DSDL
- **Browse Online:** GitHub web interface
- **Clone:** `git clone https://github.com/DroneCAN/DSDL.git`

### dsdlc Tool

- **Part of:** libcanard project
- **Repository:** https://github.com/dronecan/libcanard
- **Installation:** `pip install pydsdl`
- **Documentation:** Check libcanard README

### UAVCAN/DroneCAN Specifications

- **DroneCAN Spec:** https://dronecan.github.io/
- **UAVCAN Spec:** https://uavcan.org/
- **Message Format:** `.uavcan` files are text-based definitions

### INAV DroneCAN Support

- **Documentation:** `inav/docs/DroneCAN.md`
- **Main Driver:** `inav/src/main/drivers/dronecan/dronecan.c`
- **Build Flag:** `-DUSE_DRONECAN=ON`

### Common DroneCAN Message IDs

| Message | ID | DSDL Path |
|---------|----|----|
| NodeStatus | 341 | `dronecan/protocol/341.NodeStatus.uavcan` |
| BatteryInfo | 1092 | `uavcan/equipment/power/1092.BatteryInfo.h` |
| Fix2 (GNSS) | 1063 | `uavcan/equipment/gnss/1063.Fix2.uavcan` |
| RCInput | 1140 | `dronecan/sensors/rc/1140.RCInput.uavcan` |

---

## Section 7: Troubleshooting

### Build Errors After Adding Message

**Error: "Cannot find file..."**
- Check filename spelling and case (file paths are case-sensitive)
- Verify CMake syntax in dsdlc_generated.cmake
- Ensure file exists in both include/ and src/

**Error: "struct not found..."**
- Verify umbrella header includes the new message header
- Check struct name matches naming convention (dots → underscores)
- Ensure header file was copied to correct location

### dsdlc Installation Issues

**Python version error:**
- Ensure Python 3.9+ is installed
- Use `python3 --version` to check

**Module not found:**
- Reinstall: `pip install --upgrade pydsdl`
- Check pip output for any errors

---

## Quick Checklist: Adding a New Message

- [ ] Find message in DSDL repository
- [ ] Read message definition (.uavcan file)
- [ ] Install dsdlc tool (`pip install pydsdl`)
- [ ] Generate C code with dsdlc
- [ ] Copy .h file to `dsdlc_generated/include/`
- [ ] Copy .c file to `dsdlc_generated/src/`
- [ ] Update `cmake/dsdlc_generated.cmake` with new .c file
- [ ] (Optional) Update `dronecan_msgs.h` to expose message
- [ ] Build INAV with `-DUSE_DRONECAN=ON`
- [ ] Verify no compilation errors
- [ ] Test message receiving/sending
- [ ] Document your changes

---

## Document Metadata

| Item | Value |
|------|-------|
| **Created** | 2026-02-13 |
| **Version** | 1.0 |
| **DSDL Generated** | 2026-01-24 |
| **Generator** | dsdlc (libcanard) |
| **Files Covered** | 119 .c + 138 .h (257 total) |
| **Total Lines** | ~8,219 (all compiled) |
| **Base DSDL Repo** | https://github.com/DroneCAN/DSDL |

