/*
 * This file is part of INAV.
 *
 * INAV is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * INAV is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with INAV.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <stdint.h>

#include "platform.h"
#include "drivers/io.h"
#include "drivers/pwm_mapping.h"
#include "drivers/timer.h"

/*
 * Timer Allocation for FrSky F405
 *
 * Connector mapping from schematic:
 * - CON1, CON2 (S1, S2): T4 signals
 * - CON3, CON4 (S3, S4): T3 signals
 * - CON5, CON6 (S5, S6): T8 signals
 * - CON7, CON8 (S7, S8): T12 signals
 * - CON9 (S9): T1 signal
 */

timerHardware_t timerHardware[] = {
    // Motor outputs S1-S9 (all confirmed from schematic)
    DEF_TIM(TIM4,  CH1,  PB6,  TIM_USE_OUTPUT_AUTO, 0, 0),  // S1 - Motor 1
    DEF_TIM(TIM4,  CH2,  PB7,  TIM_USE_OUTPUT_AUTO, 0, 0),  // S2 - Motor 2
    DEF_TIM(TIM3,  CH3,  PB0,  TIM_USE_OUTPUT_AUTO, 0, 0),  // S3 - Motor 3
    DEF_TIM(TIM3,  CH4,  PB1,  TIM_USE_OUTPUT_AUTO, 0, 0),  // S4 - Motor 4
    DEF_TIM(TIM8,  CH3,  PC8,  TIM_USE_OUTPUT_AUTO, 0, 1),  // S5 - Motor 5  UP(2,1)
    DEF_TIM(TIM8,  CH4,  PC9,  TIM_USE_OUTPUT_AUTO, 0, 0),  // S6 - Motor 6  UP(2,1)
    DEF_TIM(TIM12, CH1,  PB14, TIM_USE_OUTPUT_AUTO, 0, 0),  // S7 - Motor 7  ⚠️ no DMA/Dshot
    DEF_TIM(TIM12, CH2,  PB15, TIM_USE_OUTPUT_AUTO, 0, 0),  // S8 - Motor 8  ⚠️ no DMA/Dshot
    DEF_TIM(TIM1,  CH1,  PA8,  TIM_USE_OUTPUT_AUTO, 0, 0),  // S9 - Motor 9  UP(2,5)

    // LED Strip on CON23 - PA15 (T2_1 signal on schematic)
    DEF_TIM(TIM2,  CH1,  PA15, TIM_USE_LED, 0, 0),  // LED strip output (CON23)
};

const int timerHardwareCount = sizeof(timerHardware) / sizeof(timerHardware[0]);

/*
 * IMPLEMENTATION NOTES:
 *
 * 1. All 9 motor outputs (S1-S9) have confirmed timer assignments ✅
 *
 * 2. TIM12 LIMITATION (S7, S8):
 *    - TIM12 has no DMA support on STM32F405
 *    - ✅ Works: Standard PWM, OneShot125, OneShot42, MultiShot
 *    - ❌ Does NOT work: Dshot (all variants), ProShot
 *    - Recommendation: Use S7/S8 for non-Dshot ESCs or servos
 *
 * 3. LED strip output confirmed: PA15 (T2_1) on CON23 with TIM2_CH1 ✅
 *
 * 4. DMA conflict checking:
 *    - Used claude/developer/scripts/analysis/dma_conflict_analyzer.py
 *
 * 5. Testing with physical board:
 *    - Verify all 9 motor outputs work correctly
 *    - Test S7/S8 with PWM/OneShot ESCs (not Dshot)
 *    - Test PC14 SD card reliability
 *    - Test LED strip output on CON23 (PA15)
 */
