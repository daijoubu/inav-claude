// Check timer alternatives for ALL SPEEDYBEEF7V3 pins

// From STM32F745 datasheet
const pinTimers = {
  'PA15': ['TIM2_CH1', 'TIM2_ETR'],  // S1
  'PB3':  ['TIM2_CH2'],               // S2
  'PB4':  ['TIM3_CH1'],               // S3
  'PB6':  ['TIM4_CH1'],               // S4
  'PB7':  ['TIM4_CH2'],               // S5
  'PB5':  ['TIM3_CH2'],               // S6
  'PB0':  ['TIM1_CH2N', 'TIM3_CH3', 'TIM8_CH2N'],  // S7
  'PB1':  ['TIM1_CH3N', 'TIM3_CH4', 'TIM8_CH3N'],  // S8
};

const outputs = {
  'S1': 'PA15',
  'S2': 'PB3',
  'S3': 'PB4',
  'S4': 'PB6',
  'S5': 'PB7',
  'S6': 'PB5',
  'S7': 'PB0',
  'S8': 'PB1',
};

console.log('SPEEDYBEEF7V3 Pin Timer Options\n');
console.log('='.repeat(60));

Object.entries(outputs).forEach(([output, pin]) => {
  const timers = pinTimers[pin] || ['UNKNOWN'];
  console.log(`${output} (${pin}):`);
  timers.forEach(t => {
    const complementary = t.includes('N') ? ' [COMPLEMENTARY - may not support DSHOT]' : '';
    console.log(`  - ${t}${complementary}`);
  });
  console.log('');
});

console.log('='.repeat(60));
console.log('\nCONSTRAINTS:');
console.log('- S1 (PA15): Only TIM2_CH1 available');
console.log('- S2 (PB3):  Only TIM2_CH2 available');
console.log('- S3 (PB4):  Only TIM3_CH1 available');
console.log('- S4 (PB6):  Only TIM4_CH1 available');
console.log('- S5 (PB7):  Only TIM4_CH2 available');
console.log('- S6 (PB5):  Only TIM3_CH2 available');
console.log('- S7 (PB0):  TIM1_CH2N, TIM3_CH3, or TIM8_CH2N');
console.log('- S8 (PB1):  TIM1_CH3N, TIM3_CH4, or TIM8_CH3N');

console.log('\n' + '='.repeat(60));
console.log('CONCLUSION:');
console.log('S1-S6 have NO alternatives - they are locked to TIM2, TIM3, TIM4');
console.log('Only S7 and S8 have options.');
console.log('\nIf complementary outputs (CHxN) do NOT support DSHOT:');
console.log('  -> S7 must use TIM3_CH3 (shares with S3)');
console.log('  -> S8 must use TIM3_CH4 (shares with S3)');
console.log('  -> IMPOSSIBLE to have 2 outputs on different timers!');
console.log('\nIf complementary outputs DO support DSHOT:');
console.log('  -> S7 can use TIM1_CH2N or TIM8_CH2N');
console.log('  -> S8 can use TIM1_CH3N or TIM8_CH3N');
console.log('  -> ACHIEVABLE: S7+S8 both on timers not used by S1-S4');
