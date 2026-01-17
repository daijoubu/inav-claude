#!/usr/bin/env python3
"""
Analyze DMA conflicts for INAV flight controller target configurations

Based on INAV timer definitions and STM32 reference manual DMA mappings.
"""

# DMA mappings for F405 (from dma_resolver.html and INAV timer_def_stm32f4xx.h)
dma_map_f405 = {
    'TIM1_CH1': [[2,6,0], [2,1,6], [2,3,6]],
    'TIM1_CH2': [[2,6,0], [2,2,6]],
    'TIM1_CH3': [[2,6,0], [2,6,6]],
    'TIM1_CH4': [[2,4,6]],
    'TIM2_CH1': [[1,5,3]],
    'TIM2_CH2': [[1,6,3]],
    'TIM2_CH3': [[1,1,3]],
    'TIM2_CH4': [[1,7,3], [1,6,3]],
    'TIM3_CH1': [[1,4,5]],
    'TIM3_CH2': [[1,5,5]],
    'TIM3_CH3': [[1,7,5]],
    'TIM3_CH4': [[1,2,5]],
    'TIM4_CH1': [[1,0,2]],
    'TIM4_CH2': [[1,3,2]],
    'TIM4_CH3': [[1,7,2]],
    'TIM5_CH1': [[1,2,6]],
    'TIM5_CH2': [[1,4,6]],
    'TIM5_CH3': [[1,0,6]],
    'TIM5_CH4': [[1,1,6], [1,3,6]],
    'TIM8_CH1': [[2,2,0], [2,2,7]],
    'TIM8_CH2': [[2,2,0], [2,3,7]],
    'TIM8_CH3': [[2,2,0], [2,4,7]],
    'TIM8_CH4': [[2,7,7]],
    # TIM12 - EXISTS on F405 but has NO DMA support!
    'TIM12_CH1': [],  # NO DMA
    'TIM12_CH2': [],  # NO DMA
}

# Timer configuration from target.c - FrSky F405
timers = [
    {'name': 'S1 - Motor 1', 'tim': 'TIM4', 'ch': 'CH1', 'pin': 'PB6', 'dma_flag': 0},
    {'name': 'S2 - Motor 2', 'tim': 'TIM4', 'ch': 'CH2', 'pin': 'PB7', 'dma_flag': 0},
    {'name': 'S3 - Motor 3', 'tim': 'TIM3', 'ch': 'CH3', 'pin': 'PB0', 'dma_flag': 0},
    {'name': 'S4 - Motor 4', 'tim': 'TIM3', 'ch': 'CH4', 'pin': 'PB1', 'dma_flag': 0},
    {'name': 'S5 - Motor 5', 'tim': 'TIM8', 'ch': 'CH3', 'pin': 'PC8', 'dma_flag': 1},
    {'name': 'S6 - Motor 6', 'tim': 'TIM8', 'ch': 'CH4', 'pin': 'PC9', 'dma_flag': 0},
    {'name': 'S7 - Motor 7', 'tim': 'TIM12', 'ch': 'CH1', 'pin': 'PB14', 'dma_flag': 0},
    {'name': 'S8 - Motor 8', 'tim': 'TIM12', 'ch': 'CH2', 'pin': 'PB15', 'dma_flag': 0},
    {'name': 'S9 - Motor 9', 'tim': 'TIM1', 'ch': 'CH1', 'pin': 'PA8', 'dma_flag': 0},
    {'name': 'LED strip', 'tim': 'TIM2', 'ch': 'CH1', 'pin': 'PA15', 'dma_flag': 0},
]

# UART DMA streams (from target.h - all 6 UARTs enabled)
# Note: INAV typically uses INTERRUPT mode, not DMA mode for UARTs
uart_dma = [
    {'name': 'UART1_RX', 'dma': [2, 2]},
    {'name': 'UART1_TX', 'dma': [2, 7]},
    {'name': 'UART2_RX', 'dma': [1, 5]},
    {'name': 'UART2_TX', 'dma': [1, 6]},
    {'name': 'UART3_RX', 'dma': [1, 1]},
    {'name': 'UART3_TX', 'dma': [1, 3]},
    {'name': 'UART4_RX', 'dma': [1, 2]},
    {'name': 'UART4_TX', 'dma': [1, 4]},
    {'name': 'UART5_RX', 'dma': [1, 0]},
    {'name': 'UART5_TX', 'dma': [1, 7]},
    {'name': 'UART6_RX', 'dma': [2, 1]},
    {'name': 'UART6_TX', 'dma': [2, 6]},
]

# ADC DMA (from target.h)
adc_dma = [
    {'name': 'ADC1', 'dma': [2, 0]},
]

def analyze_dma_conflicts():
    print("="*80)
    print("DMA CONFLICT ANALYSIS - FrSky F405")
    print("="*80)
    print()

    # Resolve timer DMA streams
    used_streams = {}
    timer_dma_assignments = []
    warnings = []
    errors = []

    print("TIMER DMA ASSIGNMENTS:")
    print("-"*80)

    for timer in timers:
        key = f"{timer['tim']}_{timer['ch']}"

        if key not in dma_map_f405:
            errors.append(f"❌ {timer['name']}: No DMA mapping for {key}")
            print(f"❌ {timer['name']:20s} {key:12s} {timer['pin']:6s} - NO DMA MAPPING")
            continue

        dma_options = dma_map_f405[key]

        # Check for NO DMA support (empty list)
        if len(dma_options) == 0:
            warnings.append(f"⚠️  {timer['name']}: TIM12 has NO DMA - PWM/OneShot only, NO DShot!")
            print(f"⚠️  {timer['name']:20s} {key:12s} {timer['pin']:6s} → NO DMA (PWM/OneShot only)")
            continue

        dma_flag = timer['dma_flag']

        if dma_flag >= len(dma_options):
            errors.append(f"❌ {timer['name']}: DMA flag {dma_flag} out of range (max {len(dma_options)-1})")
            print(f"❌ {timer['name']:20s} {key:12s} {timer['pin']:6s} - INVALID DMA FLAG")
            continue

        dma = dma_options[dma_flag]
        dma_str = f"DMA{dma[0]} Stream {dma[1]}"
        stream_key = f"DMA{dma[0]}_S{dma[1]}"

        timer_dma_assignments.append({
            'name': timer['name'],
            'key': key,
            'pin': timer['pin'],
            'dma': dma,
            'dma_str': dma_str,
            'stream_key': stream_key
        })

        if stream_key in used_streams:
            errors.append(f"🔴 CONFLICT: {timer['name']} and {used_streams[stream_key]} both use {dma_str}")
            print(f"🔴 {timer['name']:20s} {key:12s} {timer['pin']:6s} → {dma_str:20s} ❌ CONFLICT!")
        else:
            used_streams[stream_key] = timer['name']
            print(f"✓  {timer['name']:20s} {key:12s} {timer['pin']:6s} → {dma_str}")

    print()
    print("PERIPHERAL DMA USAGE (UART only uses DMA if configured, SPI uses polling in INAV):")
    print("-"*80)
    print("Note: INAV typically uses INTERRUPT mode for UARTs, not DMA")
    print("      Only reserve these streams if USE_UART_DMA is defined")
    print()

    # Check UART conflicts (but note they're usually not used)
    for uart in uart_dma:
        dma_str = f"DMA{uart['dma'][0]} Stream {uart['dma'][1]}"
        stream_key = f"DMA{uart['dma'][0]}_S{uart['dma'][1]}"

        if stream_key in used_streams:
            warnings.append(f"⚠️  {uart['name']} would conflict with {used_streams[stream_key]} on {dma_str} (if UART DMA enabled)")
            print(f"⚠️  {uart['name']:20s} → {dma_str:20s} (conflicts with {used_streams[stream_key]} if enabled)")
        else:
            print(f"    {uart['name']:20s} → {dma_str:20s} (reserved if UART DMA enabled)")

    print()

    # Check ADC
    for adc in adc_dma:
        dma_str = f"DMA{adc['dma'][0]} Stream {adc['dma'][1]}"
        stream_key = f"DMA{adc['dma'][0]}_S{adc['dma'][1]}"

        if stream_key in used_streams:
            errors.append(f"🔴 CONFLICT: {adc['name']} and {used_streams[stream_key]} both use {dma_str}")
            print(f"🔴 {adc['name']:20s} → {dma_str:20s} ❌ CONFLICT with {used_streams[stream_key]}!")
        else:
            used_streams[stream_key] = adc['name']
            print(f"✓  {adc['name']:20s} → {dma_str:20s}")

    print()
    print("="*80)
    print("SUMMARY:")
    print("="*80)

    if errors:
        print(f"\n🔴 {len(errors)} CRITICAL ERROR(S) FOUND:\n")
        for error in errors:
            print(f"   {error}")

    if warnings:
        print(f"\n⚠️  {len(warnings)} WARNING(S):\n")
        for warning in warnings:
            print(f"   {warning}")

    if not errors and not warnings:
        print("\n✅ NO CONFLICTS FOUND!")
        print("   All timer outputs have unique DMA streams")
        print("   UART DMA streams won't conflict (INAV uses interrupts by default)")
    elif not errors:
        print("\n✅ NO DMA CONFLICTS!")
        print("   All timer outputs with DMA support have unique streams")
        print("   TIM12 limitation noted (see warnings above)")

    print()
    print("="*80)

if __name__ == '__main__':
    analyze_dma_conflicts()
