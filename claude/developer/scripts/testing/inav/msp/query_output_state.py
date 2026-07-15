#!/usr/bin/env python3
"""Read-only MSP query: timer output mode overrides + output mapping ext2.
Does NOT send any SET/arm/config commands."""
import sys
sys.path.insert(0, "/home/raymorris/inavflight/mspapi2")
from mspapi2 import MSPApi, InavMSP

MODE_NAMES = {0: "AUTO", 1: "MOTORS", 2: "SERVOS", 3: "LED", 4: "PINIO", 5: "BEEPER"}
TIM_ID_NAMES = {0: "TIM1", 1: "TIM2", 2: "TIM3", 3: "TIM4", 4: "TIM5", 5: "TIM6",
                6: "TIM7", 7: "TIM8", 8: "TIM12", 9: "TIM13", 10: "TIM14",
                11: "TIM15", 12: "TIM16", 13: "TIM17"}
TIM_USE_BEEPER = 1 << 25
PA15_TIMER_INDEX = 1  # TIM2, per BROTHERHOBBYH743/target.c DEF_TIM(TIM2, CH1, PA15, TIM_USE_BEEPER,...)

with MSPApi(port="/dev/ttyACM0", baudrate=115200) as api:
    # --- 1. MSP2_INAV_TIMER_OUTPUT_MODE (0x200E), dataSize==0 -> list all ---
    info, payload = api._request_raw(InavMSP.MSP2_INAV_TIMER_OUTPUT_MODE, b"")
    print(f"MSP2_INAV_TIMER_OUTPUT_MODE: {len(payload)} bytes, {len(payload)//2} entries")
    beeper_overrides = []
    for i in range(0, len(payload), 2):
        timer_index, mode = payload[i], payload[i + 1]
        tim_name = TIM_ID_NAMES.get(timer_index, "?")
        mode_name = MODE_NAMES.get(mode, f"unknown({mode})")
        flag = "  <-- PA15/BEEPER pin" if timer_index == PA15_TIMER_INDEX else ""
        print(f"  timerIndex={timer_index:2d} ({tim_name:6s}) outputMode={mode} ({mode_name}){flag}")
        if mode == 5:
            beeper_overrides.append((timer_index, tim_name))

    print()
    if not beeper_overrides:
        print("No timer currently has a runtime BEEPER override -> compile-time PA15/TIM2 fallback is active.")
    elif beeper_overrides == [(PA15_TIMER_INDEX, "TIM2")]:
        print("Only PA15/TIM2 has BEEPER override -> consistent, expected, no hijack risk.")
    else:
        print("WARNING: BEEPER override found on:", beeper_overrides)

    # --- 2. MSP2_INAV_OUTPUT_MAPPING_EXT2 (0x210D) via dynamic codec ---
    info2, mapping = api._request(InavMSP.MSP2_INAV_OUTPUT_MAPPING_EXT2, b"")
    print(f"\nMSP2_INAV_OUTPUT_MAPPING_EXT2: {len(mapping)} pad entries")
    for idx, entry in enumerate(mapping):
        beeper_bit = bool(entry["usageFlags"] & TIM_USE_BEEPER)
        tim_name = TIM_ID_NAMES.get(entry["timerId"], "?")
        print(f"  padIdx={idx:2d} timerId={entry['timerId']:2d} ({tim_name:6s}) "
              f"usageFlags=0x{entry['usageFlags']:08x} TIM_USE_BEEPER={beeper_bit} "
              f"pinLabel={entry['pinLabel']}")
