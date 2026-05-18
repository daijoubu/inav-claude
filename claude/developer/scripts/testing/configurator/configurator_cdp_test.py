#!/usr/bin/env python3
"""Comprehensive CDP Connection Test - Fixed version"""
import asyncio
import websockets
import json
import urllib.request

async def run_tests():
    print("=" * 60)
    print("Chrome DevTools Protocol Connection Test")
    print("=" * 60)
    print()
    
    # Get page
    response = urllib.request.urlopen('http://localhost:9222/json/list')
    pages = json.loads(response.read())
    configurator = next((p for p in pages if p['title'] == 'INAV Configurator'), None)
    
    if not configurator:
        print("❌ INAV Configurator page not found")
        return
    
    print(f"✓ Found INAV Configurator (ID: {configurator['id']})")
    
    # Connect WebSocket
    ws_url = configurator['webSocketDebuggerUrl']
    
    async with websockets.connect(ws_url) as ws:
        print(f"✓ WebSocket connected")
        print()
        
        tests_passed = 0
        tests_total = 0
        
        # Test 1: Get page title
        tests_total += 1
        cmd = {"id": 1, "method": "Runtime.evaluate", "params": {"expression": "document.title", "returnByValue": True}}
        await ws.send(json.dumps(cmd))
        resp = json.loads(await ws.recv())
        if 'result' in resp and 'result' in resp['result']:
            title = resp['result']['result']['value']
            print(f"✓ Runtime.evaluate: Page title = '{title}'")
            tests_passed += 1
        else:
            print(f"✗ Runtime.evaluate failed")
        
        # Test 2: Get accessibility tree
        tests_total += 1
        cmd = {"id": 2, "method": "Accessibility.getFullAXTree", "params": {}}
        await ws.send(json.dumps(cmd))
        resp = json.loads(await ws.recv())
        if 'result' in resp and 'nodes' in resp['result']:
            count = len(resp['result']['nodes'])
            print(f"✓ Accessibility.getFullAXTree: {count} nodes")
            tests_passed += 1
        else:
            print(f"✗ Accessibility.getFullAXTree failed")
        
        # Test 3: Take screenshot
        tests_total += 1
        cmd = {"id": 3, "method": "Page.captureScreenshot", "params": {"format": "png"}}
        await ws.send(json.dumps(cmd))
        resp = json.loads(await ws.recv())
        if 'result' in resp and 'data' in resp['result']:
            size = len(resp['result']['data'])
            print(f"✓ Page.captureScreenshot: {size} chars (base64)")
            tests_passed += 1
        else:
            print(f"✗ Page.captureScreenshot failed")
        
        # Test 4: Query connect button
        tests_total += 1
        cmd = {"id": 4, "method": "Runtime.evaluate", "params": {"expression": "document.querySelector('a.connect') !== null", "returnByValue": True}}
        await ws.send(json.dumps(cmd))
        resp = json.loads(await ws.recv())
        if 'result' in resp and 'result' in resp['result']:
            exists = resp['result']['result']['value']
            print(f"✓ DOM query: Connect button exists = {exists}")
            tests_passed += 1
        else:
            print(f"✗ DOM query failed")
        
        # Test 5: Get button text
        tests_total += 1
        cmd = {"id": 5, "method": "Runtime.evaluate", "params": {"expression": "document.querySelector('a.connect_state')?.textContent || 'not found'", "returnByValue": True}}
        await ws.send(json.dumps(cmd))
        resp = json.loads(await ws.recv())
        if 'result' in resp and 'result' in resp['result']:
            text = resp['result']['result']['value']
            print(f"✓ Get element text: Connect button text = '{text}'")
            tests_passed += 1
        else:
            print(f"✗ Get element text failed")
        
        print()
        print("=" * 60)
        print(f"Results: {tests_passed}/{tests_total} tests passed")
        print("=" * 60)
        
        if tests_passed == tests_total:
            print("\n✅ SUCCESS: CDP connection fully functional!")
            print("\nAll CDP features verified:")
            print("  • WebSocket connection to page")
            print("  • JavaScript evaluation (Runtime.evaluate)")
            print("  • Accessibility tree snapshots")
            print("  • Screenshot capture")
            print("  • DOM querying")
            print("  • Text content extraction")
        else:
            print(f"\n❌ FAILED: {tests_total - tests_passed} test(s) failed")

if __name__ == '__main__':
    asyncio.run(run_tests())
