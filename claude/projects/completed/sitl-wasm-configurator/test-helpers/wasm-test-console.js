/**
 * WASM SITL Test Helpers
 *
 * Copy-paste these into browser DevTools console for manual testing.
 * Or inject via Chrome DevTools MCP evaluate_script.
 */

// === Connection State ===

function checkWasmState() {
    const hasModule = typeof window.Module !== 'undefined';
    const hasSerial = hasModule && typeof window.Module._serialAvailable === 'function';
    const isConnected = document.querySelector('a')?.textContent?.includes('Disconnect');

    console.log('=== WASM State ===');
    console.log('Module loaded:', hasModule);
    console.log('Serial interface:', hasSerial);
    console.log('UI connected:', isConnected);

    if (hasSerial) {
        console.log('TX buffer available:', window.Module._serialAvailable());
    }

    return { hasModule, hasSerial, isConnected };
}

// === MSP Testing ===

function sendMspApiVersion() {
    const module = window.Module;
    if (!module || !module._serialWriteByte) {
        console.error('Module not loaded or serial not available');
        return;
    }

    // MSP V1: $M< + len(0) + cmd(1) + crc(1)
    const packet = [0x24, 0x4D, 0x3C, 0x00, 0x01, 0x01];
    packet.forEach(b => module._serialWriteByte(b));
    console.log('Sent MSP_API_VERSION (cmd 1)');

    setTimeout(() => {
        const avail = module._serialAvailable();
        console.log('Response bytes:', avail);
        if (avail > 0) {
            const response = [];
            for (let i = 0; i < avail; i++) {
                response.push(module._serialReadByte());
            }
            console.log('Response:', response.map(b => b.toString(16).padStart(2, '0')).join(' '));
        }
    }, 100);
}

function sendMspStatus() {
    const module = window.Module;
    if (!module || !module._serialWriteByte) {
        console.error('Module not loaded');
        return;
    }

    // MSP V1: $M< + len(0) + cmd(101) + crc
    const cmd = 101;
    const crc = cmd; // len=0, so crc = cmd
    const packet = [0x24, 0x4D, 0x3C, 0x00, cmd, crc];
    packet.forEach(b => module._serialWriteByte(b));
    console.log('Sent MSP_STATUS (cmd 101)');

    setTimeout(() => {
        const avail = module._serialAvailable();
        console.log('Response bytes:', avail);
    }, 100);
}

// === UI Helpers ===

function clickConnect() {
    const links = document.querySelectorAll('a');
    for (const link of links) {
        if (link.textContent === 'Connect' || link.textContent === 'Disconnect') {
            link.click();
            console.log('Clicked:', link.textContent);
            return;
        }
    }
    console.error('Connect/Disconnect button not found');
}

function dismissDefaultsDialog() {
    const links = document.querySelectorAll('a');
    for (const link of links) {
        if (link.textContent.includes('Keep current settings')) {
            link.click();
            console.log('Dismissed defaults dialog');
            return true;
        }
    }
    console.log('No defaults dialog found');
    return false;
}

function reloadPage() {
    if (window.electronAPI && window.electronAPI.reloadPage) {
        window.electronAPI.reloadPage();
    } else {
        location.reload();
    }
}

// === Full Test Sequence ===

async function runFullConnectionTest() {
    console.log('=== Starting Full Connection Test ===');

    // Check initial state
    const initial = checkWasmState();

    if (!initial.isConnected) {
        console.log('Step 1: Clicking Connect...');
        clickConnect();

        // Wait for connection
        await new Promise(r => setTimeout(r, 3000));
    }

    // Dismiss dialog if present
    console.log('Step 2: Checking for defaults dialog...');
    dismissDefaultsDialog();
    await new Promise(r => setTimeout(r, 500));

    // Verify connected
    const connected = checkWasmState();
    if (!connected.isConnected) {
        console.error('FAILED: Not connected after clicking Connect');
        return false;
    }

    console.log('Step 3: Testing MSP...');
    sendMspApiVersion();
    await new Promise(r => setTimeout(r, 200));

    console.log('Step 4: Disconnecting...');
    clickConnect(); // Click Disconnect

    console.log('=== Test Complete (page will reload) ===');
    return true;
}

// Export for console use
console.log('WASM test helpers loaded. Available functions:');
console.log('  checkWasmState() - Check module and connection state');
console.log('  sendMspApiVersion() - Send MSP_API_VERSION command');
console.log('  sendMspStatus() - Send MSP_STATUS command');
console.log('  clickConnect() - Click Connect/Disconnect button');
console.log('  dismissDefaultsDialog() - Dismiss the defaults dialog');
console.log('  reloadPage() - Force page reload');
console.log('  runFullConnectionTest() - Run full test sequence');
