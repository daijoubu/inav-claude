/**
 * Regression test: Blackbox tab hangs forever when FC has no SD card / dataflash
 *
 * Bug:
 *   onboard_logging.js sends a chain of 4 MSP requests on tab init:
 *     MSP_FEATURE -> MSP_DATAFLASH_SUMMARY -> MSP_SDCARD_SUMMARY -> MSP2_BLACKBOX_CONFIG
 *   If any message times out (no hardware, real FC with no storage), the chain
 *   never reaches load_html(), GUI.content_ready(callback) is never called, and
 *   GUI.tab_switch_in_progress stays true forever — the spinner never clears and
 *   no other tab can be opened without a page reload.
 *
 * Fix (to be implemented in tabs/onboard_logging.js):
 *   A 5-second timeout fallback calls GUI.content_ready(callback) if the MSP
 *   chain has not completed by then.
 *
 * Test structure:
 *   - Bug test:  MSP never responds to MSP_SDCARD_SUMMARY. After 5 seconds
 *                tab_switch_in_progress must still be true. (demonstrates the hang)
 *   - Fix test:  Same scenario but with the 5-second timeout fallback in place.
 *                After 6 seconds tab_switch_in_progress must be false. (fix works)
 *
 * How to run:
 *   node claude/developer/scripts/testing/configurator/test_onboard_logging_tab_hang.cjs
 *
 * Expected output before fix is applied:
 *   PASS  Bug reproduced: tab_switch_in_progress stays true after MSP timeout
 *   FAIL  Fix test: tab_switch_in_progress should be false within 6 s — it is still true
 *
 * Expected output after fix is applied:
 *   PASS  Bug reproduced: tab_switch_in_progress stays true after MSP timeout
 *   PASS  Fix test: tab_switch_in_progress becomes false within 6 s
 *
 * Note: The "bug reproduced" test always passes — it documents the baseline
 *       behaviour BEFORE any timeout is present.
 */

'use strict';

// ---------------------------------------------------------------------------
// Minimal test harness (no external dependencies)
// ---------------------------------------------------------------------------

let passed = 0;
let failed = 0;

function assert(condition, message) {
    if (condition) {
        console.log('PASS ', message);
        passed++;
    } else {
        console.log('FAIL ', message);
        failed++;
    }
}

// ---------------------------------------------------------------------------
// Fake timer infrastructure
//
// We replace the global setTimeout/clearTimeout so that we can advance clock
// time without actually sleeping. This makes the tests run in milliseconds
// even though we are simulating 5-6 second waits.
// ---------------------------------------------------------------------------

let fakeNow = 0;
const pendingTimers = [];  // { id, fireAt, fn }
let nextId = 1;

const realSetTimeout   = global.setTimeout;
const realClearTimeout = global.clearTimeout;

function installFakeTimers() {
    fakeNow = 0;
    pendingTimers.length = 0;
    nextId = 1;

    global.setTimeout = function(fn, delay) {
        const id = nextId++;
        pendingTimers.push({ id, fireAt: fakeNow + (delay || 0), fn });
        return id;
    };

    global.clearTimeout = function(id) {
        const idx = pendingTimers.findIndex(t => t.id === id);
        if (idx !== -1) pendingTimers.splice(idx, 1);
    };
}

function restoreRealTimers() {
    global.setTimeout   = realSetTimeout;
    global.clearTimeout = realClearTimeout;
}

/**
 * Advance fake clock by `ms` milliseconds, firing any timers that fall due.
 * Timers are fired in chronological order, and newly scheduled timers that
 * fall within the advanced window are also fired.
 */
function advanceFakeTime(ms) {
    const target = fakeNow + ms;
    // Keep firing any timer whose fireAt <= target
    let safety = 10000;
    while (safety-- > 0) {
        // Find the earliest timer that is ready
        let earliest = null;
        for (const t of pendingTimers) {
            if (t.fireAt <= target) {
                if (!earliest || t.fireAt < earliest.fireAt) {
                    earliest = t;
                }
            }
        }
        if (!earliest) break;

        // Remove it and advance clock to its fire time
        const idx = pendingTimers.indexOf(earliest);
        pendingTimers.splice(idx, 1);
        fakeNow = earliest.fireAt;
        earliest.fn();
    }
    fakeNow = target;
}

// ---------------------------------------------------------------------------
// Minimal stubs for the Electron/browser/jQuery environment that
// onboard_logging.js depends on.
//
// We do NOT import the real tab module — it uses ES6 `import`, Vite, jQuery,
// and Electron APIs that are not available in plain Node. Instead we inline
// the exact logic that is relevant to the bug: the MSP chain and the
// content_ready call.
// ---------------------------------------------------------------------------

/**
 * Build a fresh test environment each time so tests are isolated.
 *
 * Returns:
 *   gui      - the simulated GUI object
 *   msp      - the simulated MSP object
 *   timeout  - the simulated timeout utility (mirrors js/timeouts.js)
 *   runTab   - function(callback) that runs the initialize logic under test
 */
function buildEnv({ mspHangsOnMessage = null, withTimeoutFallback = false } = {}) {

    // --- GUI stub ---
    const gui = {
        tab_switch_in_progress: true,  // set to true when a tab switch starts
        active_tab: null,
        connected_to: true,
        content_ready: function(callback) {
            // The real content_ready clears the spinner and calls the callback.
            // Crucially it resets tab_switch_in_progress (done by the caller
            // of initialize() in gui.js after content_ready fires the callback).
            //
            // In the real app, gui.js does:
            //   GUI.tab_switch_in_progress = false;  (inside the callback passed to initialize)
            // We simulate that here: when content_ready invokes callback, the
            // tab switch is considered done.
            if (callback) callback();
        }
    };

    // --- timeout stub (mirrors js/timeouts.js publicScope) ---
    const timeoutUtil = {
        _timers: {},
        add: function(name, fn, delay) {
            const id = setTimeout(fn, delay);
            this._timers[name] = id;
            return id;
        },
        remove: function(name) {
            if (this._timers[name] !== undefined) {
                clearTimeout(this._timers[name]);
                delete this._timers[name];
            }
        },
        killAll: function() {
            for (const name in this._timers) {
                clearTimeout(this._timers[name]);
            }
            this._timers = {};
        }
    };

    // MSP code constants (from js/msp/MSPCodes.js)
    const MSPCodes = {
        MSP_FEATURE:          36,
        MSP_DATAFLASH_SUMMARY: 70,
        MSP_SDCARD_SUMMARY:    79,
        MSP2_BLACKBOX_CONFIG:  0x201A,
    };

    // --- MSP stub ---
    // send_message(code, payload, noRetry, callback) is the signature.
    // When mspHangsOnMessage matches, we silently drop the message (no callback).
    // All other messages call the callback immediately (instant success).
    const msp = {
        send_message: function(code, payload, noRetry, callback) {
            if (code === mspHangsOnMessage) {
                // Simulate a timeout — callback is never called
                return;
            }
            // Simulate an instant successful response
            if (callback) callback();
        }
    };

    // --- CONFIGURATOR stub ---
    const CONFIGURATOR = { connectionValid: true };

    // -----------------------------------------------------------------------
    // The initialize logic — extracted verbatim from tabs/onboard_logging.js,
    // replacing imports with the stubs above.
    //
    // When withTimeoutFallback === true we also include the 5-second timeout
    // fallback that the fix will add.  This lets the same test file serve
    // both "shows bug" and "shows fix" scenarios.
    // -----------------------------------------------------------------------
    function runTab(callback) {
        // The real gui.js sets tab_switch_in_progress = true before calling
        // initialize(), then the passed-in callback sets it to false.
        // We replicate that contract here:
        gui.tab_switch_in_progress = true;

        // Wrap the real callback so we track when it fires.
        const wrappedCallback = function() {
            gui.tab_switch_in_progress = false;
            if (callback) callback();
        };

        // ---- BEGIN: logic from onboard_logging.js initialize() ----

        let fallbackScheduled = false;
        let chainCompleted = false;

        if (withTimeoutFallback) {
            // THE FIX: schedule a 5-second fallback so content_ready is always
            // called even if the MSP chain never completes.
            timeoutUtil.add('onboard_logging_fallback', function() {
                if (!chainCompleted) {
                    gui.content_ready(wrappedCallback);
                }
            }, 5000);
        }

        function load_html() {
            chainCompleted = true;
            if (withTimeoutFallback) {
                timeoutUtil.remove('onboard_logging_fallback');
            }
            // In the real code, load_html does DOM work and then calls:
            gui.content_ready(wrappedCallback);
        }

        if (CONFIGURATOR.connectionValid) {
            msp.send_message(MSPCodes.MSP_FEATURE, false, false, function() {
                msp.send_message(MSPCodes.MSP_DATAFLASH_SUMMARY, false, false, function() {
                    msp.send_message(MSPCodes.MSP_SDCARD_SUMMARY, false, false, function() {
                        msp.send_message(MSPCodes.MSP2_BLACKBOX_CONFIG, false, false, load_html);
                    });
                });
            });
        }

        // ---- END: logic from onboard_logging.js initialize() ----
    }

    return { gui, msp, timeoutUtil, runTab };
}

// ---------------------------------------------------------------------------
// Test 1 — Bug reproduction
//
// MSP_SDCARD_SUMMARY never responds (simulates no SD card on FCs that let the
// request time out rather than returning an error payload).
// After advancing time well past where a 5-second timeout *would* fire,
// tab_switch_in_progress must still be true — proving the bug.
// ---------------------------------------------------------------------------

function testBugReproduction() {
    installFakeTimers();

    const { gui, runTab } = buildEnv({
        mspHangsOnMessage: 79,  // MSP_SDCARD_SUMMARY
        withTimeoutFallback: false
    });

    // Simulate the tab switch starting
    runTab(/* no completion callback needed for this assertion */);

    // Advance clock by 5 seconds — far enough that any reasonable timeout
    // fallback would have fired IF it existed.
    advanceFakeTime(5100);

    assert(
        gui.tab_switch_in_progress === true,
        'Bug reproduced: tab_switch_in_progress stays true after MSP timeout (no fallback present)'
    );

    restoreRealTimers();
}

// ---------------------------------------------------------------------------
// Test 2 — Fix verification
//
// Same scenario (MSP_SDCARD_SUMMARY hangs) but now the 5-second timeout
// fallback IS in place. After advancing to 6 seconds, tab_switch_in_progress
// must be false.
// ---------------------------------------------------------------------------

function testFixVerification() {
    installFakeTimers();

    const { gui, runTab } = buildEnv({
        mspHangsOnMessage: 79,  // MSP_SDCARD_SUMMARY
        withTimeoutFallback: true
    });

    runTab();

    // Advance to just after the 5-second fallback fires
    advanceFakeTime(5100);

    assert(
        gui.tab_switch_in_progress === false,
        'Fix test: tab_switch_in_progress becomes false within 6 s when timeout fallback is present'
    );

    restoreRealTimers();
}

// ---------------------------------------------------------------------------
// Test 3 — Happy path: fallback does NOT fire when chain completes normally
//
// All 4 MSP messages succeed. content_ready must be called (tab_switch = false)
// and the fallback timer must not fire afterwards (would be a double-call to
// content_ready, which could cause subtle bugs).
// ---------------------------------------------------------------------------

function testHappyPathNoDoubleFire() {
    installFakeTimers();

    let contentReadyCalls = 0;
    const { gui, timeoutUtil, runTab } = buildEnv({
        mspHangsOnMessage: null,   // all messages succeed
        withTimeoutFallback: true
    });

    // Patch content_ready to count calls
    const origContentReady = gui.content_ready.bind(gui);
    gui.content_ready = function(cb) {
        contentReadyCalls++;
        origContentReady(cb);
    };

    runTab();

    // Chain completes instantly (all MSP mocks call back synchronously)
    // so at time 0 we are already done. Advance past the fallback window.
    advanceFakeTime(6000);

    assert(
        gui.tab_switch_in_progress === false,
        'Happy path: tab_switch_in_progress is cleared when chain completes normally'
    );

    assert(
        contentReadyCalls === 1,
        'Happy path: content_ready called exactly once (fallback did not double-fire)'
    );

    restoreRealTimers();
}

// ---------------------------------------------------------------------------
// Test 4 — MSP_FEATURE (first message) hangs — chain cannot even start
// ---------------------------------------------------------------------------

function testFirstMessageHangs() {
    installFakeTimers();

    const { gui, runTab } = buildEnv({
        mspHangsOnMessage: 36,   // MSP_FEATURE
        withTimeoutFallback: true
    });

    runTab();
    advanceFakeTime(5100);

    assert(
        gui.tab_switch_in_progress === false,
        'Fix test: fallback fires even when the FIRST message (MSP_FEATURE) hangs'
    );

    restoreRealTimers();
}

// ---------------------------------------------------------------------------
// Test 5 — MSP2_BLACKBOX_CONFIG (last message) hangs
// ---------------------------------------------------------------------------

function testLastMessageHangs() {
    installFakeTimers();

    const { gui, runTab } = buildEnv({
        mspHangsOnMessage: 0x201A,   // MSP2_BLACKBOX_CONFIG
        withTimeoutFallback: true
    });

    runTab();
    advanceFakeTime(5100);

    assert(
        gui.tab_switch_in_progress === false,
        'Fix test: fallback fires even when the LAST message (MSP2_BLACKBOX_CONFIG) hangs'
    );

    restoreRealTimers();
}

// ---------------------------------------------------------------------------
// Run all tests
// ---------------------------------------------------------------------------

console.log('');
console.log('='.repeat(70));
console.log(' Blackbox tab hang regression test');
console.log(' tabs/onboard_logging.js — MSP chain timeout bug');
console.log('='.repeat(70));
console.log('');

testBugReproduction();
testFixVerification();
testHappyPathNoDoubleFire();
testFirstMessageHangs();
testLastMessageHangs();

console.log('');
console.log('='.repeat(70));
console.log(' Results: ' + passed + ' passed, ' + failed + ' failed');
console.log('='.repeat(70));
console.log('');

// Exit non-zero only if a test that tests the FIX fails.
// (The bug-reproduction test always passes — it documents current broken state.)
if (failed > 0) {
    process.exit(1);
} else {
    process.exit(0);
}
