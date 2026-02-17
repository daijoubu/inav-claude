// Analyze SPEEDYBEEF7V3 timer assignments for DMA conflicts
import { dmaMapF7, pinAlternatesCommon } from './dma_maps.js';

// Current configuration from target.c
const currentConfig = [
  { output: 'S1', pin: 'PA15', timer: 'TIM2', channel: 'CH1' },
  { output: 'S2', pin: 'PB3',  timer: 'TIM2', channel: 'CH2' },
  { output: 'S3', pin: 'PB4',  timer: 'TIM3', channel: 'CH1' },
  { output: 'S4', pin: 'PB6',  timer: 'TIM4', channel: 'CH1' },
  { output: 'S5', pin: 'PB7',  timer: 'TIM4', channel: 'CH2' }, // Shares TIM4 with S4
  { output: 'S6', pin: 'PB5',  timer: 'TIM3', channel: 'CH2' }, // Shares TIM3 with S3, DSHOT conflict
  { output: 'S7', pin: 'PB0',  timer: 'TIM3', channel: 'CH3' }, // Shares TIM3 with S3
  { output: 'S8', pin: 'PB1',  timer: 'TIM3', channel: 'CH4' }, // Shares TIM3 with S3
  { output: 'LED', pin: 'PC8', timer: 'TIM8', channel: 'CH3' },
  { output: 'CAM', pin: 'PA0', timer: 'TIM5', channel: 'CH1' },
];

// Pin alternate timer capabilities from STM32F745 datasheet
const pinAlternatives = {
  'PB0': ['TIM1_CH2N', 'TIM3_CH3', 'TIM8_CH2N'],
  'PB1': ['TIM1_CH3N', 'TIM3_CH4', 'TIM8_CH3N'],
  'PB5': ['TIM3_CH2'],
  'PB7': ['TIM4_CH2'],
};

function parseTimerChannel(timerChannel) {
  // Parse strings like "TIM1_CH2N" or "TIM3_CH3"
  const match = timerChannel.match(/TIM(\d+)_CH(\d+)(N?)/);
  if (!match) return null;
  return {
    timer: `TIM${match[1]}`,
    channel: `CH${match[2]}${match[3]}`,
    isComplementary: match[3] === 'N'
  };
}

function getDmaStream(timer, channel) {
  const key = `${timer}_${channel}`;
  const dmaInfo = dmaMapF7[key];
  if (!dmaInfo) return null;

  // dmaMapF7 format is typically [controller, stream, channel]
  return dmaInfo;
}

function analyzeDmaConflicts(config) {
  const dmaUsage = {};
  const conflicts = [];

  config.forEach(item => {
    const dma = getDmaStream(item.timer, item.channel);
    if (!dma) {
      console.log(`⚠️  ${item.output} (${item.pin}): No DMA mapping found for ${item.timer}_${item.channel}`);
      return;
    }

    const [controller, stream, dmaChannel] = dma;
    const streamKey = `DMA${controller}_Stream${stream}`;

    if (dmaUsage[streamKey]) {
      conflicts.push({
        stream: streamKey,
        outputs: [dmaUsage[streamKey].output, item.output],
        pins: [dmaUsage[streamKey].pin, item.pin],
        timers: [dmaUsage[streamKey].timer, item.timer]
      });
    }

    dmaUsage[streamKey] = item;
  });

  return { dmaUsage, conflicts };
}

function printConfig(config, title) {
  console.log(`\n${'='.repeat(60)}`);
  console.log(title);
  console.log('='.repeat(60));

  config.forEach(item => {
    const dma = getDmaStream(item.timer, item.channel);
    const dmaStr = dma ? `DMA${dma[0]}_S${dma[1]}_Ch${dma[2]}` : 'NO_DMA';
    console.log(`${item.output.padEnd(4)} ${item.pin.padEnd(5)} ${item.timer}_${item.channel.padEnd(4)} -> ${dmaStr}`);
  });
}

function suggestAlternatives() {
  console.log(`\n${'='.repeat(60)}`);
  console.log('ALTERNATIVE TIMER OPTIONS FOR S5-S8');
  console.log('='.repeat(60));

  Object.entries(pinAlternatives).forEach(([pin, alternatives]) => {
    const output = currentConfig.find(c => c.pin === pin)?.output || pin;
    console.log(`\n${output} (${pin}):`);

    alternatives.forEach(alt => {
      const parsed = parseTimerChannel(alt);
      if (!parsed) return;

      const dma = getDmaStream(parsed.timer, parsed.channel);
      const dmaStr = dma ? `DMA${dma[0]}_S${dma[1]}_Ch${dma[2]}` : 'NO_DMA';
      const note = parsed.isComplementary ? ' (complementary output)' : '';
      console.log(`  ${alt.padEnd(15)} -> ${dmaStr}${note}`);
    });
  });
}

// Main analysis
console.log('\n🔍 SPEEDYBEEF7V3 Timer/DMA Analysis');

printConfig(currentConfig, 'CURRENT CONFIGURATION');

const { dmaUsage, conflicts } = analyzeDmaConflicts(currentConfig);

console.log(`\n${'='.repeat(60)}`);
console.log('DMA CONFLICTS');
console.log('='.repeat(60));

if (conflicts.length === 0) {
  console.log('✅ No DMA conflicts detected!');
} else {
  conflicts.forEach(conflict => {
    console.log(`\n❌ ${conflict.stream} CONFLICT:`);
    console.log(`   ${conflict.outputs[0]} (${conflict.pins[0]}, ${conflict.timers[0]}) vs ${conflict.outputs[1]} (${conflict.pins[1]}, ${conflict.timers[1]})`);
  });
}

// Timer sharing analysis
console.log(`\n${'='.repeat(60)}`);
console.log('TIMER SHARING ANALYSIS');
console.log('='.repeat(60));

const timerUsage = {};
currentConfig.forEach(item => {
  if (!timerUsage[item.timer]) timerUsage[item.timer] = [];
  timerUsage[item.timer].push(`${item.output} (${item.pin})`);
});

Object.entries(timerUsage).forEach(([timer, outputs]) => {
  if (outputs.length > 1) {
    console.log(`\n⚠️  ${timer} shared by: ${outputs.join(', ')}`);
  }
});

suggestAlternatives();

console.log(`\n${'='.repeat(60)}`);
console.log('RECOMMENDATIONS');
console.log('='.repeat(60));
console.log(`
Motors (S1-S4) use: TIM2, TIM3, TIM4
Servos (S5-S8) currently use: TIM4 (S5), TIM3 (S6-S8)

GOAL: At least 2 of S5-S8 should use timers NOT in {TIM2, TIM3, TIM4}

OPTIONS:
1. S7 (PB0): Use TIM1_CH2N or TIM8_CH2N (both avoid TIM2/3/4)
2. S8 (PB1): Use TIM1_CH3N or TIM8_CH3N (both avoid TIM2/3/4)
3. S5 (PB7): Only supports TIM4_CH2 (no alternatives)
4. S6 (PB5): Only supports TIM3_CH2 (no alternatives)

RECOMMENDED SOLUTION:
- Keep S1-S4 as-is (motors work fine)
- Keep S5 (PB7) on TIM4_CH2 (no choice)
- Keep S6 (PB5) on TIM3_CH2 (no choice, but check DMA conflict)
- Change S7 (PB0) to TIM1_CH2N or TIM8_CH2N
- Change S8 (PB1) to TIM1_CH3N or TIM8_CH3N
`);
