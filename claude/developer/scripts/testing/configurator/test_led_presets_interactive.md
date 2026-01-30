# Interactive LED Strip Preset Testing Guide

This guide provides step-by-step instructions for testing the LED strip presets using MCP Chrome DevTools.

## Prerequisites

1. INAV Configurator is running
2. MCP Chrome DevTools server is connected
3. You can interact with the configurator via MCP

## Test Steps

### Step 1: Navigate to LED Strip Tab

Use MCP to navigate to the LED Strip tab:

```javascript
// First, check if we're connected or need to connect
// Take a snapshot to see current state
mcp__chrome-devtools__take_snapshot()

// If not on LED Strip tab, navigate there
// You'll need to find the LED Strip tab link UID from the snapshot
// Then click it:
mcp__chrome-devtools__click({ uid: "LED_STRIP_TAB_UID" })

// Wait for tab to load
setTimeout(() => {}, 1000)
```

### Step 2: Test X-Frame Preset

```javascript
// Click the X-Frame preset button
mcp__chrome-devtools__evaluate_script({
  function: `() => {
    const button = document.querySelector('button.quickLayout[data-layout="xframe"]');
    if (!button) return { error: "X-Frame button not found" };

    button.click();

    // Wait for UI to update, then check results
    return new Promise((resolve) => {
      setTimeout(() => {
        const placedCount = document.querySelector('.wires-placed .placed-count')?.textContent;
        const gridPoints = document.querySelectorAll('.gPoint .wire');
        const activeLeds = Array.from(gridPoints).filter(el => el.textContent.trim() !== '');

        // Count colors
        let redCount = 0, greenCount = 0;
        document.querySelectorAll('.gPoint').forEach(cell => {
          const wire = cell.querySelector('.wire')?.textContent.trim();
          if (wire !== '') {
            if (cell.classList.contains('color-2')) redCount++;
            if (cell.classList.contains('color-6')) greenCount++;
          }
        });

        resolve({
          preset: 'xframe',
          placedCount: parseInt(placedCount) || 0,
          expectedCount: 20,
          actualLeds: activeLeds.length,
          colors: { red: redCount, green: greenCount },
          expectedColors: { red: 10, green: 10 },
          passed: (parseInt(placedCount) === 20) && (redCount === 10) && (greenCount === 10)
        });
      }, 500);
    });
  }`
})
```

**Expected Result:**
- `placedCount: 20`
- `actualLeds: 20`
- `colors: { red: 10, green: 10 }`
- `passed: true`

### Step 3: Test Cross-Frame Preset

```javascript
// Click the Cross-Frame preset button
mcp__chrome-devtools__evaluate_script({
  function: `() => {
    const button = document.querySelector('button.quickLayout[data-layout="crossframe"]');
    if (!button) return { error: "Cross-Frame button not found" };

    button.click();

    return new Promise((resolve) => {
      setTimeout(() => {
        const placedCount = document.querySelector('.wires-placed .placed-count')?.textContent;
        const gridPoints = document.querySelectorAll('.gPoint .wire');
        const activeLeds = Array.from(gridPoints).filter(el => el.textContent.trim() !== '');

        // Count colors
        let redCount = 0, greenCount = 0, whiteCount = 0;
        document.querySelectorAll('.gPoint').forEach(cell => {
          const wire = cell.querySelector('.wire')?.textContent.trim();
          if (wire !== '') {
            if (cell.classList.contains('color-1')) whiteCount++;
            if (cell.classList.contains('color-2')) redCount++;
            if (cell.classList.contains('color-6')) greenCount++;
          }
        });

        resolve({
          preset: 'crossframe',
          placedCount: parseInt(placedCount) || 0,
          expectedCount: 20,
          actualLeds: activeLeds.length,
          colors: { red: redCount, green: greenCount, white: whiteCount },
          expectedColors: { red: 5, green: 5, white: 10 },
          passed: (parseInt(placedCount) === 20) && (redCount === 5) && (greenCount === 5) && (whiteCount === 10)
        });
      }, 500);
    });
  }`
})
```

**Expected Result:**
- `placedCount: 20`
- `actualLeds: 20`
- `colors: { red: 5, green: 5, white: 10 }`
- `passed: true`

### Step 4: Test Wing Preset

```javascript
// Click the Wing preset button
mcp__chrome-devtools__evaluate_script({
  function: `() => {
    const button = document.querySelector('button.quickLayout[data-layout="wing"]');
    if (!button) return { error: "Wing button not found" };

    button.click();

    return new Promise((resolve) => {
      setTimeout(() => {
        const placedCount = document.querySelector('.wires-placed .placed-count')?.textContent;
        const gridPoints = document.querySelectorAll('.gPoint .wire');
        const activeLeds = Array.from(gridPoints).filter(el => el.textContent.trim() !== '');

        // Count colors
        let redCount = 0, greenCount = 0;
        document.querySelectorAll('.gPoint').forEach(cell => {
          const wire = cell.querySelector('.wire')?.textContent.trim();
          if (wire !== '') {
            if (cell.classList.contains('color-2')) redCount++;
            if (cell.classList.contains('color-6')) greenCount++;
          }
        });

        resolve({
          preset: 'wing',
          placedCount: parseInt(placedCount) || 0,
          expectedCount: 20,
          actualLeds: activeLeds.length,
          colors: { red: redCount, green: greenCount },
          expectedColors: { red: 11, green: 9 },
          passed: (parseInt(placedCount) === 20) && (redCount === 11) && (greenCount === 9)
        });
      }, 500);
    });
  }`
})
```

**Expected Result:**
- `placedCount: 20`
- `actualLeds: 20`
- `colors: { red: 11, green: 9 }`
- `passed: true`

### Step 5: Visual Verification (Screenshots)

After each preset test, take a screenshot to verify visually:

```javascript
mcp__chrome-devtools__take_screenshot()
```

You should see:
- **X-Frame**: Red LEDs on diagonal left arms (NW, SW), green LEDs on diagonal right arms (NE, SE)
- **Cross-Frame**: White LEDs on front/back arms (N, S), red on left arm (W), green on right arm (E)
- **Wing**: Red LEDs on left half of both rows, green LEDs on right half

## Verification Checklist

For each preset:

- [ ] Button is visible and clickable
- [ ] Correct number of LEDs placed (20 for all presets)
- [ ] Correct color distribution:
  - X-Frame: 10 red, 10 green
  - Cross-Frame: 5 red, 5 green, 10 white
  - Wing: 11 red, 9 green
- [ ] LEDs positioned correctly on grid
- [ ] Direction indicators show on LEDs
- [ ] Function indicators show on LEDs (f, w, i)
- [ ] Visual appearance matches aviation navigation standards (red=port/left, green=starboard/right)

## Optional: CLI Verification

If you have SITL running and can connect via MSP:

1. Apply a preset in the configurator
2. Click "Save" button
3. Connect to SITL CLI via MSP
4. Run `led` command
5. Verify output matches preset definition

Each LED entry should show:
```
led <index> <x>,<y>:<directions>:<functions>:<color>
```

For example, xframe wire 0:
```
led 0 2,2:NW:FWI:2
```

## Troubleshooting

### Preset button not found
- Ensure you're on the LED Strip tab
- Check that led_strip_presets.js is loaded
- Verify buttons exist in HTML

### Wrong LED count
- Check if previous LEDs are being cleared
- Verify FC.LED_STRIP array is being reset correctly

### Wrong colors
- Verify color classes are being applied to grid cells
- Check that color indexes match: 1=white, 2=red, 6=green

### Visual layout looks wrong
- Compare grid positions with preset definition
- Verify x,y coordinates match expected positions
- Check that directions are being applied correctly
