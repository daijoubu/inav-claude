# WASM SITL Testing Procedure

## Quick Reference

### Connect → Disconnect → Reconnect Cycle

1. **Select port**: "SITL (Browser)" should be pre-selected
2. **Click Connect** (the link element, not the text)
3. **Wait for "Disconnect" button** to appear (connection established)
4. **IMPORTANT: Dismiss "Default values" dialog** by clicking "Keep current settings"
5. **Click Disconnect** - page will reload automatically
6. **Click Connect again** to verify reconnect works

### Common Gotchas

- **Default values dialog**: On first connect, a dialog appears asking about UAV type. Must click "Keep current settings (Not recommended)" to dismiss it before testing other features.
- **Page reload on disconnect**: Disconnect triggers a page reload for clean state. This is intentional.
- **Vite hot reload**: Changes to JS files should hot-reload, but WASM changes require a full rebuild.

## Chrome DevTools MCP Commands

### Check current state
```
mcp__chrome-devtools__take_snapshot
mcp__chrome-devtools__list_console_messages
```

### Connect flow
```javascript
// Click Connect button (uid varies, use snapshot to find current uid)
mcp__chrome-devtools__click({ uid: "1_6" })  // Connect/Disconnect button

// Wait for connection
mcp__chrome-devtools__wait_for({ text: "Disconnect", timeout: 10000 })

// Dismiss default values dialog (IMPORTANT!)
mcp__chrome-devtools__click({ uid: "<keep-settings-uid>" })  // "Keep current settings"
```

### Disconnect flow
```javascript
// Click Disconnect
mcp__chrome-devtools__click({ uid: "<disconnect-button-uid>" })

// Wait for page reload (shows Welcome)
mcp__chrome-devtools__wait_for({ text: "Welcome", timeout: 5000 })
```

## Browser Console Scripts

These can be run in the browser DevTools console for manual testing.

### Check WASM module state
```javascript
// Check if WASM module is loaded
console.log('Module loaded:', typeof window.Module !== 'undefined');
console.log('Module._serialAvailable:', typeof window.Module?._serialAvailable);
```

### Send test MSP command
```javascript
// Send MSP_API_VERSION (code 1) manually
const module = window.Module;
if (module && module._serialWriteByte) {
    // MSP V1 header for MSP_API_VERSION
    const packet = [0x24, 0x4D, 0x3C, 0x00, 0x01, 0x01]; // $M< len=0 cmd=1 crc=1
    packet.forEach(b => module._serialWriteByte(b));
    console.log('Sent MSP_API_VERSION request');

    // Check for response after a moment
    setTimeout(() => {
        const avail = module._serialAvailable();
        console.log('Response bytes available:', avail);
    }, 100);
}
```

### Force page reload (like disconnect)
```javascript
if (window.electronAPI && window.electronAPI.reloadPage) {
    window.electronAPI.reloadPage();
}
```

## Element UIDs Reference

UIDs change after page reload, but these patterns are consistent:

| Element | How to Find |
|---------|-------------|
| Connect/Disconnect button | Link with text "Connect" or "Disconnect" |
| Port dropdown | Combobox with value "SITL (Browser)" |
| Keep current settings | Link with text containing "Keep current settings" |
| Tab links | Links with tab names (Status, Mixer, CLI, etc.) |

## Testing Cleanup Commits

When testing cleanup commits one by one:

1. **Reset to baseline**: `git reset --hard <baseline-commit>`
2. **Rebuild WASM**: Use inav-builder agent or run cmake/make
3. **Copy binaries**: Copy SITL.elf and SITL.elf.wasm to configurator
4. **Test connection**: Full connect/disconnect/reconnect cycle
5. **Apply next commit**: `git cherry-pick <commit>`
6. **Rebuild and test again**
7. **If broken**: The last applied commit caused the issue

## Build Commands

### Rebuild WASM SITL
```bash
cd /home/raymorris/Documents/planes/inavflight/inav
rm -rf build_sitl_wasm
mkdir build_sitl_wasm && cd build_sitl_wasm
cmake -DTOOLCHAIN=wasm -DSITL=ON ..
make -j4
```

### Copy binaries to configurator
```bash
cp build_sitl_wasm/SITL.elf ../inav-configurator/resources/sitl/SITL.elf
cp build_sitl_wasm/SITL.elf.wasm ../inav-configurator/resources/sitl/SITL.elf.wasm
```

## Automated Test Script

Save this as a reference for future automation:

```javascript
// Full connection test sequence (run via Chrome DevTools MCP)
async function testWasmConnection() {
    // 1. Take initial snapshot to get element UIDs
    const snapshot = await takeSnapshot();

    // 2. Find and click Connect button
    const connectBtn = findElementByText(snapshot, 'Connect');
    await click(connectBtn.uid);

    // 3. Wait for connection
    await waitFor('Disconnect', 10000);

    // 4. Dismiss default values dialog if present
    const keepSettings = findElementByText(snapshot, 'Keep current settings');
    if (keepSettings) {
        await click(keepSettings.uid);
    }

    // 5. Verify connected state
    const connectedSnapshot = await takeSnapshot();
    const hasDisconnect = findElementByText(connectedSnapshot, 'Disconnect');
    console.log('Connected:', !!hasDisconnect);

    // 6. Test disconnect
    await click(hasDisconnect.uid);
    await waitFor('Welcome', 5000);

    // 7. Test reconnect
    const freshSnapshot = await takeSnapshot();
    const reconnectBtn = findElementByText(freshSnapshot, 'Connect');
    await click(reconnectBtn.uid);
    await waitFor('Disconnect', 10000);

    console.log('Full cycle test PASSED');
}
```
