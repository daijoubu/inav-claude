// dma_resolver_optimized.js - CLEANED UP VERSION

import {
  dmaMapAT32F435,
  dmaMapF405,
  dmaMapF7,
  dmaMapH7,
  burstDmaMapF405,
  burstDmaMapF7,
  burstDmaMapH7,
  burstDmaMapAT32F435,
  pinAlternatesCommon,
  pinAlternatesAT32F435
} from './dma_maps.js';

export const getDmaMap = (mcuType) => {
  switch(mcuType) {
    case 'F405': return dmaMapF405;
    case 'F745': return dmaMapF7;
    case 'H743': return dmaMapH7;
    case 'AT32F435': return dmaMapAT32F435;
    default: 
      console.warn(`Unknown MCU type: ${mcuType}, defaulting to F405`);
      return dmaMapF405;
  }
};

export const getBurstDmaMap = (mcuType) => {
  switch(mcuType) {
    case 'F405': return burstDmaMapF405;
    case 'F745': return burstDmaMapF7;
    case 'H743': return burstDmaMapH7;
    case 'AT32F435': return burstDmaMapAT32F435;
    default: 
      console.warn(`Unknown MCU type: ${mcuType}, defaulting to F405`);
      return burstDmaMapF405;
  }
};

export const parseBetaflightTimerMap = (text) => {
  const lines = text.split('\n');
  const mapping = [];
  
  lines.forEach(line => {
    const match = line.match(/TIMER_PIN_MAP\s*\(\s*(\d+)\s*,\s*(\w+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)/);
    if (match) {
      const [, index, pin, dmaOpt, timerIdx] = match;
      mapping.push({
        index: parseInt(index),
        pin: pin.trim(),
        dmaOpt: parseInt(dmaOpt),
        timerIdx: parseInt(timerIdx)
      });
    }
  });
  
  return mapping;
};

export const parseTargetH = (text, mcuType, includeUart = false, includeSpi = false) => {
  const spiDma = [];
  
  const spi1Match = includeSpi && text.match(/SPI1_SCK_PIN\s+(\w+)/);
  const spi2Match = includeSpi && text.match(/SPI2_SCK_PIN\s+(\w+)/);
  const spi3Match = includeSpi && text.match(/SPI3_SCK_PIN\s+(\w+)/);
  
  const uart1Match = includeUart && text.match(/USE_UART1/);
  const uart2Match = includeUart && text.match(/USE_UART2/);
  const uart3Match = includeUart && text.match(/USE_UART3/);
  const uart4Match = includeUart && text.match(/USE_UART4/);
  const uart5Match = includeUart && text.match(/USE_UART5/);
  const uart6Match = includeUart && text.match(/USE_UART6/);
  const uart7Match = includeUart && text.match(/USE_UART7/);
  const uart8Match = includeUart && text.match(/USE_UART8/);
  
  if (mcuType === 'AT32F435') {
    if (spi1Match) {
      spiDma.push({ name: 'SPI1_RX', dma: [2, 1] });
      spiDma.push({ name: 'SPI1_TX', dma: [2, 2] });
    }
    if (spi2Match) {
      spiDma.push({ name: 'SPI2_RX', dma: [1, 3] });
      spiDma.push({ name: 'SPI2_TX', dma: [1, 4] });
    }
    if (spi3Match) {
      spiDma.push({ name: 'SPI3_RX', dma: [1, 5] });
      spiDma.push({ name: 'SPI3_TX', dma: [1, 6] });
    }
    
    if (uart1Match) {
      spiDma.push({ name: 'UART1_RX', dma: [2, 3] });
      spiDma.push({ name: 'UART1_TX', dma: [2, 4] });
    }
    if (uart2Match) {
      spiDma.push({ name: 'UART2_RX', dma: [1, 5] });
      spiDma.push({ name: 'UART2_TX', dma: [1, 6] });
    }
    if (uart3Match) {
      spiDma.push({ name: 'UART3_RX', dma: [1, 1] });
      spiDma.push({ name: 'UART3_TX', dma: [1, 2] });
    }
    if (uart4Match) {
      spiDma.push({ name: 'UART4_RX', dma: [1, 3] });
      spiDma.push({ name: 'UART4_TX', dma: [1, 4] });
    }
    if (uart5Match) {
      spiDma.push({ name: 'UART5_RX', dma: [1, 7] });
      spiDma.push({ name: 'UART5_TX', dma: [2, 1] });
    }
    if (uart6Match) {
      spiDma.push({ name: 'UART6_RX', dma: [2, 5] });
      spiDma.push({ name: 'UART6_TX', dma: [2, 6] });
    }
    if (uart7Match) {
      spiDma.push({ name: 'UART7_RX', dma: [2, 7] });
      spiDma.push({ name: 'UART7_TX', dma: [1, 1] });
    }
    if (uart8Match) {
      spiDma.push({ name: 'UART8_RX', dma: [1, 2] });
      spiDma.push({ name: 'UART8_TX', dma: [1, 3] });
    }
  } else if (mcuType === 'F405' || mcuType === 'F745') {
    if (spi1Match) {
      spiDma.push({ name: 'SPI1_RX', dma: [2, 0] });
      spiDma.push({ name: 'SPI1_TX', dma: [2, 3] });
    }
    if (spi2Match) {
      spiDma.push({ name: 'SPI2_RX', dma: [1, 3] });
      spiDma.push({ name: 'SPI2_TX', dma: [1, 4] });
    }
    if (spi3Match) {
      spiDma.push({ name: 'SPI3_RX', dma: [1, 0] });
      spiDma.push({ name: 'SPI3_TX', dma: [1, 5] });
    }
    
    if (uart1Match) {
      spiDma.push({ name: 'UART1_RX', dma: [2, 2] });
      spiDma.push({ name: 'UART1_TX', dma: [2, 7] });
    }
    if (uart2Match) {
      spiDma.push({ name: 'UART2_RX', dma: [1, 5] });
      spiDma.push({ name: 'UART2_TX', dma: [1, 6] });
    }
    if (uart3Match) {
      spiDma.push({ name: 'UART3_RX', dma: [1, 1] });
      spiDma.push({ name: 'UART3_TX', dma: [1, 3] });
    }
    if (uart4Match) {
      spiDma.push({ name: 'UART4_RX', dma: [1, 2] });
      spiDma.push({ name: 'UART4_TX', dma: [1, 4] });
    }
    if (uart5Match) {
      spiDma.push({ name: 'UART5_RX', dma: [1, 0] });
      spiDma.push({ name: 'UART5_TX', dma: [1, 7] });
    }
    if (uart6Match) {
      spiDma.push({ name: 'UART6_RX', dma: [2, 1] });
      spiDma.push({ name: 'UART6_TX', dma: [2, 6] });
    }
  }
  
  return spiDma;
};

export const parseInput = (text) => {
  const lines = text.split('\n');
  const timers = [];
  
  lines.forEach((line, lineNum) => {
    const match = line.match(/DEF_TIM\s*\(\s*(\w+)\s*,\s*(\w+)\s*,\s*(\w+)\s*,\s*([^,]+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)\s*,?\s*(?:\/\/\s*(.+))?/);
    if (match) {
      const [, tim, ch, pin, usage, dmaOpt1, dmaOpt2, name] = match;
      const cleanUsage = usage.trim().replace(/^TIM_USE_/, '');
      timers.push({
        name: name ? name.trim() : `Output${lineNum}`,
        tim: tim.trim(),
        ch: ch.trim(),
        pin: pin.trim(),
        usage: cleanUsage,
        originalTim: tim.trim(),
        originalCh: ch.trim(),
        inputDmaFlag: parseInt(dmaOpt2)
      });
    }
  });
  
  return timers;
};

export const dmaToString = (dma, mcuType) => {
  if (mcuType === 'AT32F435') {
    return `DMA${dma[0]} Channel ${dma[1] + 1}`;
  }
  return mcuType === 'H743' 
    ? `DMA${dma[0]} Stream ${dma[1]}` 
    : `DMA${dma[0]} Stream ${dma[1]}`;
};

export const checkConflictsBurst = (timers, burstDmaMap, reservedDma = []) => {
  const usedStreams = new Map();
  const timerGroups = new Map();
  const conflicts = [];

  reservedDma.forEach(res => {
    const streamKey = `${res.dma[0]}_${res.dma[1]}`;
    usedStreams.set(streamKey, res.name);
  });

  timers.forEach(timer => {
    if (!timerGroups.has(timer.tim)) {
      timerGroups.set(timer.tim, []);
    }
    timerGroups.get(timer.tim).push(timer.name);
  });

  timerGroups.forEach((outputs, tim) => {
    const dmaOptions = burstDmaMap[tim];
    
    if (!dmaOptions) {
      conflicts.push({
        type: 'missing_burst_dma',
        issue: `No burst DMA mapping for ${tim}`
      });
      return;
    }

    let foundStream = false;
    for (const dma of dmaOptions) {
      const streamKey = `${dma[0]}_${dma[1]}`;
      if (!usedStreams.has(streamKey)) {
        usedStreams.set(streamKey, `${tim}_BURST (${outputs.join(', ')})`);
        foundStream = true;
        break;
      }
    }

    if (!foundStream) {
      conflicts.push({
        type: 'burst_dma_conflict',
        issue: `${tim} burst mode needs DMA stream but all options conflict`
      });
    }
  });

  return { conflicts, timerGroups, usedStreams };
};

export const checkConflicts = (timers, dmaFlags, dmaMap, reservedDma = []) => {
  const usedStreams = new Map();
  const usedTimerChannels = new Map();
  const conflicts = [];

  reservedDma.forEach(res => {
    const streamKey = `${res.dma[0]}_${res.dma[1]}`;
    usedStreams.set(streamKey, res.name);
  });

  timers.forEach((timer, idx) => {
    const key = `${timer.tim}_${timer.ch}`;
    
    if (usedTimerChannels.has(key)) {
      conflicts.push({
        type: 'timer_channel',
        timer1: usedTimerChannels.get(key),
        timer2: timer.name,
        issue: `Both use ${key} (same timer channel can't drive two pins)`
      });
    } else {
      usedTimerChannels.set(key, timer.name);
    }
    
    const dmaOptions = dmaMap[key];
    
    if (!dmaOptions) {
      conflicts.push({
        type: 'missing_dma',
        timer: timer.name,
        issue: `No DMA mapping for ${key}`
      });
      return;
    }
    
    const opt = dmaFlags[idx];
    if (opt >= dmaOptions.length) return;
    
    const dma = dmaOptions[opt];
    const streamKey = `${dma[0]}_${dma[1]}`;
    
    if (usedStreams.has(streamKey)) {
      conflicts.push({
        type: 'dma_stream',
        timer1: usedStreams.get(streamKey),
        timer2: timer.name,
        stream: `DMA${dma[0]} Stream/Ch ${dma[1]}`
      });
    } else {
      usedStreams.set(streamKey, timer.name);
    }
  });

  return conflicts;
};

// OPTIMIZED SOLVER with proper short-circuiting and limits
const solveWithBacktracking = (baseTimers, dmaMap, reservedDma, tryAlternates, mcuType) => {
  console.log('Starting optimized backtracking solver...');
  
  // Pre-build reserved DMA set for O(1) lookup
  const reservedDmaSet = new Set();
  reservedDma.forEach(res => {
    const key = `${res.dma[0]}_${res.dma[1]}`;
    reservedDmaSet.add(key);
  });
  
  // Count available DMA channels
  const totalDmaChannels = mcuType === 'AT32F435' ? 14 : 
                          mcuType === 'H743' ? 16 : 14;
  const availableDma = totalDmaChannels - reservedDmaSet.size;
  
  console.log(`MCU: ${mcuType}, Outputs: ${baseTimers.length}, Available DMA: ${availableDma}/${totalDmaChannels}`);
  
  // Early impossibility check
  if (baseTimers.length > availableDma) {
    console.log(`⚠ Warning: ${baseTimers.length} outputs but only ${availableDma} DMA channels available - solution may not exist`);
  }
  
  // Track statistics
  let nodesExplored = 0;
  let nodesPruned = 0;
  const startTime = Date.now();
  
  // Select the correct pin alternates table
  const pinAlternates = mcuType === 'AT32F435' ? pinAlternatesAT32F435 : pinAlternatesCommon;
  
  // Build timer channel usage map to detect conflicts early
  const timerChannelMap = new Map();
  baseTimers.forEach((timer, idx) => {
    const alternates = tryAlternates 
      ? (pinAlternates[timer.pin] || [{ tim: timer.tim, ch: timer.ch }])
      : [{ tim: timer.tim, ch: timer.ch }];
    
    timerChannelMap.set(idx, alternates.map(alt => ({
      ...timer,
      tim: alt.tim,
      ch: alt.ch,
      isAlt: alt.tim !== timer.originalTim || alt.ch !== timer.originalCh
    })));
  });
  
  // Recursive backtracking with constraint propagation
  const solve = (outputIdx, usedTimerChannels, usedDmaStreams, assignments) => {
    nodesExplored++;
    
    // Safety limit - stop if exploring too many nodes
    if (nodesExplored > 1000000) {
      console.log('⚠ Search limit reached (1M nodes) - stopping search');
      return null;
    }
    
    // Periodic progress update for long searches
    if (nodesExplored % 50000 === 0) {
      const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
      console.log(`Progress: ${nodesExplored.toLocaleString()} nodes (${nodesPruned.toLocaleString()} pruned) in ${elapsed}s - output ${outputIdx}/${baseTimers.length}`);
    }
    
    // Base case: all outputs assigned
    if (outputIdx === baseTimers.length) {
      const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
      console.log(`✓ Solution found! Explored ${nodesExplored.toLocaleString()} nodes, pruned ${nodesPruned.toLocaleString()} in ${elapsed}s`);
      return assignments;
    }
    
    // Get possible timer configurations for this output
    const timerOptions = timerChannelMap.get(outputIdx);
    
    for (const timerConfig of timerOptions) {
      const timerKey = `${timerConfig.tim}_${timerConfig.ch}`;
      
      // SHORT-CIRCUIT 1: Check timer channel conflict
      if (usedTimerChannels.has(timerKey)) {
        nodesPruned++;
        continue;
      }
      
      // Get DMA options for this timer/channel combo
      const dmaOptions = dmaMap[timerKey];
      if (!dmaOptions || dmaOptions.length === 0) {
        nodesPruned++;
        continue;
      }
      
      // Try each DMA option
      for (let dmaIdx = 0; dmaIdx < dmaOptions.length; dmaIdx++) {
        const dma = dmaOptions[dmaIdx];
        const dmaKey = `${dma[0]}_${dma[1]}`;
        
        // SHORT-CIRCUIT 2: Check DMA stream conflict
        if (usedDmaStreams.has(dmaKey) || reservedDmaSet.has(dmaKey)) {
          nodesPruned++;
          continue;
        }
        
        // Valid assignment - recurse
        const newUsedTimers = new Map(usedTimerChannels);
        newUsedTimers.set(timerKey, timerConfig.name);
        
        const newUsedDma = new Map(usedDmaStreams);
        newUsedDma.set(dmaKey, timerConfig.name);
        
        const newAssignments = [...assignments, {
          ...timerConfig,
          dmaFlag: dmaIdx,
          dma: dmaToString(dma, mcuType),
          options: dmaOptions.length
        }];
        
        const result = solve(outputIdx + 1, newUsedTimers, newUsedDma, newAssignments);
        if (result) {
          return result;
        }
      }
    }
    
    // No valid assignment found for this output
    return null;
  };
  
  const result = solve(0, new Map(), new Map(), []);
  
  const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
  if (!result) {
    console.log(`✗ No solution found. Explored ${nodesExplored.toLocaleString()} nodes, pruned ${nodesPruned.toLocaleString()} in ${elapsed}s`);
  }
  
  return result;
};

export const findSolution = (
  baseTimers, 
  reservedDma, 
  bfMapping, 
  mcuType, 
  tryAlternates, 
  dmaMap, 
  burstDmaMap
) => {
  let bestSolution = null;

  // PHASE 0: Check if user's original input configuration works
  if (!bfMapping.length) {
    console.log('Phase 0: Checking user input configuration...');
    
    const inputDmaFlags = baseTimers.map(t => t.inputDmaFlag || 0);
    
    const conflicts = checkConflicts(baseTimers, inputDmaFlags, dmaMap, reservedDma);
    
    if (conflicts.length === 0) {
      const details = inputDmaFlags.map((opt, idx) => {
        const timer = baseTimers[idx];
        const key = `${timer.tim}_${timer.ch}`;
        const dmaOptions = dmaMap[key];
        const dma = dmaOptions && opt < dmaOptions.length ? dmaOptions[opt] : null;
        
        return {
          ...timer,
          dmaFlag: opt,
          dma: dma ? dmaToString(dma, mcuType) : 'NONE',
          options: dmaOptions ? dmaOptions.length : 0
        };
      });
      
      bestSolution = { 
        success: true, 
        details, 
        burstMode: false,
        reservedDma: reservedDma,
        source: 'Original Input (no changes needed)'
      };
      console.log('✓ Original input configuration works - no changes needed!');
      return bestSolution;
    } else {
      console.log(`Original input has ${conflicts.length} conflict(s) - will search for alternative`);
    }
  }

  // Check if Betaflight mapping is provided
  if (bfMapping.length > 0) {
    console.log('Using Betaflight TIMER_PIN_MAP configuration...');
    
    const details = baseTimers.map(timer => {
      const bfEntry = bfMapping.find(bf => bf.pin === timer.pin);
      
      if (bfEntry) {
        const key = `${timer.tim}_${timer.ch}`;
        const dmaOptions = dmaMap[key];
        const dma = dmaOptions && bfEntry.dmaOpt < dmaOptions.length 
          ? dmaOptions[bfEntry.dmaOpt] 
          : null;
        
        return {
          ...timer,
          dmaFlag: bfEntry.dmaOpt,
          dma: dma ? dmaToString(dma, mcuType) : 'UNKNOWN',
          options: dmaOptions ? dmaOptions.length : 0,
          source: 'Betaflight'
        };
      } else {
        return {
          ...timer,
          dmaFlag: 0,
          dma: 'NOT_IN_BF_MAP',
          options: 0,
          source: 'Default'
        };
      }
    });
    
    const conflicts = checkConflicts(details.map(d => ({
      ...d,
      tim: d.tim,
      ch: d.ch,
      name: d.name
    })), details.map(d => d.dmaFlag), dmaMap, reservedDma);
    
    if (conflicts.length === 0) {
      bestSolution = { 
        success: true, 
        details, 
        burstMode: false,
        reservedDma: reservedDma,
        source: 'Betaflight TIMER_PIN_MAP'
      };
      return bestSolution;
    } else {
      console.warn(`Betaflight config has ${conflicts.length} conflict(s)`);
    }
  }

  // PHASE 1: Try optimized non-burst mode solver
  if (!bestSolution) {
    console.log('Phase 1: Trying optimized non-burst mode solver...');
    
    const solution = solveWithBacktracking(baseTimers, dmaMap, reservedDma, tryAlternates, mcuType);
    
    if (solution) {
      bestSolution = {
        success: true,
        details: solution,
        burstMode: false,
        reservedDma: reservedDma,
        source: 'Optimized Solver'
      };
    }
  }

  // PHASE 2: If no solution found, try burst mode (NOT for AT32F435)
  if (!bestSolution && mcuType !== 'AT32F435') {
    console.log('Phase 2: Non-burst failed, trying burst mode...');
    
    const burstResult = checkConflictsBurst(baseTimers, burstDmaMap, reservedDma);
    
    if (burstResult.conflicts.length === 0) {
      const burstDetails = [];
      const timerDmaAssignments = new Map();
      
      burstResult.timerGroups.forEach((outputs, tim) => {
        const dmaOptions = burstDmaMap[tim];
        for (const dma of dmaOptions) {
          const streamKey = `${dma[0]}_${dma[1]}`;
          const existing = Array.from(burstResult.usedStreams.entries())
            .find(([k, v]) => k === streamKey);
          if (existing && existing[1].startsWith(tim)) {
            timerDmaAssignments.set(tim, dma);
            break;
          }
        }
      });
      
      baseTimers.forEach(timer => {
        const dma = timerDmaAssignments.get(timer.tim);
        burstDetails.push({
          ...timer,
          dmaFlag: 0,
          dma: dma ? `${dmaToString(dma, mcuType)} (Burst)` : 'UNKNOWN',
          burstTimer: timer.tim,
          options: 1
        });
      });
      
      bestSolution = { 
        success: true, 
        details: burstDetails, 
        burstMode: true,
        timerGroups: burstResult.timerGroups,
        reservedDma: reservedDma
      };
    }
  }

  if (!bestSolution) {
    console.log('No solution found in any mode');
    const errorMsg = mcuType === 'AT32F435' 
      ? 'No valid configuration found (AT32F435 does not support burst mode - only per-channel DMA tested)'
      : 'No valid configuration found (tried both normal and burst mode)';
    return { success: false, error: errorMsg };
  }

  return bestSolution;
};
