/**
 * Test script: INAV Configurator Ports Tab - Sensor Port Function Validation
 *
 * Validates that a named sensor port function appears in the Ports tab,
 * correctly reports its bit mask, and applies baud locking behavior.
 *
 * Usage: Run via Chrome DevTools MCP evaluate_script while Configurator
 * is connected to an FC and the Ports tab is active.
 *
 * Base for testing any sensor port function (CRSF_SENSOR, SBUS_SENSOR, etc.)
 *
 * PREREQUISITE: FC must be connected and Ports tab loaded before running.
 *
 * Developed during CRSF sensor input PR (#11379) testing, 2026-05-17.
 */

// ── CONFIG ──────────────────────────────────────────────────────────────────
const FUNCTION_NAME   = 'CRSF_SENSOR';   // internal rule name in serialPortHelper
const EXPECTED_BIT    = 24;              // firmware bit position (0-based)
const EXPECTED_BAUD   = 420000;          // expected default/locked baud
const LOCKED_BAUD     = true;           // true = baud select should be disabled
const TEST_UART_LABEL = 'UART2';        // which UART row to test interaction on
// ─────────────────────────────────────────────────────────────────────────────

async function runTests() {
    const mod = await import('/js/serialPortHelper.js');
    const helper = mod.default;
    const results = {};

    // Test 1: Rule exists with correct properties
    const rule = helper.getRuleByName(FUNCTION_NAME);
    results.test1_ruleExists = !!rule;
    results.test1_groups     = rule?.groups;
    results.test1_defaultBaud = rule?.defaultBaud;
    results.test1_lockedBaud  = rule?.lockedBaud;
    results.test1_isUnique    = rule?.isUnique;

    // Test 2: Bit mask is correct (1 << EXPECTED_BIT)
    const mask = helper.functionsToMask([FUNCTION_NAME]);
    results.test2_mask        = mask;
    results.test2_expected    = (1 << EXPECTED_BIT) >>> 0;
    results.test2_maskCorrect = mask === ((1 << EXPECTED_BIT) >>> 0);

    // Test 3: Round-trip mask → functions
    results.test3_roundTrip   = helper.maskToFunctions(mask);
    results.test3_roundTripOk = results.test3_roundTrip.includes(FUNCTION_NAME);

    // Test 4: Display name loaded from i18n
    results.test4_displayName = rule?.displayName;

    // Test 5: Option appears in each UART sensors dropdown
    const sensorSelects = document.querySelectorAll('select[name="function-sensors"]');
    const optionValues  = Array.from(sensorSelects[0]?.options ?? []).map(o => o.value);
    results.test5_optionInDropdown = optionValues.includes(FUNCTION_NAME);
    results.test5_allUartCount     = sensorSelects.length;

    // Test 6: Selecting the function on TEST_UART_LABEL disables the baud select
    const rows = document.querySelectorAll('table.ports tbody tr');
    for (const row of rows) {
        if (row.querySelector('td:first-child')?.textContent?.trim() !== TEST_UART_LABEL) continue;

        const sensorSelect = row.querySelector('select[name="function-sensors"]');
        const sensorBaud   = row.querySelector('.sensors_baudrate');
        if (!sensorSelect || !sensorBaud) { results.test6_error = 'elements not found'; break; }

        const before = sensorBaud.disabled;
        sensorSelect.value = FUNCTION_NAME;
        sensorSelect.dispatchEvent(new Event('change', { bubbles: true }));
        await new Promise(r => setTimeout(r, 50));
        const after = sensorBaud.disabled;

        results.test6_disabledBefore = before;
        results.test6_disabledAfter  = after;
        results.test6_lockApplied    = LOCKED_BAUD ? after === true : after === false;

        // Test 7: Switching away re-enables the baud select
        sensorSelect.value = '';
        sensorSelect.dispatchEvent(new Event('change', { bubbles: true }));
        await new Promise(r => setTimeout(r, 50));
        results.test7_disabledAfterClear = sensorBaud.disabled;
        results.test7_reenabledCorrectly = !sensorBaud.disabled;

        break;
    }

    // Test 8: 420000 NOT in SENSOR baud list (avoids MSP index -1 bug)
    const sensorBauds = helper.getBauds('SENSOR');
    results.test8_sensorBaudList          = sensorBauds;
    results.test8_lockedBaudNotInList     = !sensorBauds?.includes(String(EXPECTED_BAUD));

    return results;
}

return runTests();
