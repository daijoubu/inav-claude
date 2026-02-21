# Task Completed: Fix USB VCP Lockup on Disconnect

**Date:** 2026-02-20 22:18 | **From:** Developer | **To:** Manager | **Status:** COMPLETED

## Summary
Investigated and fixed the USB VCP lockup issue where flight controllers would freeze when the USB cable was disconnected during active communication. The issue affected both legacy (F4) and HAL-based (F7/H7) USB stacks. Root cause was infinite loops in CDC data transmission with no timeout handling, combined with inadequate disconnect detection on F4 boards without VBUS sensing.

## Branch/PR
**Branch:** `fix-usb-vcp-blocking` | **Remote:** daijoubu/inav | **Base:** upstream/maintenance-9.x | **Status:** Ready for review

## Commits
1. **Fix USB VCP lockup on disconnect (STM32F4)** - Added 50ms timeout to blocking loops in VCP_DataTx, fixed serialIsConnected() missing return statement
2. **Fix USB VCP lockup on disconnect (STM32F7/H7)** - Same timeout fix for HAL-based USB stack
3. **Fix CDC_Send_FreeBytes buffer calculation (STM32F4)** - Corrected circular buffer math that was using wrong buffer pointers
4. **Add DTR tracking for USB VCP connection detection** - Register callback to track when host opens COM port
5. **Add suspend detection as disconnect fallback (STM32F4)** - Treat USB suspend as disconnect for boards without VBUS sensing
6. **Fix DTR tracking default - assume connected initially** - Default to true so MSP works on tools that don't assert DTR

## Changes
- `src/main/drivers/serial.c` - Fixed missing return in serialIsConnected()
- `src/main/drivers/serial_usb_vcp.c` - Added DTR tracking callback
- `src/main/vcpf4/usbd_cdc_vcp.c` - Added 50ms timeout, fixed CDC_Send_FreeBytes buffer math
- `src/main/vcpf4/usbd_usr.c` - Added USB suspend detection
- `src/main/vcp_hal/usbd_cdc_interface.c` - Added 50ms timeout for F7/H7

## Testing
- [x] Tested on SPEEDYBEEF405WING (STM32F405)
- [x] Enabled LOG_DEBUG in navigation code to generate USB traffic
- [x] Engaged NAV mode while connected via USB
- [x] Unplugged USB cable during active debug output
- [x] Verified FC continues operating normally without lockup
- [x] Confirmed servo movement smooth, only minor hiccup during disconnect event

## Root Cause Analysis
- Infinite loops in CDC_Send_DATA/VCP_DataTx with no timeout
- On F4 boards without VBUS sensing, USB disconnect not detected
- serialIsConnected() had bug - never returned vtable result
- DTR state not tracked, couldn't detect when host closed port

## Next Steps
- Consider squashing commits before submitting PR to upstream
- PR ready for review by team when approved

---
**Developer**
