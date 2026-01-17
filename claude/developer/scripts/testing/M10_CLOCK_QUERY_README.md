# M10 Clock Configuration Query Tool

**Purpose:** Safely query (READ-ONLY) the CPU clock configuration of u-blox M10 GPS modules to determine if they have default or high-performance clock settings.

**Safety:** This script **only reads** configuration. It does **NOT write** or modify anything.

---

## Why This Matters

M10 GPS modules can have two different CPU clock configurations:

1. **Default Clock** (low-power, most common)
   - Factory default on most modules
   - Limited update rates with multiple GNSS constellations
   - 4 constellations: ~4 Hz max
   - 3 constellations: ~6-8 Hz max
   - 2 constellations: 10 Hz max

2. **High-Performance Clock** (OTP programmed)
   - Requires permanent one-time programming
   - Higher update rates possible
   - 4 constellations: 10 Hz max
   - 3 constellations: 12-16 Hz max
   - 2 constellations: 20 Hz max

**We need to know:** What percentage of M10 modules in the wild have high-performance mode?

---

## Installation

### Requirements

```bash
pip install pyserial
```

Or on Debian/Ubuntu:
```bash
sudo apt-get install python3-serial
```

### Script Location

```
claude/developer/scripts/testing/query_m10_clock_config.py
```

---

## Usage

### Basic Usage

```bash
# Linux/Mac with USB GPS
python3 query_m10_clock_config.py /dev/ttyUSB0

# Linux/Mac with FC connected via USB
python3 query_m10_clock_config.py /dev/ttyACM0

# Windows
python query_m10_clock_config.py COM3
```

### With Different Baud Rate

```bash
python3 query_m10_clock_config.py /dev/ttyUSB0 --baud 115200
```

### Verbose Mode

```bash
python3 query_m10_clock_config.py /dev/ttyUSB0 --verbose
```

---

## Example Output

### Default Clock Module

```
Querying M10 GPS on /dev/ttyUSB0 at 9600 baud...
============================================================

1. Querying GPS version...
   GPS Version: ROM SPG 5.10 (3e2dff)

2. Querying CPU clock configuration...
   (This is a READ-ONLY operation)
   Successfully read 4 configuration values

============================================================
RESULT: CPU Clock Mode = DEFAULT
============================================================

This M10 module is running in default (low-power) clock mode.
Update rates are limited based on constellation count.

See u-blox Integration Manual for OTP programming instructions
if you want to enable high-performance mode (permanent change!).
```

### High-Performance Clock Module

```
Querying M10 GPS on /dev/ttyUSB0 at 9600 baud...
============================================================

1. Querying GPS version...
   GPS Version: ROM SPG 5.10 (3e2dff)

2. Querying CPU clock configuration...
   (This is a READ-ONLY operation)
   Successfully read 4 configuration values

============================================================
RESULT: CPU Clock Mode = HIGH_PERFORMANCE
============================================================

This M10 module has been OTP-programmed for high-performance mode.
It can achieve higher navigation update rates.
```

---

## How It Works

### Technical Details

The script uses **UBX-CFG-VALGET** to query configuration keys:

1. Sends UBX-MON-VER to verify GPS module version
2. Sends UBX-CFG-VALGET to query CPU clock configuration keys:
   - `0x40A40001`
   - `0x40A40003`
   - `0x40A40005`
   - `0x40A4000A`
3. Compares returned values against known high-performance values
4. Reports clock mode

**Source:** u-blox MAX-M10S Integration Manual (UBX-20053088-R04), Section 2.1.7, Page 14

### Safety Features

- ✅ Read-only operation (UBX-CFG-VALGET, not VALSET)
- ✅ No write operations performed
- ✅ Does NOT modify OTP memory
- ✅ Does NOT send any configuration changes
- ✅ Safe to run on any M10 module

---

## Testing Different Scenarios

### 1. Direct GPS Module Connection

Connect M10 GPS module directly to computer via USB-UART adapter:

```
M10 GPS ---- USB-UART ---- Computer
```

```bash
python3 query_m10_clock_config.py /dev/ttyUSB0
```

### 2. Flight Controller with M10 GPS

Connect flight controller via USB with M10 GPS attached:

```
M10 GPS ---- Flight Controller ---- Computer (USB)
```

**Note:** Flight controller must pass through UBX messages. May need to:
- Disable flight controller GPS processing
- Configure passthrough mode
- Use correct UART

```bash
python3 query_m10_clock_config.py /dev/ttyACM0 --baud 115200
```

### 3. Multiple Modules

Test multiple M10 modules to gather statistics:

```bash
# Module 1
python3 query_m10_clock_config.py /dev/ttyUSB0 > module1_result.txt

# Module 2
python3 query_m10_clock_config.py /dev/ttyUSB0 > module2_result.txt

# etc...
```

---

## Data Collection

### What We Want to Know

1. **Percentage of default vs high-performance modules**
2. **Which manufacturers ship with high-performance enabled**
3. **Module model variations** (M10S, M10Q, etc.)

### Reporting Results

Please share results with format:

```
Module: [Brand/Model]
Version: [from script output]
Clock Mode: [DEFAULT or HIGH_PERFORMANCE]
Purchase Date: [approximate]
Source: [where purchased]
```

Example:
```
Module: Matek M10-5883
Version: ROM SPG 5.10 (3e2dff)
Clock Mode: DEFAULT
Purchase Date: 2024-11
Source: Amazon
```

---

## Troubleshooting

### "Error opening serial port"

- Check port name is correct (`/dev/ttyUSB0`, `COM3`, etc.)
- Check permissions: `sudo chmod 666 /dev/ttyUSB0`
- Or add user to dialout group: `sudo usermod -a -G dialout $USER` (logout/login required)

### "Could not read GPS version"

- GPS not powered or not connected
- Wrong serial port
- Wrong baud rate (try `--baud 115200` or `--baud 38400`)
- Check physical connections

### "Could not read clock configuration"

- GPS firmware doesn't support CFG-VALGET (older firmware)
- Not an M10 module (script is M10-specific)
- Communication error - try again

### "WARNING: This doesn't appear to be an M10 module"

- Script detected non-M10 GPS
- Script is designed for M10 only
- May work on M9/M8 but results will be meaningless

---

## Next Steps Based on Results

### If Most Modules are DEFAULT:

- INAV should assume default clock
- Use constellation-aware rates within default limits
- Document how users can OTP program (with warnings)

### If Most Modules are HIGH_PERFORMANCE:

- INAV could use higher default rates
- Still need constellation-aware limiting
- Less concern about exceeding hardware limits

### If Results are Mixed:

- INAV could detect clock mode at runtime
- Adjust rates dynamically based on detected mode
- Best of both worlds but more complex

---

## Safety Reminder

**This script is READ-ONLY and completely safe.**

**For OTP Programming (if needed later):**
- Use official u-blox u-center software
- Follow Integration Manual exactly
- Test on spare module first
- Understand it's PERMANENT
- Not recommended for INAV to automate

---

## References

**u-blox MAX-M10S Integration Manual** (UBX-20053088-R04)
- Section 2.1.7: "High performance navigation update rate configuration"
- Page 13-14

**u-blox M10 SPG 5.10 Interface Description** (UBX-21035062-R03)
- Section 4.9.17: CFG-RATE configuration
- UBX-CFG-VALGET message format

---

**Script Version:** 1.0
**Last Updated:** 2026-01-16
**Status:** Ready for testing
