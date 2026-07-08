#!/usr/bin/env python3
"""Minimal Chrome DevTools Protocol (CDP) helper for driving the INAV Configurator
Electron renderer in automated tests, when no chrome-devtools MCP tool is available.

Requires: pip install --user websockets  (or --break-system-packages on Arch/PEP668)

Usage pattern:

    import asyncio, websockets
    from cdp_helper import get_configurator_ws, CDP

    async def main():
        ws_url = await get_configurator_ws()
        async with websockets.connect(ws_url, max_size=None) as ws:
            c = CDP(ws)
            print(await c.eval("document.title"))

    asyncio.run(main())

Notes / lessons learned:
- The Configurator's remote debugging port defaults to 9222 (see start-with-debugging.sh).
- FC/GUI/CONFIGURATOR module-scope variables are NOT exposed on `window` (ES modules),
  so you can't do `window.FC...`. Drive the UI through the DOM (click(), .value=,
  dispatchEvent) instead, exactly like a real user/browser automation would.
- To connect to a running SITL instance from the UI: set `#port` select value to
  'sitl' and dispatch a 'change' event, then click 'a.connect'. This calls
  CONFIGURATOR.connection.connect("127.0.0.1:5760", ...) directly - no IP:Port
  field needed (that field is only for the 'tcp'/'udp'/'manual' options).
- jQuery .data() attributes set at <option> creation time (e.g. isSitl, isTcp)
  persist on the DOM node regardless of how you later change .value via plain JS,
  since it's the same element object.
- Always verify with Runtime.exceptionThrown / Runtime.consoleAPICalled (enable
  Runtime.enable + Log.enable) if a UI action silently "does nothing" - the
  serial_backend.js console logging is verbose and will show the real error
  (e.g. "TCP error Error: Port should be >= 0 and < 65536").
"""
import asyncio
import json
import urllib.request
import urllib.error


class CDP:
    """Thin wrapper for Runtime.evaluate over an already-open CDP websocket."""

    def __init__(self, ws):
        self.ws = ws
        self._id = 0

    async def eval(self, expr, timeout=10):
        self._id += 1
        myid = self._id
        await self.ws.send(json.dumps({
            "id": myid,
            "method": "Runtime.evaluate",
            "params": {"expression": expr, "returnByValue": True, "awaitPromise": True},
        }))
        while True:
            raw = await asyncio.wait_for(self.ws.recv(), timeout=timeout)
            r = json.loads(raw)
            if r.get('id') == myid:
                if 'result' in r and 'result' in r['result']:
                    res = r['result']['result']
                    if res.get('subtype') == 'error':
                        raise RuntimeError(f"JS exception: {res.get('description', res)}")
                    if 'value' in res:
                        return res['value']
                    return res
                if 'error' in r:
                    raise RuntimeError(r['error'])
                return r


async def get_configurator_ws(cdp_port=9222, page_title='INAV Configurator'):
    """Find the INAV Configurator renderer page's websocket debugger URL.

    Raises RuntimeError with a clear diagnostic if the debug port isn't reachable
    or the Configurator window isn't found among the open CDP targets.
    """
    url = f'http://localhost:{cdp_port}/json/list'
    try:
        resp = urllib.request.urlopen(url, timeout=5)
    except urllib.error.URLError as e:
        raise RuntimeError(
            f"FAILED to reach CDP endpoint {url}: {e}\n"
            "  Check: Is the Configurator running with --remote-debugging-port=9222?\n"
            "  (e.g. via 'yarn start' / start-with-debugging.sh)\n"
            "  If running in a sandbox, retry with dangerouslyDisableSandbox: true"
        )

    pages = json.loads(resp.read())
    cfg = next((p for p in pages if p.get('title') == page_title), None)
    if not cfg:
        titles = [p.get('title') for p in pages]
        raise RuntimeError(
            f"INAV Configurator page (title='{page_title}') not found in CDP targets. "
            f"Found titles: {titles}"
        )
    return cfg['webSocketDebuggerUrl']
