# STM32F405 TIM12 Findings

**Date:** 2026-01-16
**Source:** Official documentation and INAV codebase analysis

## Confirmed: TIM12 EXISTS on STM32F405

### Pin Alternate Functions

From STM32F405 documentation:

**PB14 Alternate Functions:**
- SPI2_MISO
- TIM1_CH2N
- **TIM12_CH1** (AF9)
- OTG_HS_DM
- USART3_RTS
- TIM8_CH2N
- I2S2ext_SD
- EVENTOUT

**PB15 Alternate Functions:**
- SPI2_MOSI
- I2S2_SD
- TIM1_CH3N
- TIM8_CH3N
- **TIM12_CH2** (AF9)
- OTG_HS_DP
- EVENTOUT
- RTC_REFIN

### TIM12 in INAV Codebase

From `inav/src/main/drivers/timer_stm32f4xx.c`:

```c
#if defined(TIM12) && !defined(STM32F411xE)
    [11] = { .tim = TIM12, .rcc = RCC_APB1(TIM12), .irq = TIM8_BRK_TIM12_IRQn},
#endif
```

From `inav/src/main/drivers/timer_def_stm32f4xx.h`:

```c
#define DEF_TIM_DMA__BTCH_TIM12_CH1   NONE
#define DEF_TIM_DMA__BTCH_TIM12_CH2   NONE
```

**Key Finding:** TIM12 exists on F405 but has NO DMA support!

### Comparison with F7/H7

From `inav/src/main/drivers/timer_def_stm32f7xx.h`:

```c
#define DEF_TIM_AF__PB14__TCH_TIM12_CH1   D(9, 12)  // AF9, TIM12
#define DEF_TIM_AF__PB15__TCH_TIM12_CH2   D(9, 12)  // AF9, TIM12
```

From `inav/src/main/drivers/timer_def_stm32h7xx.h`:

```c
#define DEF_TIM_AF__PB14__TCH_TIM12_CH1   D(2, 12)  // AF2, TIM12
#define DEF_TIM_AF__PB15__TCH_TIM12_CH2   D(2, 12)  // AF2, TIM12
```

**F7 and H7 also have TIM12 on PB14/PB15** with the same channels.

## DMA Support Summary

| MCU Series | TIM12 Exists? | DMA Support? | Alternate Function |
|------------|---------------|--------------|-------------------|
| STM32F405  | ✅ YES        | ❌ NO        | AF9               |
| STM32F7xx  | ✅ YES        | ❌ NO        | AF9               |
| STM32H7xx  | ✅ YES        | ❌ NO        | AF2               |

**Note:** TIM12 exists across F4/F7/H7 but has NO DMA on any of them!

## Implications for Motor Outputs

### What Works:
- ✅ Standard PWM (50Hz - 490Hz)
- ✅ OneShot125
- ✅ OneShot42
- ✅ MultiShot

### What DOESN'T Work:
- ❌ DShot150/300/600/1200 (requires DMA)
- ❌ ProShot (requires DMA)
- ❌ Burst mode DMA

## Recommendation

For motors on TIM12 (S7/S8 on FrSky F405):
1. Use standard PWM or OneShot protocols
2. Reserve DShot for motors on TIM1/TIM2/TIM3/TIM4/TIM8 (which have DMA)
3. Document this limitation clearly in target configuration

## Sources

- [TinyGo STM32F405 Reference](https://tinygo.org/docs/reference/microcontrollers/machine/feather-stm32f405/)
- [STM32F405 Port Annotations - GitHub](https://github.com/travisgoodspeed/md380tools/blob/master/annotations/STM32F405_ports.md)
- INAV codebase: `inav/src/main/drivers/timer_stm32f4xx.c`
- INAV codebase: `inav/src/main/drivers/timer_def_stm32f4xx.h`
- STM32 Reference Manual RM0090: [STM32F405/415/407/417/427/437/429/439](https://www.st.com/resource/en/reference_manual/dm00031020-stm32f405-415-stm32f407-417-stm32f427-437-and-stm32f429-439-advanced-arm-based-32-bit-mcus-stmicroelectronics.pdf)
