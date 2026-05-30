#!/usr/bin/env python3
"""
Test: Advanced Tuning tab shows only correct section based on platform type.

Bug: Before fix, FC.MIXER_CONFIG.platformType could be -1 when the tab loaded,
causing both airplane and multirotor sections to show simultaneously.

Fix (tabs/advanced_tuning.js): MSPChainer fetches MIXER_CONFIG before rendering
HTML, ensuring platformType is valid when the show/hide logic runs.

Usage:
    python3 test_advanced_tuning_visibility.py

Requirements:
    - INAV Configurator running with --remote-debugging-port=9222
    - SITL running on localhost:5760 (or FC connected via serial)
    - If running in sandbox: use dangerouslyDisableSandbox=true

Note: The websocket-client library must be installed (pip install websocket-client).
      This script uses suppress_origin=True which is required for Electron CDP.
"""

import json
import time
import sys
import urllib.request

try:
    from websocket import create_connection
except ImportError:
    print("X Missing dependency: pip install websocket-client")
    sys.exit(1)

CDP_HOST = "localhost"
CDP_PORT = 9222
SITL_TCP = "localhost:5760"


def find_configurator_target():
    url = f"http://{CDP_HOST}:{CDP_PORT}/json/list"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            targets = json.loads(resp.read())
    except Exception as e:
        print(f"X FAILED to get CDP targets: {e}")
        print("  Is configurator running with --remote-debugging-port=9222?")
        print("  If in sandbox: retry with dangerouslyDisableSandbox: true")
        sys.exit(1)

    for t in targets:
        if "INAV Configurator" in t.get("title", "") or "localhost:5174" in t.get("url", ""):
            return t

    print("X Could not find INAV Configurator CDP target")
    print(f"  Available targets: {[t['title'] for t in targets]}")
    sys.exit(1)


class CDPSession:
    def __init__(self, ws_url):
        # suppress_origin=True is REQUIRED for Electron CDP WebSocket connections
        self.ws = create_connection(ws_url, timeout=15, suppress_origin=True)
        self._mid = 0

    def ev(self, expr, await_promise=False):
        self._mid += 1
        m = self._mid
        self.ws.send(json.dumps({
            "id": m,
            "method": "Runtime.evaluate",
            "params": {
                "expression": expr,
                "returnByValue": True,
                "awaitPromise": await_promise,
            }
        }))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == m:
                return msg.get("result", {}).get("result", {})

    def check_vis(self, selector):
        """Returns 'visible', 'hidden', or 'not-found'."""
        r = self.ev(f"""
        (function() {{
            var els = document.querySelectorAll('{selector}');
            if (els.length === 0) return 'not-found';
            var vis = false;
            for (var i=0; i<els.length; i++) {{
                if (window.getComputedStyle(els[i]).display !== 'none') vis = true;
            }}
            return vis ? 'visible' : 'hidden';
        }})()
        """)
        return r.get("value", "error")

    def close(self):
        self.ws.close()


def connect_to_sitl(session, sitl_tcp):
    """Attempt to connect the configurator to SITL via TCP."""
    # Select 'tcp' in port dropdown
    r = session.ev("""
    (function() {
        var sel = document.querySelector('select#port');
        if (!sel) return 'no-select';
        sel.value = 'tcp';
        sel.dispatchEvent(new Event('change', {bubbles: true}));
        return sel.value;
    })()
    """)
    if r.get("value") != "tcp":
        return False, f"Could not select TCP port: {r}"
    time.sleep(0.3)

    # Set the TCP host:port
    r = session.ev(f"""
    (function() {{
        var inp = document.querySelector('#port-override');
        if (!inp) return 'no-input';
        inp.value = '{sitl_tcp}';
        inp.dispatchEvent(new Event('input', {{bubbles: true}}));
        inp.dispatchEvent(new Event('change', {{bubbles: true}}));
        return 'set: ' + inp.value;
    }})()
    """)
    time.sleep(0.3)

    # Click the 'a.connect' link (NOT the #connectbutton div — the <a> tag works)
    r = session.ev("""
    (function() {
        var link = document.querySelector('a.connect');
        if (!link) return 'no-a.connect';
        link.click();
        return 'clicked';
    })()
    """)
    if r.get("value") != "clicked":
        return False, f"Click failed: {r}"

    # Wait for connection (up to 10s)
    for _ in range(10):
        time.sleep(1)
        state_r = session.ev("""
        (function() {
            return JSON.stringify({
                connected: !!document.querySelector('a.connect.active'),
                portHidden: window.getComputedStyle(
                    document.querySelector('#portsinput') || document.createElement('div')
                ).display === 'none',
            });
        })()
        """)
        state = json.loads(state_r.get("value", "{}"))
        if state.get("connected") and state.get("portHidden"):
            return True, "connected"

    return False, "Timeout waiting for connection"


def main():
    failures = 0
    print("=" * 60)
    print("TEST: Advanced Tuning Tab - Section Visibility")
    print("=" * 60)
    print()

    target = find_configurator_target()
    print(f"+ Found configurator: {target['title']}")

    session = CDPSession(target["webSocketDebuggerUrl"])
    print("+ Connected to CDP")

    # Check if already connected
    conn_r = session.ev("""
    (function() {
        return JSON.stringify({
            connected: !!document.querySelector('a.connect.active'),
            portHidden: window.getComputedStyle(
                document.querySelector('#portsinput') || document.createElement('div')
            ).display === 'none',
        });
    })()
    """)
    conn = json.loads(conn_r.get("value", "{}"))
    already_connected = conn.get("connected") and conn.get("portHidden")

    if not already_connected:
        print(f"  Not connected. Connecting to SITL at {SITL_TCP}...")
        ok, msg = connect_to_sitl(session, SITL_TCP)
        if not ok:
            print(f"X Could not connect to SITL: {msg}")
            print("  Please start SITL (start_sitl.sh) and re-run.")
            session.close()
            sys.exit(1)
        print("+ Connected to SITL")
    else:
        print("+ Already connected to FC")

    print()

    # --- Test 1: Navigate to Advanced Tuning tab and check platformType ---
    print("--- TEST 1: platformType must be valid (not -1) after tab load ---")

    nav_r = session.ev("""
    (function() {
        var li = document.querySelector('li.tab_advanced_tuning');
        if (!li) return 'li-not-found';
        var a = li.querySelector('a');
        if (!a) return 'a-not-found';
        a.click();
        return 'clicked';
    })()
    """)
    print(f"  Tab click: {nav_r.get('value')}")

    if nav_r.get("value") != "clicked":
        print("X Advanced Tuning tab not found in DOM.")
        failures += 1
    else:
        # Wait for MSPChainer to fetch MIXER_CONFIG and render HTML
        print("  Waiting 4s for tab to load (including MSPChainer fetch)...")
        time.sleep(4)

        # Get FC state via dynamic ESM import
        fc_r = session.ev("""
        import('/js/fc.js').then(m => {
            var FC = m.default;
            return JSON.stringify({
                hasMixerConfig: !!FC.MIXER_CONFIG,
                platformType: FC.MIXER_CONFIG ? FC.MIXER_CONFIG.platformType : -999,
                isAirplane: typeof FC.isAirplane === 'function' ? FC.isAirplane() : null,
                isMultirotor: typeof FC.isMultirotor === 'function' ? FC.isMultirotor() : null,
            });
        })
        """, await_promise=True)
        fc_info = json.loads(fc_r.get("value", "{}"))

        pt = fc_info.get("platformType", -999)
        is_airplane = fc_info.get("isAirplane")
        is_multirotor = fc_info.get("isMultirotor")

        print(f"  FC.MIXER_CONFIG.platformType = {pt}")
        print(f"  FC.isAirplane()   = {is_airplane}")
        print(f"  FC.isMultirotor() = {is_multirotor}")

        if pt == -1 or pt == -999:
            print(f"X FAIL: platformType = {pt}!")
            print("  MIXER_CONFIG was not fetched before rendering.")
            print("  The MSPChainer fix is NOT working.")
            failures += 1
        else:
            print(f"+ PASS: platformType = {pt} (valid). MIXER_CONFIG fetched before render.")

    # --- Test 2: Only correct section is visible ---
    print()
    print("--- TEST 2: Only correct section is visible ---")

    airplane_vis = session.check_vis(".airplaneTuning")
    airplane_title_vis = session.check_vis(".airplaneTuningTitle")
    multirotor_vis = session.check_vis(".multirotorTuning")
    multirotor_title_vis = session.check_vis(".multirotorTuningTitle")

    print(f"  .airplaneTuning:        {airplane_vis}")
    print(f"  .airplaneTuningTitle:   {airplane_title_vis}")
    print(f"  .multirotorTuning:      {multirotor_vis}")
    print(f"  .multirotorTuningTitle: {multirotor_title_vis}")

    if airplane_vis == "not-found" or multirotor_vis == "not-found":
        print("X FAIL: Section selectors not found in DOM — tab may not have loaded.")
        failures += 1
    else:
        both_vis = (airplane_vis == "visible" and multirotor_vis == "visible")
        if both_vis and (is_airplane or is_multirotor):
            print("X FAIL: Both airplane AND multirotor sections visible simultaneously!")
            print("  This is the exact bug symptom. The fix is NOT working.")
            failures += 1
        elif is_multirotor and multirotor_vis == "visible" and airplane_vis == "hidden":
            print("+ PASS: Multirotor — multirotor visible, airplane hidden. Correct!")
        elif is_airplane and airplane_vis == "visible" and multirotor_vis == "hidden":
            print("+ PASS: Airplane — airplane visible, multirotor hidden. Correct!")
        elif not is_airplane and not is_multirotor and both_vis:
            print(f"+ PASS: Generic platform {pt} — both shown (else-branch, expected).")
        else:
            if not both_vis:
                print("+ PASS: Sections not simultaneously visible.")
            else:
                print(f"  Unexpected state: airplane={airplane_vis}, multirotor={multirotor_vis}")
                failures += 1

    session.close()

    print()
    print("=" * 60)
    if failures == 0:
        print("OVERALL RESULT: PASSED")
        print("The fix is working: MIXER_CONFIG is fetched before rendering,")
        print("so platformType is valid when show/hide logic runs.")
    else:
        print(f"OVERALL RESULT: FAILED ({failures} failure(s))")
    print("=" * 60)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
