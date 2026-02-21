# Todo: Test NEXUS DSM Verification

## Phase 1: Setup

- [ ] Checkout PR #11324 branch
- [ ] Build NEXUS firmware
- [ ] Flash to Nexus hardware via DFU
- [ ] Verify basic boot and CLI access

## Phase 2: DSM Configuration

- [ ] Configure UART1 for serial RX
- [ ] Set serialrx_provider to SPEKTRUM2048
- [ ] Connect DSM satellite receiver to DSM port
- [ ] Bind satellite to transmitter

## Phase 3: Verification

- [ ] Open Configurator Receiver tab
- [ ] Verify channel values display (1000-2000 range)
- [ ] Move all transmitter sticks/switches
- [ ] Confirm all channels respond correctly
- [ ] Check for signal stability (no dropouts)
- [ ] Test SPEKTRUM1024 mode if applicable

## Phase 4: Documentation

- [ ] Document exact CLI commands used
- [ ] Note any issues or quirks found
- [ ] Photograph DSM port connection if helpful
- [ ] Update target README if needed

## Phase 5: Optional - Bind Pin

- [ ] Check if hardware has bind button/pin
- [ ] If yes, identify GPIO pin
- [ ] Add SPEKTRUM_BIND_PIN to target.h
- [ ] Test bind-on-boot functionality

## Completion

- [ ] All tests passing
- [ ] Test report created
- [ ] Send completion report to manager
