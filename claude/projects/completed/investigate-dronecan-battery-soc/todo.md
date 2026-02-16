# Todo: Investigate DroneCAN Battery SOC Integration

## Phase 1: Research DroneCAN Battery Messages

- [ ] Identify battery-related DroneCAN messages
  - [ ] Search DSDL for BatteryInfo message
  - [ ] Check for SOC/remaining_capacity fields
  - [ ] Look for energy consumption fields (Wh consumed, etc.)
  - [ ] Document all relevant fields

- [ ] Check device support
  - [ ] Which devices support SOC reporting?
  - [ ] What data format is used?
  - [ ] Are there standard fields or vendor-specific?

## Phase 2: Analyze Current Battery Implementation

- [ ] Review INAV battery code
  - [ ] battery_sensor_dronecan.c - current implementation
  - [ ] battery.c - general battery handling
  - [ ] How current integration works
  - [ ] How mAh consumption is calculated

- [ ] Understand calculation flow
  - [ ] How is battery percentage calculated?
  - [ ] What triggers battery warnings?
  - [ ] How is "battery remaining" determined?

## Phase 3: Determine Implementation Requirements

- [ ] Identify required changes
  - [ ] Parse new fields from DroneCAN messages
  - [ ] Store SOC values
  - [ ] Modify calculation logic

- [ ] Design user configuration
  - [ ] Define setting options (Current/DroneCAN/Fallback)
  - [ ] Determine default behavior
  - [ ] Consider UI implications

- [ ] Analyze edge cases
  - [ ] What if DroneCAN SOC is unavailable?
  - [ ] What if values are out of range?
  - [ ] How to handle unit conversions?

## Phase 4: Create Implementation Plan

- [ ] Document architecture
  - [ ] Data flow diagram
  - [ ] Integration points
  - [ ] Settings structure

- [ ] Create step-by-step plan
  - [ ] Phase 1: Parse new fields
  - [ ] Phase 2: Add configuration setting
  - [ ] Phase 3: Implement calculation logic
  - [ ] Phase 4: Testing

- [ ] Estimate timeline and risks
  - [ ] Effort per phase
  - [ ] Potential blockers
  - [ ] Mitigation strategies

## Phase 5: Document Findings

- [ ] Write investigation report
  - [ ] Executive summary
  - [ ] Technical analysis
  - [ ] Implementation plan
  - [ ] Risk assessment

- [ ] Submit to manager
  - [ ] Report in project directory
  - [ ] Send completion report
