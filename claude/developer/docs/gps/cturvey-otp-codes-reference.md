# cturvey's M10 OTP Codes Reference

**Source:** https://github.com/cturvey/RandomNinjaChef/tree/main/uBloxM10OTPCodes
**Author:** cturvey (clive1 on u-blox forums - well-known u-blox expert)
**Date Referenced:** 2026-01-16

---

## 192 MHz CPU Clock Mode Configuration

### Hex Sequences (from cturvey's repo)

**Command 1:**
```
B5 62 06 41 10 00 03 00 04 1F 54 5E 79 BF 28 EF 12 05 FD FF FF FF 8F 0D
```

**Command 2:**
```
B5 62 06 41 1C 00 04 01 A4 10 BD 34 F9 12 28 EF 12 05 05 00 A4 40 00 B0 71 0B 0A 00 A4 40 00 D8 B8 05 DE AE
```

### Verification

✅ **These sequences MATCH the official u-blox Integration Manual (Table 6)**
  - MAX-M10S Integration Manual (UBX-20053088-R04), Page 14
  - MIA-M10Q Integration Manual, Page 15

**Confidence Level:** HIGH - Expert-verified and matches official documentation

---

## cturvey's Warning

> "Setting OTP values in u-Blox M10 devices for permanent configuration. **Use sparingly its a finite resource.**"

**Translation:**
- OTP memory has limited write cycles
- Once written, **cannot be changed**
- Should be used "with thought and consideration"

---

## Other M10 OTP Configurations in Repo

cturvey's repository includes OTP codes for:

1. **Baud Rate Settings**
   - 57600 baud permanent default
   - 115200 baud permanent default

2. **CPU Clock Mode** ← What we care about
   - 192 MHz clock configuration (high-performance mode)

3. **Measurement Rate Control**
   - 5Hz (200ms)
   - 10Hz (100ms)
   - Combined with interference mitigation

4. **Internal LNA Modes**
   - Bypass mode
   - Low gain mode

5. **Communication Protocols**
   - UART/I2C configuration
   - Pin swapping (TX/SCL, RX/SDA)
   - NMEA/UBX protocol settings

6. **Dynamic Model Selection**
   - Automotive mode
   - High-altitude mode (80km)

---

## Implications for INAV

### What This Gives Us

1. **Verified OTP Sequences**
   - Expert-confirmed hex codes
   - Matches official documentation
   - Known working configuration

2. **Precedent for OTP Programming**
   - Other projects are using OTP programming
   - Community has experience with it
   - Not completely uncharted territory

3. **Reference Implementation**
   - Could study cturvey's code for implementation patterns
   - See how he handles OTP programming safely
   - Learn from expert approach

### What We Should Still Consider

1. **Detection Before Programming**
   - Use our query script first
   - Never blindly OTP program
   - Check if already programmed

2. **User Consent Required**
   - Clear warnings about permanence
   - User must explicitly confirm
   - Not automatic or default behavior

3. **Verification After Programming**
   - Use query script to verify success
   - Integration manual provides verification sequence
   - Don't assume success

---

## Recommended Approach for INAV

### Phase 1: Data Collection (Current)
1. ✅ Create query script (done)
2. ⏳ Test on real M10 modules
3. ⏳ Gather statistics (default vs high-perf in the wild)

### Phase 2: Decision Based on Data

**If most modules are DEFAULT:**
- Use constellation-aware rates within default limits
- Optionally: Provide OTP programming feature (with warnings)
- Document how to OTP program manually

**If most modules are HIGH_PERFORMANCE:**
- Can use higher default rates
- Less concern about exceeding limits
- Still need constellation-aware logic

### Phase 3: Implementation (If Needed)

**If we decide to implement OTP programming:**

1. **Study cturvey's implementation**
   - How does he send the sequences?
   - What error handling does he use?
   - How does he verify success?

2. **Create safe wrapper**
   - Detect current mode first (our query script)
   - Require explicit user confirmation
   - Provide clear warnings
   - Verify after programming
   - Log results

3. **Test thoroughly**
   - Test on spare modules
   - Verify with different firmware versions
   - Check all edge cases
   - Document failure modes

4. **User-facing safeguards**
   - CLI command (not automatic)
   - Multiple confirmation prompts
   - Clear warning about permanence
   - "Are you ABSOLUTELY sure?" approach

---

## Code to Review

**From cturvey's repo (for study):**

1. **`uBloxM10OTPCodes/README.md`**
   - Hex sequences for various OTP configurations
   - Documentation references

2. **`M10_gnss.c`**
   - General M10 GNSS configuration
   - May contain OTP programming code

3. **`uBloxConfig.c`**
   - u-blox configuration utilities
   - May have OTP helpers

4. **`uBloxChecksum.c`**
   - UBX checksum calculation
   - Needed for crafting OTP messages

**Action:** Clone repo and study implementation details

```bash
git clone https://github.com/cturvey/RandomNinjaChef.git
cd RandomNinjaChef
# Review files mentioned above
```

---

## Comparison: Official Manual vs cturvey

| Aspect | u-blox Manual | cturvey Repo |
|--------|--------------|--------------|
| Hex sequences | ✅ Documented | ✅ Same sequences |
| Warnings | ⚠️ "Permanent, cannot be reverted" | ⚠️ "Finite resource, use sparingly" |
| Verification | ✅ Step-by-step procedure | ❓ Not documented in README |
| Implementation | ❌ Manual process only | ✅ Likely has code |
| Safety checks | ❓ Not specified | ❓ Need to review code |

---

## Next Steps

1. **Clone and study cturvey's repo**
   - Understand his implementation
   - Look for safety checks
   - See if there's error handling

2. **Test our query script**
   - On real M10 modules
   - Gather statistics
   - Understand real-world situation

3. **Make informed decision**
   - Based on actual data from query script
   - Based on cturvey's implementation review
   - Based on user needs and risks

4. **If implementing OTP:**
   - Learn from cturvey's approach
   - Add comprehensive safety checks
   - Require explicit user confirmation
   - Test exhaustively before releasing

---

## References

**cturvey's Repository:**
- Main: https://github.com/cturvey/RandomNinjaChef
- OTP Codes: https://github.com/cturvey/RandomNinjaChef/tree/main/uBloxM10OTPCodes
- README: https://raw.githubusercontent.com/cturvey/RandomNinjaChef/main/uBloxM10OTPCodes/README.md

**Official Documentation:**
- MAX-M10S Integration Manual (UBX-20053088-R04), Page 14
- MIA-M10Q Integration Manual, Page 15

**Author Background:**
- cturvey = clive1 on u-blox forums
- Well-known u-blox expert
- Extensive u-blox experience

---

**Document Status:** Reference material for future implementation
**Confidence:** HIGH (expert-verified, matches official docs)
**Risk Assessment:** OTP programming still carries permanent modification risk
**Last Updated:** 2026-01-16
