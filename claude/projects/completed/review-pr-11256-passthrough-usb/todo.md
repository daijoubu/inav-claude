# Todo List: Review PR #11256 - Passthrough USB Improvements

## Phase 1: Architecture Analysis

- [ ] Use inav-architecture agent to understand USB CDC architecture
  - [ ] Map USB CDC stack components
  - [ ] Understand serial passthrough system
  - [ ] Identify how USB and serial layers interact
  - [ ] Document component relationships
- [ ] Review cross-platform USB implementations
  - [ ] F4 VCP implementation differences
  - [ ] F7/H7 HAL implementation differences
  - [ ] AT32 considerations (not in this PR)
- [ ] Document architectural findings
  - [ ] Create architecture overview
  - [ ] Identify integration points
  - [ ] Note any architectural concerns

## Phase 2: Code Review - USB Flow Control

- [ ] Review circular buffer implementation
  - [ ] `usbd_cdc_interface.c` buffer redesign (+119/-25)
  - [ ] Check buffer overflow/underflow handling
  - [ ] Verify stall/resume logic
  - [ ] Check thread safety
- [ ] Review F4 flow control implementation
  - [ ] `vcpf4/usbd_cdc_vcp.c` changes (+69/-8)
  - [ ] Verify consistency with HAL version
- [ ] Review USB CDC core changes
  - [ ] `usbd_cdc_core.c` packet handling (+13/-2)
  - [ ] `USBD_CDC_ReceivePacket` function
  - [ ] SOF handling improvements

## Phase 3: Code Review - Line Coding

- [ ] Review line coding mirroring implementation
  - [ ] `serial_usb_vcp.c` - `usbVcpGetLineCoding` function
  - [ ] Parity bit handling (8N1, 8E1)
  - [ ] Stop bits configuration
  - [ ] Baud rate mirroring
- [ ] Review CDC accessors
  - [ ] `CDC_StopBits()` function
  - [ ] `CDC_Parity()` function
  - [ ] Cross-platform consistency
- [ ] Verify serial port configuration application
  - [ ] Check how settings propagate to UART

## Phase 4: Code Review - Passthrough Refactoring

- [ ] Review passthrough transfer logic
  - [ ] `io/serial.c` refactoring (+123/-22)
  - [ ] Batch processing implementation
  - [ ] `serialReadBuf` usage
- [ ] Review `serialReadBuf` implementation
  - [ ] `drivers/serial.c` new function (+9/-0)
  - [ ] Buffer safety
  - [ ] Return value handling
- [ ] Check error handling
  - [ ] Timeout scenarios
  - [ ] Buffer full conditions
  - [ ] Disconnect handling

## Phase 5: Code Review - Hayes Escape Sequence

- [ ] Review escape sequence state machine
  - [ ] State structure definition (`io/serial.h`)
  - [ ] Timing logic (1s silence, +++, 1s silence)
  - [ ] State transitions
- [ ] Review escape sequence detection
  - [ ] Integration in passthrough loop
  - [ ] Edge cases (partial sequences, timing)
  - [ ] Return to CLI behavior

## Phase 6: Code Quality & Style

- [ ] Check code style compliance
  - [ ] INAV coding conventions
  - [ ] Naming consistency
  - [ ] Comment quality
- [ ] Review error handling
  - [ ] Null pointer checks
  - [ ] Buffer boundary checks
  - [ ] Error return values
- [ ] Check for potential issues
  - [ ] Race conditions
  - [ ] Memory leaks
  - [ ] Integer overflow/underflow
  - [ ] Uninitialized variables

## Phase 7: Testing & Recommendations

- [ ] Review author's testing
  - [ ] STM32 flashing (8E1 line coding)
  - [ ] ESP8266/ESP32 flashing (flow control)
  - [ ] Configurator compatibility
- [ ] Identify additional testing needs
  - [ ] Edge cases to test
  - [ ] Stress testing recommendations
  - [ ] Platform-specific testing
- [ ] Document testing recommendations

## Phase 8: Synthesis & Report

- [ ] Compile architecture findings
- [ ] Compile code review findings
- [ ] Categorize issues by severity
  - [ ] Critical (must fix)
  - [ ] High (should fix)
  - [ ] Medium (nice to fix)
  - [ ] Low (nit/style)
- [ ] Create recommendations
  - [ ] Suggested improvements
  - [ ] Testing recommendations
  - [ ] Merge recommendation
- [ ] Write comprehensive review report
- [ ] Post review or send to manager

## Completion

- [ ] Architecture analysis complete
- [ ] All 13 files reviewed
- [ ] Findings documented
- [ ] Recommendations provided
- [ ] Review report created
- [ ] Send completion report to manager
