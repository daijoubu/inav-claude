import { dmaMapF7 } from './dma_maps.js';

console.log('Checking DMA support for TIM1 channels:\n');

const channels = [
  'TIM1_CH1',
  'TIM1_CH1N',
  'TIM1_CH2',
  'TIM1_CH2N',
  'TIM1_CH3',
  'TIM1_CH3N',
  'TIM1_CH4'
];

channels.forEach(ch => {
  const dma = dmaMapF7[ch];
  if (dma) {
    const padded = ch + ' '.repeat(Math.max(0, 12 - ch.length));
    console.log(`${padded}: DMA${dma[0]}_Stream${dma[1]}_Channel${dma[2]}`);
  } else {
    const padded = ch + ' '.repeat(Math.max(0, 12 - ch.length));
    console.log(`${padded}: NO DMA MAPPING`);
  }
});

console.log('\nConclusion:');
console.log('If CHxN channels have DMA mappings, they CAN support DSHOT.');
console.log('If CHxN channels show NO DMA, they can only do standard PWM (servos).');
