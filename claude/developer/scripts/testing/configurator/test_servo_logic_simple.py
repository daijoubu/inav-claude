#!/usr/bin/env python3
"""
Simple test for issue #11069 - just configure and send RC, observe in configurator.
Uses mspapi2 for cleaner MSP handling.
"""
import sys
sys.path.insert(0, '/home/raymorris/Documents/planes/inavflight/mspapi2')

from mspapi2 import MSPApi, InavMSP
import time
import struct

def configure_test():
    """Configure logic condition and servo mixer for testing"""

    print("Configuring logic condition and servo mixer...")

    with MSPApi(tcp_endpoint="localhost:5760") as api:
        # Configure Logic Condition 0: RC Channel 6 (AUX2) > 1700
        # Format: enabled, activatorId, operation, operand_type[3], operand_value[3], flags
        print("Setting logic condition 0: RC CH6 > 1700")
        logic_data = struct.pack('<BBBBBBIIIB',
            1,      # enabled
            -1,     # activatorId (-1 = always active)
            42,     # operation (42 = GREATER_THAN)
            0, 6, 0,  # operand types: 0=VALUE for A, 6=RC_CHANNEL_6 for B, 0=VALUE for C
            0, 1700, 0,  # operand values
            0       # flags
        )
        api._request(InavMSP.MSP2_INAV_SET_LOGIC_CONDITIONS, struct.pack('<B', 0) + logic_data)

        # Configure Servo Mixer Rule: Servo 0, input=MAX, rate=100, speed=0, condition=0
        print("Setting servo mixer rule: Servo 0 with logic condition 0")
        servo_data = struct.pack('<BBBBHBB',
            0,      # ruleIndex
            0,      # targetChannel (Servo 0)
            16,     # inputSource (16 = MAX, a constant max value)
            100 & 0xFF, (100 >> 8) & 0xFF,  # rate as two bytes (little endian)
            0,      # speed
            0       # conditionId
        )
        api._request(InavMSP.MSP2_INAV_SET_SERVO_MIXER, servo_data)

        # Save to EEPROM
        print("Saving configuration...")
        api._request(InavMSP.MSP_EEPROM_WRITE, b'')
        time.sleep(1)

    print("\nConfiguration complete!")
    print("\nTest procedure:")
    print("1. Go to Receiver tab in configurator")
    print("2. Set AUX2 (channel 6) to LOW (< 1700)")
    print("3. Go to Outputs/Mixer tab - Servo 0 should be INACTIVE")
    print("4. Set AUX2 to HIGH (> 1700)")
    print("5. Servo 0 should become ACTIVE")
    print("6. Set AUX2 back to LOW")
    print("7. BUG: If servo slowly decays instead of immediately stopping, bug is confirmed")

def send_rc_high():
    """Send RC with AUX2 high (>1700)"""
    with MSPApi(tcp_endpoint="localhost:5761") as api:
        # RC channels: Roll, Pitch, Yaw, Throttle, AUX1, AUX2, ...
        rc_channels = [1500, 1500, 1500, 1000,  # RPYT
                      1500, 1800,               # AUX1, AUX2 (HIGH)
                      1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500]
        rc_data = struct.pack('<' + 'H' * len(rc_channels), *rc_channels)
        api._request(InavMSP.MSP_SET_RAW_RC, rc_data)
        print("RC sent: AUX2 = HIGH (1800)")

def send_rc_low():
    """Send RC with AUX2 low (<1700)"""
    with MSPApi(tcp_endpoint="localhost:5761") as api:
        rc_channels = [1500, 1500, 1500, 1000,
                      1500, 1200,               # AUX1, AUX2 (LOW)
                      1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500]
        rc_data = struct.pack('<' + 'H' * len(rc_channels), *rc_channels)
        api._request(InavMSP.MSP_SET_RAW_RC, rc_data)
        print("RC sent: AUX2 = LOW (1200)")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 test_servo_logic_simple.py config  - Configure the test")
        print("  python3 test_servo_logic_simple.py high    - Send AUX2 HIGH")
        print("  python3 test_servo_logic_simple.py low     - Send AUX2 LOW")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "config":
        configure_test()
    elif cmd == "high":
        send_rc_high()
    elif cmd == "low":
        send_rc_low()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
