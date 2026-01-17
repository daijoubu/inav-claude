# M10 Navigation Update Rate - Key Findings

**Source:** MAX-M10S Data Sheet UBX-20035208

## Critical Discovery: Update Rate Depends on Constellation Count

The M10 datasheet shows that **maximum safe update rate decreases as more GNSS constellations are enabled**.

### Default Mode Update Rates

| GNSS Configuration | Max Nav Update Rate |
|-------------------|---------------------|
| GPS+GAL | 10 Hz |
| GPS+GAL+GLO | 6 Hz |
| GPS+GAL+BDS B1I (default) | 3 Hz |
| GPS+GAL+BDS B1C | 8 Hz |
| GPS+GAL+BDS B1C+GLO | 4 Hz |

### High Performance Mode Update Rates

| GNSS Configuration | Max Nav Update Rate |
|-------------------|---------------------|
| GPS+GAL | 20 Hz |
| GPS+GAL+GLO | 16 Hz |
| GPS+GAL+BDS B1I | 12 Hz |
| GPS+GAL+BDS B1C | 16 Hz |
| GPS+GAL+BDS B1C+GLO | 10 Hz |

## Key Insights

1. **More constellations = Lower max update rate**
   - With 2 constellations (GPS+GAL): 10Hz default, 20Hz high perf
   - With 3 constellations (GPS+GAL+GLO): 6Hz default, 16Hz high perf
   - With 4 constellations (GPS+GAL+BDS+GLO): 4Hz default, 10Hz high perf

2. **Even in "High Performance" mode, 4 constellations max out at 10Hz**
   - This explains Jetrell's findings!
   - INAV's 10Hz default is running M10 at its absolute limit when using 4 constellations
   - No headroom for the GPS module to handle processing load

3. **Default mode with 4 constellations: only 3-4Hz recommended**
   - INAV running at 10Hz with 4 constellations is forcing "high performance" mode
   - May require special configuration to enable
   - Could explain satellite tracking issues and HDOP fluctuations

## Implications for INAV

**Current INAV Configuration:**
- Enables Galileo by default (will enable in this PR)
- Users often enable Glonass and/or Beidou for more satellites
- Default update rate: 10Hz

**Problem:**
- With 4 constellations, 10Hz is the MAXIMUM even in high-performance mode
- GPS module is at its processing limit
- Results in poor satellite tracking and HDOP instability (Jetrell's findings)

**Recommended Changes:**
- **2 constellations (GPS+Galileo):** 10Hz is safe ✅
- **3 constellations (GPS+Galileo+one more):** Reduce to 6-8Hz
- **4 constellations (GPS+Galileo+Glonass+Beidou):** Reduce to 4-6Hz

## Configuration-Aware Update Rate

INAV could implement constellation-aware update rates:

```c
// Count enabled constellations
int constellations = 1; // GPS always
if (gpsConfig()->ubloxUseGalileo) constellations++;
if (gpsConfig()->ubloxUseGlonass) constellations++;
if (gpsConfig()->ubloxUseBeidou) constellations++;

// Set rate based on constellation count
uint8_t recommendedHz;
if (constellations >= 4) {
    recommendedHz = 6;  // 4 constellations: conservative default
} else if (constellations == 3) {
    recommendedHz = 8;  // 3 constellations: good balance
} else {
    recommendedHz = 10; // 1-2 constellations: full speed
}
```

## Why This Wasn't Noticed Before

- Galileo was OFF by default in INAV
- Most users running GPS-only or GPS+Glonass (2 constellations)
- 10Hz works fine with 2 constellations
- Once we enable Galileo by default, users may enable 3-4 constellations
- Problem becomes visible

## Reference

Data Sheet: MAX-M10S_DataSheet_UBX-20035208.pdf
Table 1: MAX-M10S specifications (Page 4)
