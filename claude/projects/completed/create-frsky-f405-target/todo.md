# Todo: Create FrSky F405 FC Target Configuration

## Phase 1: Schematic Analysis

- [ ] Use target-developer agent to analyze schematic
- [ ] Extract MCU pin assignments from page 2 (MCU.SchDoc)
- [ ] Identify all timer channels used for outputs
- [ ] Map all SPI buses (SPI1, SPI2, SPI3)
- [ ] Map all I2C buses (I2C1, I2C2)
- [ ] Map all UARTs (USART1-3, UART4-5, USART6)

## Phase 2: Pin Mapping

- [ ] Create target.h file skeleton
- [ ] Define MCU and clock configuration
- [ ] Map SPI1 pins (gyro - IIM-42688P)
- [ ] Map SPI2 pins (OSD - AT7456E)
- [ ] Map SPI3 pins (SD card)
- [ ] Map I2C1 pins (barometer - SPL06)
- [ ] Map I2C2 pins (external connector)
- [ ] Map all UART TX/RX pins
- [ ] Map ADC channels (VBAT, CURR, RSSI)
- [ ] Map LED pin
- [ ] Map buzzer pin

## Phase 3: Timer Allocation

- [ ] Identify timer channels for 9 motor outputs (S1-S9)
- [ ] Identify timer channels for 6 servo/LED outputs
- [ ] Check for timer conflicts
- [ ] Check for DMA conflicts
- [ ] Document timer allocation strategy

## Phase 4: Special Features

- [ ] Configure SBUS inverter on USART2_RX
- [ ] Configure current sensor (INA139)
- [ ] Configure voltage divider
- [ ] Document power output pins (9V/12V, VBEC)

## Phase 5: Documentation

- [ ] Document any pin conflicts
- [ ] Document any assumptions made
- [ ] Document missing information from schematic
- [ ] Add comments explaining pin choices
- [ ] Cross-reference with similar F405 targets

## Completion

- [ ] Target.h file created with all mappings
- [ ] Timer allocations documented
- [ ] All assumptions clearly noted
- [ ] Send completion report to manager
