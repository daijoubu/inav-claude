#!/usr/bin/env python3
"""Fine-grained timing verification of the setting-container race fix.

Verifies:
1. Configuration tab: vbat=ADC/current=ADC (hidden case) -> #dronecan-battery-id-row
   stays hidden the ENTIRE time from t=0 through full settle.
2. Configuration tab: CAN selected -> row correctly shown, no regression.
3. GPS tab: provider=UBLOX (hidden case) -> #gps_dronecan_node_id_row stays hidden
   the entire time.
4. GPS tab: provider=DroneCAN -> row correctly shown, no regression.

Samples visibility at t = 0, 0.1, 0.3, 0.5, 0.7, 1.0, 1.4, 2.0s after the tab
link is clicked (i.e. after process_html()/configureInputs() begins running
fresh), and also installs a jQuery .show()/.toggle() monkeypatch so we can see
exactly when each mechanism touches the row, for root-cause correlation.

NOTE: clicking a.save on these tabs triggers "Settings Saved in EEPROM" +
"Reboot request accepted" -> the FC reboots and the Configurator
auto-reconnects a few seconds later. We must wait for reconnect (and for the
active tab to finish reloading) before switching tabs to run the timing
sample, or the DOM will simply not be there.
"""
import asyncio
import json
import sys

sys.path.insert(0, '/home/robs/Projects/inav-claude/claude/developer/scripts/testing/configurator')
import websockets
from cdp_helper import get_configurator_ws, CDP

SAMPLE_TIMES = [0, 0.1, 0.3, 0.5, 0.7, 1.0, 1.4, 2.0]
HIDDEN_OK = ('none', 'NOT-IN-DOM')

INSTALL_MONKEYPATCH = r"""
(function(){
  if (window.__raceLogInstalled) { return 'already-installed'; }
  window.__raceLogInstalled = true;
  window.__visLog = [];
  var origShow = $.fn.show;
  var origToggle = $.fn.toggle;
  $.fn.show = function(){
    try {
      var ids = this.map(function(){return this.id || ('.'+this.className);}).get();
      window.__visLog.push({t: performance.now(), op:'show', ids: ids});
    } catch(e) {}
    return origShow.apply(this, arguments);
  };
  $.fn.toggle = function(state){
    try {
      var ids = this.map(function(){return this.id || ('.'+this.className);}).get();
      window.__visLog.push({t: performance.now(), op:'toggle', state: state, ids: ids});
    } catch(e) {}
    return origToggle.apply(this, arguments);
  };
  return 'installed';
})()
"""


async def sample_visibility(c, selector):
    """Sample selector's display/visibility at each SAMPLE_TIMES offset from
    the moment the tab link was clicked (t0 stored in window.__clickT0)."""
    samples = []
    start = asyncio.get_event_loop().time()
    for dt in SAMPLE_TIMES:
        target = start + dt
        now = asyncio.get_event_loop().time()
        if target > now:
            await asyncio.sleep(target - now)
        display = await c.eval(
            f"(function(){{var el=$('{selector}'); return el.length ? (el.css('display')||'') : 'NOT-IN-DOM';}})()")
        visible = await c.eval(
            f"(function(){{var el=$('{selector}'); return el.length ? el.is(':visible') : false;}})()")
        parent_display = await c.eval(
            f"(function(){{var el=$('{selector}'); return el.length ? (el.parent().css('display')||'') : 'NOT-IN-DOM';}})()")
        elapsed_since_click = await c.eval("performance.now() - (window.__clickT0 || performance.now())")
        samples.append({
            'sample_dt_requested': dt,
            'elapsed_since_click_ms': elapsed_since_click,
            'display': display,
            'visible': visible,
            'parent_display': parent_display,
        })
    return samples


async def get_vis_log(c, marker_id):
    return await c.eval(f"window.__visLog.filter(o => o.ids.some(id => id.indexOf('{marker_id}') !== -1))")


async def clear_vis_log(c):
    await c.eval("window.__visLog = []; window.__clickT0 = undefined; true")


async def click_tab_and_mark(c, tab_selector):
    await c.eval(f"window.__clickT0 = performance.now(); $('{tab_selector}')[0].click(); true")


async def switch_away(c, other_tab_selector='#tabs li.tab_setup a'):
    await c.eval(f"$('{other_tab_selector}')[0].click(); true")
    await asyncio.sleep(1.5)


async def wait_for_connected(c, timeout=30):
    start = asyncio.get_event_loop().time()
    while asyncio.get_event_loop().time() - start < timeout:
        state = await c.eval("$('a.connect').hasClass('active')")
        if state:
            return True
        await asyncio.sleep(0.5)
    return False


async def click_save_and_wait_for_reboot_reconnect(c, timeout=30):
    """Click a.save, then wait for the FC to disconnect (reboot) and
    reconnect. Returns True if reconnected within timeout."""
    await c.eval("$('a.save')[0].click(); true")
    # Wait for disconnect first (reboot in progress), then reconnect.
    start = asyncio.get_event_loop().time()
    saw_disconnect = False
    while asyncio.get_event_loop().time() - start < timeout:
        state = await c.eval("$('a.connect').hasClass('active')")
        if not state:
            saw_disconnect = True
            break
        await asyncio.sleep(0.3)
    if not saw_disconnect:
        print("  WARNING: never saw disconnect after save click (maybe no reboot needed)")
    ok = await wait_for_connected(c, timeout=timeout)
    if ok:
        # give the reloaded tab a moment to finish its own settings fetch
        await asyncio.sleep(2.0)
    return ok


def print_report(title, samples, vis_log):
    print(f"\n=== {title} ===")
    print(f"{'req_dt':>8} {'elapsed_ms':>11} {'display':>10} {'visible':>8} {'parent_display':>15}")
    for s in samples:
        print(f"{s['sample_dt_requested']:>8.2f} {s['elapsed_since_click_ms']:>11.1f} "
              f"{s['display']:>10} {str(s['visible']):>8} {s['parent_display']:>15}")
    print("jQuery show()/toggle() calls touching this row (relative to click):")
    if not vis_log:
        print("  (none captured)")
    for entry in vis_log:
        print(f"  op={entry['op']:6s} state={entry.get('state')!s:6s} ids={entry['ids']}")


async def main():
    ws_url = await get_configurator_ws()
    async with websockets.connect(ws_url, max_size=None) as ws:
        c = CDP(ws)

        connected = await wait_for_connected(c, timeout=5)
        if not connected:
            print("FAILED: Configurator is not connected to SITL. Aborting.")
            print("  Check: is SITL running on port 5760? Is the Configurator's port select set to 'sitl'?")
            return

        install_result = await c.eval(INSTALL_MONKEYPATCH)
        print("Monkeypatch install:", install_result)

        results = {}

        # ------------------------------------------------------------------
        # TEST 1: Configuration tab, vbat=ADC / current=ADC (hidden case)
        # ------------------------------------------------------------------
        await switch_away(c)
        await clear_vis_log(c)
        await click_tab_and_mark(c, '#tabs li.tab_configuration a')
        samples = await sample_visibility(c, '#dronecan-battery-id-row')
        vbat_val = await c.eval("$('#vbat_meter_type option:selected').text()")
        cur_val = await c.eval("$('#current_meter_type option:selected').text()")
        vis_log = await get_vis_log(c, 'dronecan-battery-id-row')
        print_report(f"TEST 1: Configuration tab, vbat={vbat_val} current={cur_val} (expect HIDDEN always)",
                     samples, vis_log)
        test1_pass = all(s['display'] in HIDDEN_OK and not s['visible'] for s in samples)
        results['test1_config_hidden_case'] = test1_pass
        print(f">>> TEST 1 RESULT: {'PASS' if test1_pass else 'FAIL - row was visible at some point!'}")

        # ------------------------------------------------------------------
        # TEST 2: Configuration tab, vbat=CAN (shown case) -- set + save
        # ------------------------------------------------------------------
        print("\nSetting vbat_meter_type=CAN and saving (this triggers an FC reboot)...")
        await c.eval("""
        (function(){
          var sel = document.getElementById('vbat_meter_type');
          sel.value = '6'; // CAN
          sel.dispatchEvent(new Event('change'));
          return sel.value;
        })()
        """)
        await asyncio.sleep(0.3)
        reconnected = await click_save_and_wait_for_reboot_reconnect(c)
        print("Reconnected after save:", reconnected)
        if not reconnected:
            print("ABORT TEST 2: never reconnected after save/reboot")
            results['test2_config_shown_case'] = None
        else:
            await switch_away(c)
            await clear_vis_log(c)
            await click_tab_and_mark(c, '#tabs li.tab_configuration a')
            samples2 = await sample_visibility(c, '#dronecan-battery-id-row')
            vbat_val2 = await c.eval("$('#vbat_meter_type option:selected').text()")
            cur_val2 = await c.eval("$('#current_meter_type option:selected').text()")
            vis_log2 = await get_vis_log(c, 'dronecan-battery-id-row')
            print_report(f"TEST 2: Configuration tab, vbat={vbat_val2} current={cur_val2} (expect SHOWN at settle)",
                         samples2, vis_log2)
            test2_pass = samples2[-1]['display'] not in HIDDEN_OK and samples2[-1]['visible'] is True
            results['test2_config_shown_case'] = test2_pass
            print(f">>> TEST 2 RESULT: {'PASS' if test2_pass else 'FAIL - row not shown at settle!'}")

        # Revert vbat_meter_type back to ADC for cleanliness
        print("\nReverting vbat_meter_type back to ADC and saving...")
        await c.eval("""
        (function(){
          var sel = document.getElementById('vbat_meter_type');
          if (sel) {
            sel.value = '1'; // ADC
            sel.dispatchEvent(new Event('change'));
          }
        })()
        """)
        await asyncio.sleep(0.3)
        await click_save_and_wait_for_reboot_reconnect(c)

        # ------------------------------------------------------------------
        # TEST 3: GPS tab, provider=UBLOX (hidden case)
        # ------------------------------------------------------------------
        await switch_away(c)
        await click_tab_and_mark(c, '#tabs li.tab_gps a')
        await asyncio.sleep(1.5)
        gps_opts = await c.eval(
            "$('#gps_protocol option').map(function(){return {v:$(this).val(), t:$(this).text()}}).get()")
        print("\nGPS protocol options:", json.dumps(gps_opts))
        current_gps_type = await c.eval("$('#gps_protocol').val()")
        print("current gps_type value:", current_gps_type)

        ublox_val = next((o['v'] for o in gps_opts if 'UBLOX' in o['t'].upper() and 'CAN' not in o['t'].upper()), None)
        dronecan_val = next((o['v'] for o in gps_opts if 'DRONECAN' in o['t'].upper() or 'CAN' in o['t'].upper()), None)
        print(f"UBLOX option value: {ublox_val}, DroneCAN option value: {dronecan_val}")

        if current_gps_type != ublox_val and ublox_val is not None:
            print(f"Setting gps_protocol to UBLOX ({ublox_val}) and saving...")
            await c.eval(f"""
            (function(){{
              var sel = document.getElementById('gps_protocol');
              sel.value = '{ublox_val}';
              sel.dispatchEvent(new Event('change'));
              return sel.value;
            }})()
            """)
            await asyncio.sleep(0.3)
            await click_save_and_wait_for_reboot_reconnect(c)

        await switch_away(c)
        await clear_vis_log(c)
        await click_tab_and_mark(c, '#tabs li.tab_gps a')
        samples3 = await sample_visibility(c, '#gps_dronecan_node_id_row')
        gps_type_now = await c.eval("$('#gps_protocol option:selected').text()")
        vis_log3 = await get_vis_log(c, 'gps_dronecan_node_id_row')
        print_report(f"TEST 3: GPS tab, provider={gps_type_now} (expect HIDDEN always)", samples3, vis_log3)
        test3_pass = all(s['display'] in HIDDEN_OK and not s['visible'] for s in samples3)
        results['test3_gps_hidden_case'] = test3_pass
        print(f">>> TEST 3 RESULT: {'PASS' if test3_pass else 'FAIL - row was visible at some point!'}")

        # ------------------------------------------------------------------
        # TEST 4: GPS tab, provider=DroneCAN (shown case)
        # ------------------------------------------------------------------
        if dronecan_val is not None:
            print(f"\nSetting gps_protocol to DroneCAN ({dronecan_val}) and saving...")
            await c.eval(f"""
            (function(){{
              var sel = document.getElementById('gps_protocol');
              sel.value = '{dronecan_val}';
              sel.dispatchEvent(new Event('change'));
              return sel.value;
            }})()
            """)
            await asyncio.sleep(0.3)
            reconnected4 = await click_save_and_wait_for_reboot_reconnect(c)
            print("Reconnected after save:", reconnected4)

            if not reconnected4:
                print("ABORT TEST 4: never reconnected after save/reboot")
                results['test4_gps_shown_case'] = None
            else:
                await switch_away(c)
                await clear_vis_log(c)
                await click_tab_and_mark(c, '#tabs li.tab_gps a')
                samples4 = await sample_visibility(c, '#gps_dronecan_node_id_row')
                gps_type_now4 = await c.eval("$('#gps_protocol option:selected').text()")
                vis_log4 = await get_vis_log(c, 'gps_dronecan_node_id_row')
                print_report(f"TEST 4: GPS tab, provider={gps_type_now4} (expect SHOWN at settle)", samples4, vis_log4)
                test4_pass = samples4[-1]['display'] not in HIDDEN_OK and samples4[-1]['visible'] is True
                results['test4_gps_shown_case'] = test4_pass
                print(f">>> TEST 4 RESULT: {'PASS' if test4_pass else 'FAIL - row not shown at settle!'}")

            # Revert back to UBLOX for cleanliness
            print(f"\nReverting gps_protocol back to UBLOX ({ublox_val}) and saving...")
            await c.eval(f"""
            (function(){{
              var sel = document.getElementById('gps_protocol');
              if (sel) {{
                sel.value = '{ublox_val}';
                sel.dispatchEvent(new Event('change'));
              }}
            }})()
            """)
            await asyncio.sleep(0.3)
            await click_save_and_wait_for_reboot_reconnect(c)
        else:
            print("\nTEST 4 SKIPPED: no DroneCAN option found in gps_protocol select "
                  "(firmware likely built without DroneCAN GPS support)")
            results['test4_gps_shown_case'] = None

        print("\n\n========== SUMMARY ==========")
        for k, v in results.items():
            status = 'PASS' if v is True else ('SKIPPED/INCONCLUSIVE' if v is None else 'FAIL')
            print(f"{k}: {status}")


asyncio.run(main())
