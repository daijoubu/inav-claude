#!/usr/bin/env python3
"""
Test WASM SITL Connection via Chrome DevTools Protocol

Tests the serialAvailable() fix and WASM MSP communication.

Expected results:
- Connection should succeed
- MSP_API_VERSION should return valid data
- MSP_FC_VARIANT should return "INAV"
- No errors in console

Usage:
    python3 test_wasm_connection.py
"""

import asyncio
import json
import sys
import websockets

# Test state
test_results = {
    'passed': [],
    'failed': [],
    'warnings': []
}

def log_success(test):
    """Log a successful test"""
    print(f'✓ {test}')
    test_results['passed'].append(test)

def log_failure(test, reason):
    """Log a failed test"""
    print(f'✗ {test}')
    print(f'  Reason: {reason}')
    test_results['failed'].append({'test': test, 'reason': reason})

def log_warning(message):
    """Log a warning"""
    print(f'⚠ {message}')
    test_results['warnings'].append(message)

async def get_devtools_url():
    """Get the WebSocket URL for Chrome DevTools"""
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get('http://127.0.0.1:9222/json') as resp:
            targets = await resp.json()
            if targets:
                return targets[0]['webSocketDebuggerUrl']
    return None

async def evaluate_js(ws, expression):
    """Evaluate JavaScript expression in browser"""
    msg_id = 1000 + len(test_results['passed']) + len(test_results['failed'])
    await ws.send(json.dumps({
        'id': msg_id,
        'method': 'Runtime.evaluate',
        'params': {
            'expression': expression,
            'returnByValue': True
        }
    }))

    # Wait for response
    while True:
        response = await ws.recv()
        data = json.loads(response)
        if data.get('id') == msg_id:
            if 'result' in data:
                return data['result'].get('result', {})
            elif 'error' in data:
                raise Exception(f"Evaluation error: {data['error']}")

async def test_wasm_connection():
    """Main test function"""
    try:
        print('\n=== WASM SITL Connection Test ===\n')
        print('Connecting to Chrome DevTools...')

        # Get WebSocket URL
        ws_url = await get_devtools_url()
        if not ws_url:
            print('✗ Failed to get DevTools URL')
            print('  Make sure configurator is running with remote debugging')
            return 1

        # Connect to WebSocket
        async with websockets.connect(ws_url) as ws:
            log_success('Connected to Chrome DevTools')

            # Enable Runtime domain
            await ws.send(json.dumps({
                'id': 1,
                'method': 'Runtime.enable'
            }))
            await ws.recv()  # Wait for acknowledgment

            # Step 1: Check if WASM loader exists
            print('\n--- Step 1: Check WASM Loader ---')
            result = await evaluate_js(ws, 'typeof window.wasmLoader !== "undefined"')

            if result.get('value') == True:
                log_success('WASM loader exists')
            else:
                log_failure('WASM loader exists', 'window.wasmLoader is undefined')
                log_warning('WASM loader may not have been initialized yet')

            # Step 2: Check if WASM module is loaded
            print('\n--- Step 2: Check WASM Module ---')
            result = await evaluate_js(ws, '''
                (function() {
                    if (!window.wasmLoader) return { loaded: false, error: 'No loader' };
                    if (!window.wasmLoader.isLoaded()) return { loaded: false, error: 'Not loaded' };
                    const module = window.wasmLoader.getModule();
                    return {
                        loaded: true,
                        hasSerialWriteByte: typeof module._serialWriteByte === 'function',
                        hasSerialReadByte: typeof module._serialReadByte === 'function',
                        hasSerialAvailable: typeof module._serialAvailable === 'function'
                    };
                })()
            ''')

            module_state = result.get('value', {})

            if module_state.get('loaded'):
                log_success('WASM module is loaded')

                if module_state.get('hasSerialWriteByte'):
                    log_success('serialWriteByte() function exists')
                else:
                    log_failure('serialWriteByte() function exists', 'Function not found in module')

                if module_state.get('hasSerialReadByte'):
                    log_success('serialReadByte() function exists')
                else:
                    log_failure('serialReadByte() function exists', 'Function not found in module')

                if module_state.get('hasSerialAvailable'):
                    log_success('serialAvailable() function exists')
                else:
                    log_failure('serialAvailable() function exists', 'Function not found in module')
            else:
                log_failure('WASM module is loaded', module_state.get('error', 'Unknown error'))
                log_warning('Cannot proceed with further tests - WASM not loaded')
                log_warning('Try connecting to "SITL (Browser)" in the configurator first')

            # Step 3: Test serialAvailable() returns correct type
            print('\n--- Step 3: Test serialAvailable() ---')
            if module_state.get('loaded') and module_state.get('hasSerialAvailable'):
                result = await evaluate_js(ws, '''
                    (function() {
                        const module = window.wasmLoader.getModule();
                        const available = module._serialAvailable();
                        return {
                            value: available,
                            isNumber: typeof available === 'number',
                            isNonNegative: available >= 0
                        };
                    })()
                ''')

                avail_result = result.get('value', {})

                if avail_result.get('isNumber'):
                    log_success('serialAvailable() returns a number')
                else:
                    log_failure('serialAvailable() returns a number',
                              f"Got type: {type(avail_result.get('value'))}")

                if avail_result.get('isNonNegative'):
                    log_success('serialAvailable() returns non-negative value')
                    print(f"  Current value: {avail_result.get('value')} bytes available")
                else:
                    log_failure('serialAvailable() returns non-negative value',
                              f"Got: {avail_result.get('value')}")

            # Step 4: Test byte interface
            print('\n--- Step 4: Test Serial Byte Interface ---')
            if module_state.get('loaded') and module_state.get('hasSerialWriteByte') and module_state.get('hasSerialReadByte'):
                result = await evaluate_js(ws, '''
                    (function() {
                        const module = window.wasmLoader.getModule();

                        // Test write
                        try {
                            module._serialWriteByte(0x42);
                        } catch (e) {
                            return { writeSuccess: false, error: e.message };
                        }

                        // Check if we can read
                        const availableBefore = module._serialAvailable();

                        // Try to read (might return -1 if nothing there)
                        let readValue;
                        try {
                            readValue = module._serialReadByte();
                        } catch (e) {
                            return { writeSuccess: true, readSuccess: false, error: e.message };
                        }

                        return {
                            writeSuccess: true,
                            readSuccess: true,
                            availableBefore: availableBefore,
                            readValue: readValue
                        };
                    })()
                ''')

                byte_result = result.get('value', {})

                if byte_result.get('writeSuccess'):
                    log_success('serialWriteByte() executes without error')
                else:
                    log_failure('serialWriteByte() executes without error', byte_result.get('error'))

                if byte_result.get('readSuccess'):
                    log_success('serialReadByte() executes without error')
                    print(f"  Available before read: {byte_result.get('availableBefore')} bytes")
                    print(f"  Read value: {byte_result.get('readValue')}")
                else:
                    log_failure('serialReadByte() executes without error', byte_result.get('error'))

            # Step 5: Check connection state
            print('\n--- Step 5: Check Connection State ---')
            result = await evaluate_js(ws, '''
                (function() {
                    // Check if SERIAL object exists
                    if (typeof SERIAL === 'undefined') {
                        return { serialExists: false };
                    }

                    // Check connection info
                    return {
                        serialExists: true,
                        connected: SERIAL.connected,
                        connectionId: SERIAL.connectionId,
                        connectionType: SERIAL.connectionType
                    };
                })()
            ''')

            conn_state = result.get('value', {})

            if conn_state.get('serialExists'):
                log_success('SERIAL object exists')

                if conn_state.get('connected'):
                    log_success('SERIAL.connected is true')
                    print(f"  Connection ID: {conn_state.get('connectionId')}")
                    print(f"  Connection Type: {conn_state.get('connectionType')}")
                else:
                    log_warning('SERIAL.connected is false - not connected yet')
                    log_warning('Click "Connect" button in configurator to establish connection')
            else:
                log_failure('SERIAL object exists', 'SERIAL is undefined')

            # Step 6: Check for MSP data (if connected)
            if conn_state.get('connected'):
                print('\n--- Step 6: Check MSP Data ---')
                result = await evaluate_js(ws, '''
                    (function() {
                        if (typeof CONFIG === 'undefined') {
                            return { configExists: false };
                        }

                        return {
                            configExists: true,
                            apiVersion: CONFIG.apiVersion || 'unknown',
                            fcVariant: CONFIG.flightControllerIdentifier || 'unknown',
                            fcVersion: CONFIG.flightControllerVersion || 'unknown'
                        };
                    })()
                ''')

                msp_data = result.get('value', {})

                if msp_data.get('configExists'):
                    log_success('CONFIG object exists')

                    if msp_data.get('apiVersion') != 'unknown':
                        log_success('MSP_API_VERSION received')
                        print(f"  API Version: {msp_data.get('apiVersion')}")
                    else:
                        log_warning('MSP_API_VERSION not received yet')

                    if msp_data.get('fcVariant') == 'INAV':
                        log_success('MSP_FC_VARIANT is "INAV"')
                        print(f"  FC Version: {msp_data.get('fcVersion')}")
                    elif msp_data.get('fcVariant') != 'unknown':
                        log_failure('MSP_FC_VARIANT is "INAV"', f"Got: {msp_data.get('fcVariant')}")
                    else:
                        log_warning('MSP_FC_VARIANT not received yet')
                else:
                    log_warning('CONFIG object does not exist - MSP data not loaded')

            # Print summary
            print('\n=== Test Summary ===\n')
            print(f"Passed: {len(test_results['passed'])}")
            print(f"Failed: {len(test_results['failed'])}")
            print(f"Warnings: {len(test_results['warnings'])}")

            if test_results['failed']:
                print('\nFailed tests:')
                for item in test_results['failed']:
                    print(f"  ✗ {item['test']}")
                    print(f"    {item['reason']}")

            if test_results['warnings']:
                print('\nWarnings:')
                for warning in test_results['warnings']:
                    print(f"  ⚠ {warning}")

            return 1 if test_results['failed'] else 0

    except Exception as error:
        print(f'\n✗ Test execution failed:')
        print(f'  {error}')

        if 'ECONNREFUSED' in str(error):
            print('\nCannot connect to Chrome DevTools.')
            print('Make sure:')
            print('  1. Configurator is running')
            print('  2. Remote debugging is enabled on port 9222')
            print('  3. If running in sandbox: retry with dangerouslyDisableSandbox: true')

        return 1

if __name__ == '__main__':
    exit_code = asyncio.run(test_wasm_connection())
    sys.exit(exit_code)
