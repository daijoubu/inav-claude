# STM32F765/F767/F768/F769 Alternate Function Mapping (Table 13)

Source: STM32F765xx/STM32F767xx/STM32F768Ax/STM32F769xx Datasheet DS11532, pages 89–106

## AF Group Reference

| AF# | Peripheral Group |
|-----|------------------|
| AF 0 | SYS |
| AF 1 | I2C4/UART5/TIM1/2 |
| AF 2 | TIM3/4/5 |
| AF 3 | TIM8/9/10/11/LPTIM1/DFSDM1/CEC |
| AF 4 | I2C1/2/3/4/USART1/CEC |
| AF 5 | SPI1/2/3/4/5/6/I2S/I2C4/UART4/DFSDM1 |
| AF 6 | SPI2/3/SAI1/UART4/DFSDM1 |
| AF 7 | SPI6/SAI2/USART1/2/3/UART5/DFSDM1/SPDIFRX |
| AF 8 | SAI2/CAN1/UART4/5/7/8/OTG_FS/SPDIFRX |
| AF 9 | CAN1/2/TIM12/13/14/QUADSPI/SDMMC2/DFSDM1/OTG2_HS/OTG1_FS/FMC/LCD |
| AF10 | SAI2/QUADSPI/SDMMC2/DFSDM1/OTG2_HS/OTG1_FS |
| AF11 | I2C4/CAN3/SDMMC2/ETH/OTG2_FS |
| AF12 | FMC/SDMMC1/MDIOS/OTG2_FS |
| AF13 | DCMI/LCD/DSI |
| AF14 | LCD |
| AF15 | EVENTOUT |

---

## Pin Alternate Functions


### Port A

| Pin | AF0 | AF1 | AF2 | AF3 | AF4 | AF5 | AF6 | AF7 | AF8 | AF9 | AF10 | AF11 | AF12 | AF13 | AF14 | AF15 |
|-----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|
| **PA0** | - | TIM2_CH1/TIM2_ETR | TIM5_CH1 | TIM8_ETR | - | - | - | USART2_CTS | UART4_TX | - | SAI2_SD_B | ETH_MII_CRS | - | - | - | EVENTOUT |
| **PA1** | - | TIM2_CH2 | TIM5_CH2 | - | - | - | - | USART2_RTS | UART4_RX | QUADSP/I_BK1_IO3 | SAI2_MCK_B | ETH_MII_RX_CLKETH_RMI/I_REF_CLK | - | - | LCD_R2 | EVENTOUT |
| **PA2** | - | TIM2_CH3 | TIM5_CH3 | TIM9_CH1 | - | - | - | USART2_TX | SAI2_SCK_B | - | - | ETH_MDIO | MDIOS_MDIO | - | LCD_R1 | EVENTOUT |
| **PA3** | - | TIM2_CH4 | TIM5_CH4 | TIM9_CH2 | - | - | - | USART2_RX | - | LCD_B2 | OTG_HS_ULPI_D0 | ETH_MII_COL | - | - | LCD_B5 | EVENTOUT |
| **PA4** | - | - | - | - | - | SPI1_NSS/I2S1_WS | SPI3_NSS/I2S3_WS | USART2_CK | SPI6_NSS | - | - | - | OTG_HS_SOF | DCMI_H/SYNC | LCD_VSYNC | EVENTOUT |
| **PA5** | - | TIM2_CH1/TIM2_ETR | - | TIM8_CH1N | - | SPI1_SCK/I2S1_CK | - | - | SPI6_SCK | - | OTG_HS_ULPI_CK | - | - | - | LCD_R4 | EVENTOUT |
| **PA6** | - | TIM1_BKIN | TIM3_CH1 | TIM8_BKIN | - | SPI1_MISO | - | - | SPI6_MISO | TIM13_CH1 | - | - | MDIOS_MDC | DCMI_PI/XCLK | LCD_G2 | EVENTOUT |
| **PA7** | - | TIM1_CH1N | TIM3_CH2 | TIM8_CH1N | - | SPI1_MOSI/I2S1_SD | - | - | SPI6_MOSI | TIM14_CH1 | - | ETH_MII_RX_DVE/TH_RMII_CRS_DV | FMC_SDNWE | - | - | EVENTOUT |
| **PA8** | MCO1 | TIM1_CH1 | - | TIM8_BKIN2 | I2C3_SCL | - | - | USART1_CK | - | - | OTG_FS_SOF | CAN3_RX | UART7_RX | LCD_B3 | LCD_R6 | EVENTOUT |
| **PA9** | - | TIM1_CH2 | - | - | I2C3_SMBA | SPI2_SCK/I2S2_CK | - | USART1_TX | - | - | - | - | - | DCMI_D0 | LCD_R5 | EVENTOUT |
| **PA10** | - | TIM1_CH3 | - | - | - | - | - | USART1_RX | - | LCD_B4 | OTG_FS_ID | - | MDIOS_MDIO | DCMI_D1 | LCD_B1 | EVENTOUT |
| **PA11** | - | TIM1_CH4 | - | - | - | SPI2_NSS/I2S2_WS | UART4_RX | USART1_CTS | - | CAN1_RX | OTG_FS_DM | - | - | - | LCD_R4 | EVENTOUT |
| **PA12** | - | TIM1_ETR | - | - | - | SPI2_SCK/I2S2_CK | UART4_TX | USART1_RTS | SAI2_FS_B | CAN1_TX | OTG_FS_DP | - | - | - | LCD_R5 | EVENTOUT |
| **PA13** | JTMS-SWDIO | - | - | - | - | - | - | - | - | - | - | - | - | - | - | EVENTOUT |
| **PA14** | JTCK-SWCLK | - | - | - | - | - | - | - | - | - | - | - | - | - | - | EVENTOUT |
| **PA15** | JTDI | TIM2_CH1/TIM2_ETR | - | - | HDMI-CEC | SPI1_NSS/I2S1_WS | SPI3_NSS/I2S3_WS | SPI6_NSS | UART4_RTS | - | - | CAN3_TX | UART7_TX | - | - | EVENTOUT |

### Port B

| Pin | AF0 | AF1 | AF2 | AF3 | AF4 | AF5 | AF6 | AF7 | AF8 | AF9 | AF10 | AF11 | AF12 | AF13 | AF14 | AF15 |
|-----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|
| **PB0** | - | TIM1_CH2N | TIM3_CH3 | TIM8_CH2N | - | - | DFSDM1_CKOUT | - | UART4_CTS | LCD_R3 | OTG_HS_ULPI_D1 | ETH_MII_RXD2 | - | - | LCD_G1 | EVENTOUT |
| **PB1** | - | TIM1_CH3N | TIM3_CH4 | TIM8_CH3N | - | - | DFSDM1_DATIN1 | - | - | LCD_R6 | OTG_HS_ULPI_D2 | ETH_MII_RXD3 | - | - | LCD_G0 | EVENTOUT |
| **PB2** | - | - | - | - | - | - | SAI1_SD_A | SPI3_MOSI/I2S3_SD | - | QUADSP/I_CLK | DFSDM1_CKIN1 | - | - | - | - | EVENTOUT |
| **PB3** | JTDO/T/RACES/WO | TIM2_CH2 | - | - | - | SPI1_SCK/I2S1_CK | SPI3_SCK/I2S3_CK | - | SPI6_SCK | - | SDMMC2_D2 | CAN3_RX | UART7_RX | - | - | EVENTOUT |
| **PB4** | NJTRST | - | TIM3_CH1 | - | - | SPI1_MISO | SPI3_MISO | SPI2_NSS/I2S2_WS | SPI6_MISO | - | SDMMC2_D3 | CAN3_TX | UART7_TX | - | - | EVENTOUT |
| **PB5** | - | UART5_RX | TIM3_CH2 | - | I2C1_SMBA | SPI1_MOSI/I2S1_SD | SPI3_MOSI/I2S3_SD | - | SPI6_MOSI | CAN2_RX | OTG_HS_ULPI_D7 | ETH_PPS_OUT | FMC_SD/CKE1 | DCMI_D10 | LCD_G7 | EVENTOUT |
| **PB6** | - | UART5_TX | TIM4_CH1 | HDMI-CEC | I2C1_SCL | - | DFSDM1_DATIN5 | USART1_TX | - | CAN2_TX | QUADSPI_BK1_NCS | I2C4_SCL | FMC_SDNE1 | DCMI_D5 | - | EVENTOUT |
| **PB7** | - | - | TIM4_CH2 | - | I2C1_SDA | - | DFSDM1_CKIN5 | USART1_RX | - | - | - | I2S4_SDA | FMC_NL | DCMI_V/SYNC | - | EVENTOUT |
| **PB8** | - | I2C4_SCL | TIM4_CH3 | TIM10_CH1 | I2C1_SCL | - | DFSDM1_CKIN7 | UART5_RX | - | CAN1_RX | SDMMC2_D4 | ETH_MII_TXD3 | SDMMC_D4 | DCMI_D6 | LCD_B6 | EVENTOUT |
| **PB9** | - | I2C4_SDA | TIM4_CH4 | TIM11_CH1 | I2C1_SDA | SPI2_NSS/I2S2_WS | DFSDM1_DATIN7 | UART5_TX | - | CAN1_TX | SDMMC2_D5 | I2C4_SMBA | SDMMC_D5 | DCMI_D7 | LCD_B7 | EVENTOUT |
| **PB10** | - | TIM2_CH3 | - | - | I2C2_SCL | SPI2_SCK/I2S2_CK | DFSDM1_DATIN7 | USART3_TX | - | QUADSP/I_BK1_NCS | OTG_HS_ULPI_D3 | ETH_MII_RX_ER | - | - | LCD_G4 | EVENTOUT |
| **PB11** | - | TIM2_CH4 | - | - | I2C2_SDA | - | DFSDM1_CKIN7 | USART3_RX | - | - | OTG_HS_ULPI_D4 | ETH_MII_TX_ENE/TH_RMII_TX_EN | - | DSI_TE | LCD_G5 | EVENTOUT |
| **PB12** | - | TIM1_BKIN | - | - | I2C2_SMBA | SPI2_NSS/I2S2_WS | DFSDM1_DATIN1 | USART3_CK | UART5_RX | CAN2_RX | OTG_HS_ULPI_D5 | ETH_MII_TXD0ET/H_RMII_TXD0 | OTG_HS_ID | - | - | EVENTOUT |
| **PB13** | - | TIM1_CH1N | - | - | - | SPI2_SCK/I2S2_CK | DFSDM1_CKIN1 | USART3_CTS | UART5_TX | CAN2_TX | OTG_HS_ULPI_D6 | ETH_MII_TXD1ET/H_RMII_TXD1 | - | - | - | EVENTOUT |
| **PB14** | - | TIM1_CH2N | - | TIM8_CH2N | USART1_TX | SPI2_MISO | DFSDM1_DATIN2 | USART3_RTS | UART4_RTS | TIM12_CH1 | SDMMC2_D0 | - | OTG_HS_DM | - | - | EVENTOUT |
| **PB15** | RTC_REFIN | TIM1_CH3N | - | TIM8_CH3N | USART1_RX | SPI2_MOSI/I2S2_SD | DFSDM1_CKIN2 | - | UART4_CTS | TIM12_CH2 | SDMMC2_D1 | - | OTG_HS_DP | - | - | EVENTOUT |

### Port C

| Pin | AF0 | AF1 | AF2 | AF3 | AF4 | AF5 | AF6 | AF7 | AF8 | AF9 | AF10 | AF11 | AF12 | AF13 | AF14 | AF15 |
|-----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|
| **PC0** | - | - | - | DFSDM1_CKIN0 | - | - | DFSDM1_DATIN4 | - | SAI2_FS_B | - | OTG_HS_ULPI_STP | - | FMC_SDNWE | - | LCD_R5 | EVENTOUT |
| **PC1** | TRACED/0 | - | - | DFSDM1_DATAIN0 | - | SPI2_MOSI/I2S2_SD | SAI1_SD_A | - | - | - | DFSDM1_CKIN4 | ETH_MDC | MDIOS_MDC | - | - | EVENTOUT |
| **PC2** | - | - | - | DFSDM1_CKIN1 | - | SPI2_MISO | DFSDM1_CKOUT | - | - | - | OTG_HS_ULPI_DIR | ETH_MII_TXD2 | FMC_SDNE0 | - | - | EVENTOUT |
| **PC3** | - | - | - | DFSDM1_DATAIN1 | - | SPI2_MOSI/I2S2_SD | - | - | - | - | OTG_HS_ULPI_NXT | ETH_MII_TX_CLK | FMC_SD/CKE0 | - | - | EVENTOUT |
| **PC4** | - | - | - | DFSDM1_CKIN2 | - | I2S1_MCK | - | - | SPDIF_RX2 | - | - | ETH_MII_RXD0ET/H_RMII_RXD0 | FMC_SDNE0 | - | - | EVENTOUT |
| **PC5** | - | - | - | DFSDM1_DATAIN2 | - | - | - | - | SPDIF_RX3 | - | - | ETH_MII_RXD1ET/H_RMII_RXD1 | FMC_SD/CKE0 | - | - | EVENTOUT |
| **PC6** | - | - | TIM3_CH1 | TIM8_CH1 | - | I2S2_MCK | - | DFSDM1_CKIN3 | USART6_TX | FMC_NWAIT | SDMMC2_D6 | - | SDMMC_D6 | DCMI_D0 | LCD_HSYNC | EVENTOUT |
| **PC7** | - | - | TIM3_CH2 | TIM8_CH2 | - | - | I2S3_MCK | DFSDM1_DATAIN3 | USART6_RX | FMC_NE1 | SDMMC2_D7 | - | SDMMC_D7 | DCMI_D1 | LCD_G6 | EVENTOUT |
| **PC8** | TRACED/1 | - | TIM3_CH3 | TIM8_CH3 | - | - | - | UART5_RTS | USART6_CK | FMC_NE2/FMC_NCE | - | - | SDMMC_D0 | DCMI_D2 | - | EVENTOUT |
| **PC9** | MCO2 | - | TIM3_CH4 | TIM8_CH4 | I2C3_SDA | I2S_CKIN | - | UART5_CTS | - | QUADSP/I_BK1_IO0 | LCD_G3 | - | SDMMC_D1 | DCMI_D3 | LCD_B2 | EVENTOUT |
| **PC10** | - | - | - | DFSDM1_CKIN5 | - | - | SPI3_SCK/I2S3_CK | USART3_TX | UART4_TX | QUADSP/I_BK1_IO1 | - | - | SDMMC_D2 | DCMI_D8 | LCD_R2 | EVENTOUT |
| **PC11** | - | - | - | DFSDM1_DATAIN5 | - | - | SPI3_MISO | USART3_RX | UART4_RX | QUADSP/I_BK2_NCS | - | - | SDMMC_D3 | DCMI_D4 | - | EVENTOUT |
| **PC12** | TRACED/3 | - | - | - | - | - | SPI3_MOSI/I2S3_SD | USART3_CK | UART5_TX | - | - | - | SDMMC_CK | DCMI_D9 | - | EVENTOUT |
| **PC13** | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | EVENTOUT |
| **PC14** | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | EVENTOUT |
| **PC15** | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | EVENTOUT |

### Port D

| Pin | AF0 | AF1 | AF2 | AF3 | AF4 | AF5 | AF6 | AF7 | AF8 | AF9 | AF10 | AF11 | AF12 | AF13 | AF14 | AF15 |
|-----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|
| **PD0** | - | - | - | DFSDM1_CKIN6 | - | - | DFSDM1_DATAIN7 | - | UART4_RX | CAN1_RX | - | - | FMC_D2 | - | - | EVENTOUT |
| **PD1** | - | - | - | DFSDM1_DATAIN6 | - | - | DFSDM1_CKIN7 | - | UART4_TX | CAN1_TX | - | - | FMC_D3 | - | - | EVENTOUT |
| **PD2** | TRACED/2 | - | TIM3_ETR | - | - | - | - | - | UART5_RX | - | - | - | SDMMC_CMD | DCMI_D11 | - | EVENTOUT |
| **PD3** | - | - | - | DFSDM1_CKOUT | - | SPI2_SCK/I2S2_CK | DFSDM1_DATAIN0 | USART2_CTS | - | - | - | - | FMC_CLK | DCMI_D5 | LCD_G7 | EVENTOUT |
| **PD4** | - | - | - | - | - | - | DFSDM1_CKIN0 | USART2_RTS | - | - | - | - | FMC_NOE | - | - | EVENTOUT |
| **PD5** | - | - | - | - | - | - | - | USART2_TX | - | - | - | - | FMC_NWE | - | - | EVENTOUT |
| **PD6** | - | - | - | DFSDM1_CKIN4 | - | SPI3_MOSI/I2S3_SD | SAI1_SD_A | USART2_RX | - | - | DFSDM1_DATAIN1 | SDMMC2_CK | FMC_N/WAIT | DCMI_D10 | LCD_B2 | EVENTOUT |
| **PD7** | - | - | - | DFSDM1_DATAIN4 | - | SPI1_MOSI/I2S1_SD | DFSDM1_CKIN1 | USART2_CK | SPDIF_RX0 | - | - | SDMMC2_CMD | FMC_NE1 | - | - | EVENTOUT |
| **PD8** | - | - | - | DFSDM1_CKIN3 | - | - | - | USART3_TX | SPDIF_RX1 | - | - | - | FMC_D13 | - | - | EVENTOUT |
| **PD9** | - | - | - | DFSDM1_DATAIN3 | - | - | - | USART3_RX | - | - | - | - | FMC_D14 | - | - | EVENTOUT |
| **PD10** | - | - | - | DFSDM1_CKOUT | - | - | - | USART3_CK | - | - | - | - | FMC_D15 | - | LCD_B3 | EVENTOUT |
| **PD11** | - | - | - | - | I2C4_SMBA | - | - | USART3_CTS | - | QUADSP/I_BK1_IO0 | SAI2_SD_A | - | FMC_A16/FMC_CLE | - | - | EVENTOUT |
| **PD12** | - | - | TIM4_CH1 | LPTIM1_IN1 | I2C4_SCL | - | - | USART3_RTS | - | QUADSP/I_BK1_IO1 | SAI2_FS_A | - | FMC_A17/FMC_ALE | - | - | EVENTOUT |
| **PD13** | - | - | TIM4_CH2 | LPTIM1_OUT | I2C4_SDA | - | - | - | - | QUADSP/I_BK1_IO3 | SAI2_SCK_A | - | FMC_A18 | - | - | EVENTOUT |
| **PD14** | - | - | TIM4_CH3 | - | - | - | - | - | UART8_CTS | - | - | - | FMC_D0 | - | - | EVENTOUT |
| **PD15** | - | - | TIM4_CH4 | - | - | - | - | - | UART8_RTS | - | - | - | FMC_D1 | - | - | EVENTOUT |

### Port E

| Pin | AF0 | AF1 | AF2 | AF3 | AF4 | AF5 | AF6 | AF7 | AF8 | AF9 | AF10 | AF11 | AF12 | AF13 | AF14 | AF15 |
|-----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|
| **PE0** | - | - | TIM4_ETR | LPTIM1_ETR | - | - | - | - | UART8_Rx | - | SAI2_MCK_A | - | FMC_NBL0 | DCMI_D2 | - | EVENTOUT |
| **PE1** | - | - | - | LPTIM1_IN2 | - | - | - | - | UART8_T/x | - | - | - | FMC_NBL1 | DCMI_D3 | - | EVENTOUT |
| **PE2** | TRACEC/LK | - | - | - | - | SPI4_SCK | SAI1_MCLK_A | - | - | QUADSP/I_BK1_IO2 | - | ETH_MII_TXD3 | FMC_A23 | - | - | EVENTOUT |
| **PE3** | TRACED/0 | - | - | - | - | - | SAI1_SD_B | - | - | - | - | - | FMC_A19 | - | - | EVENTOUT |
| **PE4** | TRACED/1 | - | - | - | - | SPI4_NSS | SAI1_FS_A | - | - | - | DFSDM1_DATAIN3 | - | FMC_A20 | DCMI_D4 | LCD_B0 | EVENTOUT |
| **PE5** | TRACED/2 | - | - | TIM9_CH1 | - | SPI4_MISO | SAI1_SCK_A | - | - | - | DFSDM1_CKIN3 | - | FMC_A21 | DCMI_D6 | LCD_G0 | EVENTOUT |
| **PE6** | TRACED/3 | TIM1_B/KIN2 | - | TIM9_CH2 | - | SPI4_MOSI | SAI1_SD_A | - | - | - | SAI2_MCK_B | - | FMC_A22 | DCMI_D7 | LCD_G1 | EVENTOUT |
| **PE7** | - | TIM1_ETR | - | - | - | - | DFSDM1_DATAIN2 | - | UART7_Rx | - | QUADSPI_BK2_IO0 | - | FMC_D4 | - | - | EVENTOUT |
| **PE8** | - | TIM1_CH1N | - | - | - | - | DFSDM1_CKIN2 | - | UART7_T/x | - | QUADSPI_BK2_IO1 | - | FMC_D5 | - | - | EVENTOUT |
| **PE9** | - | TIM1_CH1 | - | - | - | - | DFSDM1_CKOUT | - | UART7_RTS | - | QUADSPI_BK2_IO2 | - | FMC_D6 | - | - | EVENTOUT |
| **PE10** | - | TIM1_CH2N | - | - | - | - | DFSDM1_DATAIN4 | - | UART7_CTS | - | QUADSPI_BK2_IO3 | - | FMC_D7 | - | - | EVENTOUT |
| **PE11** | - | TIM1_CH2 | - | - | - | SPI4_NSS | DFSDM1_CKIN4 | - | - | - | SAI2_SD_B | - | FMC_D8 | - | LCD_G3 | EVENTOUT |
| **PE12** | - | TIM1_CH3N | - | - | - | SPI4_SCK | DFSDM1_DATAIN5 | - | - | - | SAI2_SCK_B | - | FMC_D9 | - | LCD_B4 | EVENTOUT |
| **PE13** | - | TIM1_CH3 | - | - | - | SPI4_MISO | DFSDM1_CKIN5 | - | - | - | SAI2_FS_B | - | FMC_D10 | - | LCD_DE | EVENTOUT |
| **PE14** | - | TIM1_CH4 | - | - | - | SPI4_MOSI | - | - | - | - | SAI2_MCK_B | - | FMC_D11 | - | LCD_CLK | EVENTOUT |
| **PE15** | - | TIM1_BKIN | - | - | - | - | - | - | - | - | - | - | FMC_D12 | - | LCD_R7 | EVENTOUT |

### Port F

| Pin | AF0 | AF1 | AF2 | AF3 | AF4 | AF5 | AF6 | AF7 | AF8 | AF9 | AF10 | AF11 | AF12 | AF13 | AF14 | AF15 |
|-----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|
| **PF0** | - | - | - | - | I2C2_SDA | - | - | - | - | - | - | - | FMC_A0 | - | - | EVENTOUT |
| **PF1** | - | - | - | - | I2C2_SCL | - | - | - | - | - | - | - | FMC_A1 | - | - | EVENTOUT |
| **PF2** | - | - | - | - | I2C2_SMBA | - | - | - | - | - | - | - | FMC_A2 | - | - | EVENTOUT |
| **PF3** | - | - | - | - | - | - | - | - | - | - | - | - | FMC_A3 | - | - | EVENTOUT |
| **PF4** | - | - | - | - | - | - | - | - | - | - | - | - | FMC_A4 | - | - | EVENTOUT |
| **PF5** | - | - | - | - | - | - | - | - | - | - | - | - | FMC_A5 | - | - | EVENTOUT |
| **PF6** | - | - | - | TIM10_CH1 | - | SPI5_NSS | SAI1_SD_B | - | UART7_Rx | QUADSP/I_BK1_IO3 | - | - | - | - | - | EVENTOUT |
| **PF7** | - | - | - | TIM11_CH1 | - | SPI5_SCK | SAI1_MCLK_B | - | UART7_T/x | QUADSP/I_BK1_IO2 | - | - | - | - | - | EVENTOUT |
| **PF8** | - | - | - | - | - | SPI5_MISO | SAI1_SCK_B | - | UART7_RTS | TIM13_CH1 | QUADSPI_BK1_IO0 | - | - | - | - | EVENTOUT |
| **PF9** | - | - | - | - | - | SPI5_MOSI | SAI1_FS_B | - | UART7_CTS | TIM14_CH1 | QUADSPI_BK1_IO1 | - | - | - | - | EVENTOUT |
| **PF10** | - | - | - | - | - | - | - | - | - | QUADSP/I_CLK | - | - | - | DCMI_D11 | LCD_DE | EVENTOUT |
| **PF11** | - | - | - | - | - | SPI5_MOSI | - | - | - | - | SAI2_SD_B | - | FMC_SD/NRAS | DCMI_D12 | - | EVENTOUT |
| **PF12** | - | - | - | - | - | - | - | - | - | - | - | - | FMC_A6 | - | - | EVENTOUT |
| **PF13** | - | - | - | - | I2C4_SMBA | - | DFSDM1_DATAIN6 | - | - | - | - | - | FMC_A7 | - | - | EVENTOUT |
| **PF14** | - | - | - | - | I2C4_SCL | - | DFSDM1_CKIN6 | - | - | - | - | - | FMC_A8 | - | - | EVENTOUT |
| **PF15** | - | - | - | - | I2C4_SDA | - | - | - | - | - | - | - | FMC_A9 | - | - | EVENTOUT |

### Port G

| Pin | AF0 | AF1 | AF2 | AF3 | AF4 | AF5 | AF6 | AF7 | AF8 | AF9 | AF10 | AF11 | AF12 | AF13 | AF14 | AF15 |
|-----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|
| **PG0** | - | - | - | - | - | - | - | - | - | - | - | - | FMC_A10 | - | - | EVENTOUT |
| **PG1** | - | - | - | - | - | - | - | - | - | - | - | - | FMC_A11 | - | - | EVENTOUT |
| **PG2** | - | - | - | - | - | - | - | - | - | - | - | - | FMC_A12 | - | - | EVENTOUT |
| **PG3** | - | - | - | - | - | - | - | - | - | - | - | - | FMC_A13 | - | - | EVENTOUT |
| **PG4** | - | - | - | - | - | - | - | - | - | - | - | - | FMC_A14/FMC_BA0 | - | - | EVENTOUT |
| **PG5** | - | - | - | - | - | - | - | - | - | - | - | - | FMC_A15/FMC_BA1 | - | - | EVENTOUT |
| **PG6** | - | - | - | - | - | - | - | - | - | - | - | - | FMC_NE3 | DCMI_D12 | LCD_R7 | EVENTOUT |
| **PG7** | - | - | - | - | - | - | SAI1_MCLK_A | - | USART6_CK | - | - | - | FMC_INT | DCMI_D13 | LCD_CLK | EVENTOUT |
| **PG8** | - | - | - | - | - | SPI6_NSS | - | SPDIF_RX2 | USART6_RTS | - | - | ETH_PPS_OUT | FMC_SDCLK | - | LCD_G7 | EVENTOUT |
| **PG9** | - | - | - | - | - | SPI1_MISO | - | SPDIF_RX3 | USART6_RX | QUADSP/I_BK2_IO2 | SAI2_FS_B | SDMMC2_D0 | FMC_NE2/FMC_NCE | DCMI_V/SYNC | - | EVENTOUT |
| **PG10** | - | - | - | - | - | SPI1_NSS/I2S1_WS | - | - | - | LCD_G3 | SAI2_SD_B | SDMMC2_D1 | FMC_NE3 | DCMI_D2 | LCD_B2 | EVENTOUT |
| **PG11** | - | - | - | - | - | SPI1_SCK/I2S1_CK | - | SPDIF_RX0 | - | - | SDMMC2_D2 | ETH_MII_TX_ENE/TH_RMII_TX_EN | - | DCMI_D3 | LCD_B3 | EVENTOUT |
| **PG12** | - | - | - | LPTIM1_IN1 | - | SPI6_MISO | - | SPDIF_RX1 | USART6_RTS | LCD_B4 | - | SDMMC2_D3 | FMC_NE4 | - | LCD_B1 | EVENTOUT |
| **PG13** | TRACED/0 | - | - | LPTIM1_OUT | - | SPI6_SCK | - | - | USART6_CTS | - | - | ETH_MII_TXD0ET/H_RMII_TXD0 | FMC_A24 | - | LCD_R0 | EVENTOUT |
| **PG14** | TRACED/1 | - | - | LPTIM1_ETR | - | SPI6_MOSI | - | - | USART6_TX | QUADSP/I_BK2_IO3 | - | ETH_MII_TXD1ET/H_RMII_TXD1 | FMC_A25 | - | LCD_B0 | EVENTOUT |
| **PG15** | - | - | - | - | - | - | - | - | USART6_CTS | - | - | - | FMC_SD/NCAS | DCMI_D13 | - | EVENTOUT |

### Port H

| Pin | AF0 | AF1 | AF2 | AF3 | AF4 | AF5 | AF6 | AF7 | AF8 | AF9 | AF10 | AF11 | AF12 | AF13 | AF14 | AF15 |
|-----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|
| **PH0** | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | EVENTOUT |
| **PH1** | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | EVENTOUT |
| **PH2** | - | - | - | LPTIM1_IN2 | - | - | - | - | - | QUADSP/I_BK2_IO0 | SAI2_SCK_B | ETH_MII_CRS | FMC_SD/CKE0 | - | LCD_R0 | EVENTOUT |
| **PH3** | - | - | - | - | - | - | - | - | - | QUADSP/I_BK2_IO1 | SAI2_MCK_B | ETH_MII_COL | FMC_SDNE0 | - | LCD_R1 | EVENTOUT |
| **PH4** | - | - | - | - | I2C2_SCL | - | - | - | - | LCD_G5 | OTG_HS_ULPI_NXT | - | - | - | LCD_G4 | EVENTOUT |
| **PH5** | - | - | - | - | I2C2_SDA | SPI5_NSS | - | - | - | - | - | - | FMC_SDNWE | - | - | EVENTOUT |
| **PH6** | - | - | - | - | I2C2_SMBA | SPI5_SCK | - | - | - | TIM12_CH1 | - | ETH_MII_RXD2 | FMC_SDNE1 | DCMI_D8 | - | EVENTOUT |
| **PH7** | - | - | - | - | I2C3_SCL | SPI5_MISO | - | - | - | - | - | ETH_MII_RXD3 | FMC_SD/CKE1 | DCMI_D9 | - | EVENTOUT |
| **PH8** | - | - | - | - | I2C3_SDA | - | - | - | - | - | - | - | FMC_D16 | DCMI_H/SYNC | LCD_R2 | EVENTOUT |
| **PH9** | - | - | - | - | I2C3_SMBA | - | - | - | - | TIM12_CH2 | - | - | FMC_D17 | DCMI_D0 | LCD_R3 | EVENTOUT |
| **PH10** | - | - | TIM5_CH1 | - | I2C4_SMBA | - | - | - | - | - | - | - | FMC_D18 | DCMI_D1 | LCD_R4 | EVENTOUT |
| **PH11** | - | - | TIM5_CH2 | - | I2C4_SCL | - | - | - | - | - | - | - | FMC_D19 | DCMI_D2 | LCD_R5 | EVENTOUT |
| **PH12** | - | - | TIM5_CH3 | - | I2C4_SDA | - | - | - | - | - | - | - | FMC_D20 | DCMI_D3 | LCD_R6 | EVENTOUT |
| **PH13** | - | - | - | TIM8_CH1N | - | - | - | - | UART4_TX | CAN1_TX | - | - | FMC_D21 | - | LCD_G2 | EVENTOUT |
| **PH14** | - | - | - | TIM8_CH2N | - | - | - | - | UART4_RX | CAN1_RX | - | - | FMC_D22 | DCMI_D4 | LCD_G3 | EVENTOUT |
| **PH15** | - | - | - | TIM8_CH3N | - | - | - | - | - | - | - | - | FMC_D23 | DCMI_D11 | LCD_G4 | EVENTOUT |

### Port I

| Pin | AF0 | AF1 | AF2 | AF3 | AF4 | AF5 | AF6 | AF7 | AF8 | AF9 | AF10 | AF11 | AF12 | AF13 | AF14 | AF15 |
|-----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|
| **PI0** | - | - | TIM5_CH4 | - | - | SPI2_NSS/I2S2_WS | - | - | - | - | - | - | FMC_D24 | DCMI_D13 | LCD_G5 | EVENTOUT |
| **PI1** | - | - | - | TIM8_BKIN2 | - | SPI2_SCK/I2S2_CK | - | - | - | - | - | - | FMC_D25 | DCMI_D8 | LCD_G6 | EVENTOUT |
| **PI2** | - | - | - | TIM8_CH4 | - | SPI2_MISO | - | - | - | - | - | - | FMC_D26 | DCMI_D9 | LCD_G7 | EVENTOUT |
| **PI3** | - | - | - | TIM8_ETR | - | SPI2_MOSI/I2S2_SD | - | - | - | - | - | - | FMC_D27 | DCMI_D10 | - | EVENTOUT |
| **PI4** | - | - | - | TIM8_BKIN | - | - | - | - | - | - | SAI2_MCK_A | - | FMC_NBL2 | DCMI_D5 | LCD_B4 | EVENTOUT |
| **PI5** | - | - | - | TIM8_CH1 | - | - | - | - | - | - | SAI2_SCK_A | - | FMC_NBL3 | DCMI_V/SYNC | LCD_B5 | EVENTOUT |
| **PI6** | - | - | - | TIM8_CH2 | - | - | - | - | - | - | SAI2_SD_A | - | FMC_D28 | DCMI_D6 | LCD_B6 | EVENTOUT |
| **PI7** | - | - | - | TIM8_CH3 | - | - | - | - | - | - | SAI2_FS_A | - | FMC_D29 | DCMI_D7 | LCD_B7 | EVENTOUT |
| **PI8** | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | EVENTOUT |
| **PI9** | - | - | - | - | - | - | - | - | UART4_RX | CAN1_RX | - | - | FMC_D30 | - | LCD_VSYNC | EVENTOUT |
| **PI10** | - | - | - | - | - | - | - | - | - | - | - | ETH_MII_RX_ER | FMC_D31 | - | LCD_HSYNC | EVENTOUT |
| **PI11** | - | - | - | - | - | - | - | - | - | LCD_G6 | OTG_HS_ULPI_DIR | - | - | - | - | EVENTOUT |
| **PI12** | - | - | - | - | - | - | - | - | - | - | - | - | - | - | LCD_HSYNC | EVENTOUT |
| **PI13** | - | - | - | - | - | - | - | - | - | - | - | - | - | - | LCD_VSYNC | EVENTOUT |
| **PI14** | - | - | - | - | - | - | - | - | - | - | - | - | - | - | LCD_CLK | EVENTOUT |
| **PI15** | - | - | - | - | - | - | - | - | - | LCD_G2 | - | - | - | - | LCD_R0 | EVENTOUT |

### Port J

| Pin | AF0 | AF1 | AF2 | AF3 | AF4 | AF5 | AF6 | AF7 | AF8 | AF9 | AF10 | AF11 | AF12 | AF13 | AF14 | AF15 |
|-----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|
| **PJ0** | - | - | - | - | - | - | - | - | - | LCD_R7 | - | - | - | - | LCD_R1 | EVENTOUT |
| **PJ1** | - | - | - | - | - | - | - | - | - | - | - | - | - | - | LCD_R2 | EVENTOUT |
| **PJ2** | - | - | - | - | - | - | - | - | - | - | - | - | - | DSI_TE | LCD_R3 | EVENTOUT |
| **PJ3** | - | - | - | - | - | - | - | - | - | - | - | - | - | - | LCD_R4 | EVENTOUT |
| **PJ4** | - | - | - | - | - | - | - | - | - | - | - | - | - | - | LCD_R5 | EVENTOUT |
| **PJ5** | - | - | - | - | - | - | - | - | - | - | - | - | - | - | LCD_R6 | EVENTOUT |
| **PJ6** | - | - | - | - | - | - | - | - | - | - | - | - | - | - | LCD_R7 | EVENTOUT |
| **PJ7** | - | - | - | - | - | - | - | - | - | - | - | - | - | - | LCD_G0 | EVENTOUT |
| **PJ8** | - | - | - | - | - | - | - | - | - | - | - | - | - | - | LCD_G1 | EVENTOUT |
| **PJ9** | - | - | - | - | - | - | - | - | - | - | - | - | - | - | LCD_G2 | EVENTOUT |
| **PJ10** | - | - | - | - | - | - | - | - | - | - | - | - | - | - | LCD_G3 | EVENTOUT |
| **PJ11** | - | - | - | - | - | - | - | - | - | - | - | - | - | - | LCD_G4 | EVENTOUT |
| **PJ12** | - | - | - | - | - | - | - | - | - | LCD_G3 | - | - | - | - | LCD_B0 | EVENTOUT |
| **PJ13** | - | - | - | - | - | - | - | - | - | LCD_G4 | - | - | - | - | LCD_B1 | EVENTOUT |
| **PJ14** | - | - | - | - | - | - | - | - | - | - | - | - | - | - | LCD_B2 | EVENTOUT |
| **PJ15** | - | - | - | - | - | - | - | - | - | - | - | - | - | - | LCD_B3 | EVENTOUT |

### Port K

| Pin | AF0 | AF1 | AF2 | AF3 | AF4 | AF5 | AF6 | AF7 | AF8 | AF9 | AF10 | AF11 | AF12 | AF13 | AF14 | AF15 |
|-----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|
| **PK0** | - | - | - | - | - | - | - | - | - | - | - | - | - | - | LCD_G5 | EVENTOUT |
| **PK1** | - | - | - | - | - | - | - | - | - | - | - | - | - | - | LCD_G6 | EVENTOUT |
| **PK2** | - | - | - | - | - | - | - | - | - | - | - | - | - | - | LCD_G7 | EVENTOUT |
| **PK3** | - | - | - | - | - | - | - | - | - | - | - | - | - | - | LCD_B4 | EVENTOUT |
| **PK4** | - | - | - | - | - | - | - | - | - | - | - | - | - | - | LCD_B5 | EVENTOUT |
| **PK5** | - | - | - | - | - | - | - | - | - | - | - | - | - | - | LCD_B6 | EVENTOUT |
| **PK6** | - | - | - | - | - | - | - | - | - | - | - | - | - | - | LCD_B7 | EVENTOUT |
| **PK7** | - | - | - | - | - | - | - | - | - | - | - | - | - | - | LCD_DE | EVENTOUT |
