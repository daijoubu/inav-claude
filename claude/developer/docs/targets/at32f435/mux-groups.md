# AT32F435/437 MUX Group Reference

Source: AT32F435/437 Reference Manual + INAV driver source

The AT32F435 uses GPIO_MUXx registers (MUX0–MUX15) to select alternate
functions per pin. This is equivalent to STM32's AF0–AF15 numbering.

| MUX# | Peripheral Group |
|------|------------------|
| MUX 0 | SYS (SWD/JTAG, TRACE, MCO, CLKOUT) |
| MUX 1 | TMR1 / TMR2 |
| MUX 2 | TMR3 / TMR4 / TMR5 / TMR20 (partial) |
| MUX 3 | TMR8 / TMR9 / TMR10 / TMR11 |
| MUX 4 | I2C1 / I2C2 / I2C3 |
| MUX 5 | SPI1 / SPI2 / I2S1 / I2S2 |
| MUX 6 | SPI3 / SPI4 / I2S3 / I2S4 / TMR20 (partial) |
| MUX 7 | USART1 / USART2 / USART3 |
| MUX 8 | UART4 / UART5 / USART6 / UART7 / UART8 |
| MUX 9 | CAN1 / CAN2 / TMR12 / TMR13 / TMR14 |
| MUX10 | OTGFS1 / OTGFS2 |
| MUX11 | EMAC (Ethernet MII/RMII) |
| MUX12 | SDIO1 / XMC (external memory) |
| MUX13 | DVP (digital video) / SDIO2 |
| MUX14 | QSPI1 / QSPI2 |
| MUX15 | EVENTOUT |

## Key Differences from STM32

- Called 'IOMUX' / 'GPIO_MUX_n' instead of 'AFn'
- AT32 has **4 SPI** peripherals (vs 3 on F405/F722)
- AT32 has **4 USART + 4 UART = 8** serial ports (vs 6 on F405)
- AT32 has **TMR20** (extra advanced timer) on MUX2 or MUX6 depending on pin
- AT32 has **QSPI1/QSPI2** on MUX14 (not available on STM32F4)
- AT32 DMA uses **DMAMUX** — any DMA channel can serve any peripheral
  (no fixed DMA stream/channel conflicts like STM32F4)

## INAV Default MUX Values

In INAV target.h, MUX values are NOT specified for standard pin assignments;
INAV uses these defaults from the driver source:

| Peripheral | Default MUX | Override in target.h |
|------------|-------------|----------------------|
| SPI1, SPI2 | GPIO_MUX_5 | `SPI1_SCK_AF`, `SPI1_MISO_AF`, `SPI1_MOSI_AF` |
| SPI3, SPI4 | GPIO_MUX_6 | `SPI3_SCK_AF`, etc. |
| I2C1/2/3   | GPIO_MUX_4 | (always MUX4 for I2C) |
| USART1/2/3 | GPIO_MUX_7 | `UART1_AF` or `UART1_TX_AF`/`UART1_RX_AF` |
| UART4–8    | GPIO_MUX_8 | `UART4_AF` etc. |

## Timer DEF_TIM() Notes

In `target.c`, `DEF_TIM(TMR3, CH3, PB0, ...)` automatically resolves
the correct MUX number from the `DEF_TIM_AF__PB0__TCH_TMR3_CH3` macro
defined in `timer_def_at32f43x.h`. The `af` (flags) parameter in
`DEF_TIM` is unused for AT32 (pass 0).
