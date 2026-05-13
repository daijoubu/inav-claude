#!/usr/bin/env python3
"""
Tab Sweep v2 for INAV Configurator
Tests all connected tabs for console errors after the ES6 module merge.

Uses Chrome DevTools Protocol (CDP) via WebSocket.
Tabs are identified by their CSS class names (e.g., tab_setup, tab_led_strip).
FC must already be connected, or script will attempt connection.

Usage: python3 tab_sweep_v2.py
"""

import json
import time
import sys
import threading
import queue
import urllib.request
from websocket import create_connection, WebSocketTimeoutException

CDP_HOST = 'localhost'
CDP_PORT = 9222
WAIT_AFTER_TAB = 3.5        # seconds to wait after clicking each tab for it to fully load
WAIT_FOR_CONNECT = 12.0     # seconds to wait for FC connection
WAIT_SWITCH = 1.5           # seconds between tabs in cleanup-check test

# Pre-existing errors to ignore (unrelated to this merge)
IGNORE_PATTERNS = [
    'debug_trace',
    'options.js',
    'stream',
    'timers',
    '429',
    'WebGL',
    'semver',
    'ERR_FILE_NOT_FOUND',
    'net::ERR_',
    'favicon',
    'source map',
    'sourceMappingURL',
    'devtools',
    'Security Warning',
    'webSecurity',
    'allowRunningInsecureContent',
    'Content-Security-Policy',
    'unsafe-eval',
    'Electron Security',
]

# Tabs to skip (nav groups, external links, toggles)
SKIP_CLASSES = {
    'nav-group',
    'nav-toggle-all',
    'tab_help',  # external link to GitHub wiki
}

def should_ignore(msg):
    if not msg:
        return True
    m = msg.lower()
    for p in IGNORE_PATTERNS:
        if p.lower() in m:
            return True
    return False


class CDPClient:
    def __init__(self, ws_url):
        self.ws_url = ws_url
        self.ws = None
        self._msg_id = 1
        self._lock = threading.Lock()
        self._pending = {}
        self._event_queue = queue.Queue()
        self._reader_thread = None
        self._running = False
        self.events_by_tab = {}
        self._current_tab = None

    def connect(self):
        print(f"Connecting to CDP: {self.ws_url}")
        try:
            self.ws = create_connection(
                self.ws_url,
                timeout=10,
                suppress_origin=True  # Required: Electron rejects unknown origins
            )
            self._running = True
            self._reader_thread = threading.Thread(target=self._reader, daemon=True)
            self._reader_thread.start()
            print("  Connected to CDP")
            return True
        except Exception as e:
            print(f"  FAILED to connect to CDP: {e}")
            print("  Note: If running in sandbox, retry with dangerouslyDisableSandbox: true")
            return False

    def set_current_tab(self, tab_name):
        self._current_tab = tab_name
        if tab_name not in self.events_by_tab:
            self.events_by_tab[tab_name] = {'errors': [], 'warnings': []}

    def record(self, msg, level='error'):
        tab = self._current_tab or 'unknown'
        if tab not in self.events_by_tab:
            self.events_by_tab[tab] = {'errors': [], 'warnings': []}
        bucket = 'errors' if level == 'error' else 'warnings'
        self.events_by_tab[tab][bucket].append(msg)
        icon = 'X' if level == 'error' else '!'
        print(f"  [{icon} {level.upper()}] {msg[:200]}")

    def _reader(self):
        while self._running:
            try:
                data = self.ws.recv()
                msg = json.loads(data)
                if 'id' in msg and msg['id'] in self._pending:
                    self._pending[msg['id']].put(msg)
                elif 'method' in msg:
                    self._process_event(msg)
            except WebSocketTimeoutException:
                pass
            except Exception as e:
                if self._running:
                    self._event_queue.put({'method': '_error', 'error': str(e)})
                break

    def _process_event(self, msg):
        method = msg.get('method', '')
        params = msg.get('params', {})

        if method == 'Runtime.consoleAPICalled':
            evt_type = params.get('type', '')
            if evt_type not in ('error', 'warning', 'warn'):
                return
            args = params.get('args', [])
            text = ' '.join(
                str(a.get('value', a.get('description', json.dumps(a))))
                for a in args
            )
            if not should_ignore(text):
                level = 'error' if evt_type == 'error' else 'warning'
                self.record(f"console.{evt_type}: {text[:250]}", level)

        elif method == 'Runtime.exceptionThrown':
            exc = params.get('exceptionDetails', {})
            exc_obj = exc.get('exception', {})
            text = exc_obj.get('description') or exc.get('text') or json.dumps(exc)
            if not should_ignore(text):
                self.record(f"EXCEPTION: {text[:250]}")

        elif method == 'Log.entryAdded':
            entry = params.get('entry', {})
            if entry.get('level') in ('error', 'warning'):
                text = entry.get('text', '')
                if not should_ignore(text):
                    lvl = 'error' if entry['level'] == 'error' else 'warning'
                    self.record(f"log.{entry['level']}: {text[:250]}", lvl)

    def send(self, method, params=None):
        with self._lock:
            msg_id = self._msg_id
            self._msg_id += 1
        payload = {'id': msg_id, 'method': method, 'params': params or {}}
        result_q = queue.Queue()
        self._pending[msg_id] = result_q
        self.ws.send(json.dumps(payload))
        try:
            result = result_q.get(timeout=12)
            if msg_id in self._pending:
                del self._pending[msg_id]
            if 'error' in result:
                raise RuntimeError(f"CDP error: {result['error']}")
            return result.get('result', {})
        except queue.Empty:
            if msg_id in self._pending:
                del self._pending[msg_id]
            raise TimeoutError(f"Timeout waiting for {method}")

    def evaluate(self, expression):
        result = self.send('Runtime.evaluate', {
            'expression': expression,
            'awaitPromise': False,
            'returnByValue': True,
            'allowUnsafeEvalBlockedByCSP': True,
        })
        val = result.get('result', {})
        if val.get('subtype') == 'error':
            raise RuntimeError(f"JS eval error: {val.get('description', '')}")
        raw = val.get('value')
        if isinstance(raw, str):
            try:
                return json.loads(raw)
            except Exception:
                return raw
        return raw

    def close(self):
        self._running = False
        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass


def get_cdp_ws_url():
    try:
        url = f'http://{CDP_HOST}:{CDP_PORT}/json'
        with urllib.request.urlopen(url, timeout=5) as resp:
            targets = json.loads(resp.read().decode())
        for target in targets:
            if 'INAV Configurator' in target.get('title', '') or \
               'localhost:5174' in target.get('url', ''):
                return target['webSocketDebuggerUrl']
        for target in targets:
            if target.get('type') == 'page' and 'DevTools' not in target.get('title', ''):
                return target['webSocketDebuggerUrl']
        return None
    except Exception as e:
        print(f"Error fetching CDP targets: {e}")
        return None


def main():
    print("=" * 65)
    print("       INAV Configurator Tab Sweep v2")
    print("=" * 65)

    ws_url = get_cdp_ws_url()
    if not ws_url:
        print("FAIL: Could not find INAV Configurator CDP target")
        print("      Is the configurator running at localhost:5174?")
        sys.exit(1)

    print(f"CDP target: {ws_url[:80]}")

    cdp = CDPClient(ws_url)
    if not cdp.connect():
        sys.exit(1)

    # Enable CDP domains for error monitoring
    cdp.send('Runtime.enable')
    cdp.send('Log.enable')
    cdp.send('Network.enable')
    print("CDP domains enabled\n")

    # -------------------------------------------------------
    # Inject window-level error traps
    # -------------------------------------------------------
    cdp.set_current_tab('startup')
    cdp.evaluate('''
        window.__sweepErrors = [];
        if (!window.__sweepErrHandler) {
            window.__sweepErrHandler = function(e) {
                window.__sweepErrors.push({type:"error", msg: e.message + " @ " + (e.filename||"?") + ":" + e.lineno});
            };
            window.addEventListener("error", window.__sweepErrHandler);
        }
        if (!window.__sweepRejHandler) {
            window.__sweepRejHandler = function(e) {
                window.__sweepErrors.push({type:"rejection", msg: String(e.reason)});
            };
            window.addEventListener("unhandledrejection", window.__sweepRejHandler);
        }
        if (!window.__origConsoleError) {
            window.__origConsoleError = console.error.bind(console);
            console.error = function() {
                var msg = Array.prototype.slice.call(arguments).join(" ");
                window.__sweepErrors.push({type:"console.error", msg: msg});
                window.__origConsoleError.apply(console, arguments);
            };
        }
        "injected"
    ''')
    print("Error listeners injected")

    # -------------------------------------------------------
    # Check if FC is already connected
    # -------------------------------------------------------
    time.sleep(0.5)
    state = cdp.evaluate('''
        JSON.stringify({
            connectClass: (document.querySelector(".connect")||{className:""}).className,
            activeTab: (document.querySelector("#tabs li.active")||{className:""}).className,
            portHidden: (document.querySelector("#portsinput")||{style:{display:""}}).style.display === "none"
        })
    ''')
    print(f"Page state: {json.dumps(state, indent=2)}")

    already_connected = (
        isinstance(state, dict) and
        ('active' in state.get('connectClass', '') or state.get('portHidden'))
    )

    # -------------------------------------------------------
    # Connect if needed
    # -------------------------------------------------------
    if not already_connected:
        print("\n--- FC not connected, attempting connection ---")
        cdp.set_current_tab('connection_setup')

        # Try to set the port
        port_result = cdp.evaluate('''
            (function() {
                // INAV Configurator uses a custom port picker, try to find ttyACM0
                var portItems = document.querySelectorAll(".portsinput__item, [data-port-id]");
                var found = null;
                for (var i=0; i<portItems.length; i++) {
                    var item = portItems[i];
                    if (item.textContent.indexOf("ttyACM0") > -1 || item.getAttribute("data-port-id") === "/dev/ttyACM0") {
                        item.click();
                        found = item.textContent.trim();
                        break;
                    }
                }
                return found ? "set: " + found : "not found (" + portItems.length + " items)";
            })()
        ''')
        print(f"Port select: {port_result}")

        time.sleep(0.3)
        click_result = cdp.evaluate('''
            (function() {
                var btn = document.querySelector("a.connect");
                if (btn) { btn.click(); return "clicked: " + btn.textContent.trim(); }
                return "connect button not found";
            })()
        ''')
        print(f"Connect click: {click_result}")

        print(f"Waiting up to {WAIT_FOR_CONNECT}s for FC connection...")
        t_start = time.time()
        while time.time() - t_start < WAIT_FOR_CONNECT:
            time.sleep(0.7)
            status = cdp.evaluate('''
                JSON.stringify({
                    connectClass: (document.querySelector(".connect")||{className:""}).className,
                    activeTab: (document.querySelector("#tabs li.active")||{className:""}).className
                })
            ''')
            s = status if isinstance(status, dict) else {}
            if 'active' in s.get('connectClass', '') or s.get('activeTab', '').startswith('tab_'):
                print(f"  FC Connected! {json.dumps(s)}")
                already_connected = True
                break
            print(f"  Waiting... ({s.get('connectClass','?')})")

        if not already_connected:
            print("  WARNING: Connection status unclear, continuing anyway")
    else:
        print("FC already connected (portsinput hidden, connect button active)")

    time.sleep(1.0)

    # -------------------------------------------------------
    # Discover connected tabs (all tab_* classes except skipped)
    # -------------------------------------------------------
    print("\n--- Discovering tabs ---")
    tabs_raw = cdp.evaluate('''
        (function() {
            var items = document.querySelectorAll("#tabs li");
            var result = [];
            for (var i=0; i<items.length; i++) {
                var li = items[i];
                var cls = li.className.trim();
                var computed = window.getComputedStyle(li);
                var a = li.querySelector("a");
                var href = a ? (a.getAttribute("href") || "") : "";
                var text = (a ? a.textContent : li.textContent).trim().split("\\n")[0].trim();
                result.push({
                    cls: cls,
                    text: text.substring(0,30),
                    href: href,
                    computedDisplay: computed.display,
                    active: li.classList.contains("active")
                });
            }
            return JSON.stringify(result);
        })()
    ''')

    all_tabs = tabs_raw if isinstance(tabs_raw, list) else []
    print(f"Found {len(all_tabs)} total tab items")

    # Filter to clickable tabs: must be tab_* class, visible, not skipped, not nav groups
    clickable = []
    for t in all_tabs:
        cls = t.get('cls', '')
        primary_class = cls.split()[0] if cls else ''
        if not primary_class.startswith('tab_'):
            continue
        if primary_class in SKIP_CLASSES:
            continue
        if t.get('computedDisplay') == 'none':
            continue
        if not t.get('href') and not t.get('text'):
            continue
        # Avoid duplicate mission_control entry
        if any(c['cls'].split()[0] == primary_class for c in clickable):
            continue
        clickable.append({
            'cls': primary_class,
            'text': t.get('text', primary_class),
        })

    print(f"Clickable connected tabs ({len(clickable)}):")
    for t in clickable:
        print(f"  {t['cls']:35s}  \"{t['text']}\"")

    if len(clickable) < 5:
        print("\nWARNING: Very few tabs found. FC may not be connected, or tab discovery failed.")
        print("Full tab list for diagnosis:")
        for t in all_tabs:
            print(f"  {t}")

    # -------------------------------------------------------
    # Sweep each tab
    # -------------------------------------------------------
    print("\n--- Sweeping tabs ---")

    def collect_window_errors(tab_name):
        errs = cdp.evaluate('''
            (function(){var e=window.__sweepErrors||[];window.__sweepErrors=[];return JSON.stringify(e);})()
        ''')
        if isinstance(errs, str):
            try:
                errs = json.loads(errs)
            except Exception:
                errs = []
        elif not isinstance(errs, list):
            errs = []
        for e in errs:
            msg = e.get('msg', '')
            if not should_ignore(msg):
                cdp.record(f"{e.get('type','err')}: {msg[:200]}", 'error')

    for tab in clickable:
        cls = tab['cls']
        text = tab['text']
        cdp.set_current_tab(text)

        print(f"\n>>> Tab: \"{text}\" ({cls})")

        # Collect any pending errors from before click
        collect_window_errors(text)

        # Click the tab via its class
        click_res = cdp.evaluate(f'''
            (function(){{
                var li = document.querySelector("li.{cls}");
                if (!li) return "li not found for class {cls}";
                var a = li.querySelector("a");
                if (a) {{ a.click(); return "clicked a in " + li.className; }}
                li.click();
                return "clicked li " + li.className;
            }})()
        ''')
        print(f"  Click: {click_res}")

        # Wait for tab to load
        time.sleep(WAIT_AFTER_TAB)

        # Collect errors that fired during load
        collect_window_errors(text)

        # Check active tab and whether content loaded
        tab_state = cdp.evaluate('''
            JSON.stringify({
                activeTab: (document.querySelector("#tabs li.active")||{className:""}).className.split(" ")[0],
                hasMainContent: !!(document.querySelector(".content .tab, .tab-pane.active, [data-ng-view]"))
            })
        ''')
        ts = tab_state if isinstance(tab_state, dict) else {}
        print(f"  Active: {ts.get('activeTab','?')}")

        data = cdp.events_by_tab.get(text, {})
        err_cnt = len(data.get('errors', []))
        warn_cnt = len(data.get('warnings', []))
        status = "PASS" if err_cnt == 0 else "FAIL"
        print(f"  Result: {status} ({err_cnt} errors, {warn_cnt} warnings)")

    # -------------------------------------------------------
    # Tab switching test — detect "cleanup is not a function"
    # -------------------------------------------------------
    print("\n--- Tab switching test (cleanup error detection) ---")
    cdp.set_current_tab('tab_switching')

    # Use a subset of tabs that exercise the merge-affected areas
    switch_focus = ['tab_led_strip', 'tab_configuration', 'tab_setup', 'tab_gps',
                    'tab_receiver', 'tab_osd', 'tab_outputs', 'tab_pid_tuning']
    switch_tabs = [t for t in clickable if t['cls'] in switch_focus]
    # Add any not already in list, up to 10 total
    for t in clickable:
        if len(switch_tabs) >= 10:
            break
        if t not in switch_tabs:
            switch_tabs.append(t)

    for i, tab in enumerate(switch_tabs):
        next_tab = switch_tabs[(i + 1) % len(switch_tabs)]
        cdp.evaluate(f'''
            (function(){{
                var li = document.querySelector("li.{next_tab['cls']}");
                if (li) {{ var a = li.querySelector("a"); if (a) a.click(); else li.click(); }}
            }})()
        ''')
        time.sleep(WAIT_SWITCH)

        # Check for cleanup errors specifically
        errs = cdp.evaluate('''
            (function(){var e=window.__sweepErrors||[];window.__sweepErrors=[];return JSON.stringify(e);})()
        ''')
        if isinstance(errs, str):
            try:
                errs = json.loads(errs)
            except Exception:
                errs = []
        elif not isinstance(errs, list):
            errs = []

        for e in errs:
            msg = e.get('msg', '')
            if not should_ignore(msg):
                tag = ""
                if 'cleanup' in msg.lower() or 'is not a function' in msg.lower():
                    tag = "[CLEANUP] "
                cdp.record(f"{tag}switch->{next_tab['cls']}: {msg[:200]}")
                if tag:
                    print(f"  [X CLEANUP ERROR on switch to {next_tab['cls']}]: {msg[:150]}")

    sw = cdp.events_by_tab.get('tab_switching', {})
    sw_errors = sw.get('errors', [])
    print(f"  Switching test: {'PASS' if not sw_errors else 'FAIL'} ({len(sw_errors)} errors)")

    cdp.close()

    # -------------------------------------------------------
    # Final Report
    # -------------------------------------------------------
    print("\n")
    print("=" * 65)
    print("              FINAL TAB SWEEP REPORT")
    print("=" * 65)

    passing = []
    failing = []

    # Exclude noise-only tabs from summary
    skip_summary = {'startup', 'connection_setup', 'unknown'}

    for tab_name, data in cdp.events_by_tab.items():
        if tab_name in skip_summary and not data.get('errors') and not data.get('warnings'):
            continue
        errs = data.get('errors', [])
        warns = data.get('warnings', [])
        if errs:
            failing.append((tab_name, errs, warns))
        else:
            passing.append((tab_name, warns))

    print(f"\nPASSING ({len(passing)} tabs/phases):")
    for name, warns in passing:
        w_note = f"  ({len(warns)} warnings)" if warns else ""
        print(f"  PASS  {name}{w_note}")

    if failing:
        print(f"\nFAILING ({len(failing)} tabs/phases):")
        for name, errs, warns in failing:
            print(f"  FAIL  {name}")
            for e in errs:
                print(f"          ERROR: {e[:220]}")
            for w in warns:
                print(f"          WARN:  {w[:220]}")
    else:
        print("\n  All tabs PASSED - no errors detected!")

    total_errors = sum(len(d.get('errors', [])) for d in cdp.events_by_tab.values())
    total_warnings = sum(len(d.get('warnings', [])) for d in cdp.events_by_tab.values())
    print(f"\nTotal: {total_errors} errors, {total_warnings} warnings")
    print("(Filtered: debug_trace, options.js, stream, timers, 429, WebGL, semver,")
    print("           Electron Security Warnings, source maps, favicon)")
    print()

    return 0 if total_errors == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
