# Chrome DevTools MCP Test Sequence

Quick reference for testing WASM SITL via MCP.

## Pre-requisites

1. Configurator running: `cd inav-configurator && NODE_ENV=development npm start`
2. Chrome DevTools MCP server connected

## Standard Test Sequence

### 1. Check current page state
```
mcp__chrome-devtools__take_snapshot
```

### 2. Click Connect (find the link with "Connect" text)
```
mcp__chrome-devtools__click uid="<connect-link-uid>"
```

### 3. Wait for connection
```
mcp__chrome-devtools__wait_for text="Disconnect" timeout=10000
```

### 4. IMPORTANT: Dismiss defaults dialog
```
mcp__chrome-devtools__take_snapshot
# Find "Keep current settings" link uid
mcp__chrome-devtools__click uid="<keep-settings-uid>"
```

### 5. Verify connected state
```
mcp__chrome-devtools__take_snapshot
# Should show: "Disconnect" button, profile dropdowns, all tabs
```

### 6. Test disconnect (triggers page reload)
```
mcp__chrome-devtools__click uid="<disconnect-uid>"
mcp__chrome-devtools__wait_for text="Welcome" timeout=5000
```

### 7. Test reconnect
```
mcp__chrome-devtools__take_snapshot
mcp__chrome-devtools__click uid="<connect-uid>"
mcp__chrome-devtools__wait_for text="Disconnect" timeout=10000
```

## Key Element Patterns

After each snapshot, look for these elements:

| State | Element to Find |
|-------|-----------------|
| Disconnected | Link with text "Connect" |
| Connected | Link with text "Disconnect" |
| Defaults dialog | Link with text "Keep current settings" |
| Port selector | Combobox with value "SITL (Browser)" |
| Tabs | Links: Status, Mixer, Configuration, CLI, etc. |

## Console Messages

Check for errors:
```
mcp__chrome-devtools__list_console_messages types=["error"]
```

Check all recent messages:
```
mcp__chrome-devtools__list_console_messages pageSize=20
```

## Inject Test Helpers

```
mcp__chrome-devtools__evaluate_script function="() => {
    // Paste content of wasm-test-console.js here
}"
```

Then call helper functions:
```
mcp__chrome-devtools__evaluate_script function="() => checkWasmState()"
```

## Common Issues

1. **"Element not found"**: UIDs change after page reload. Take a fresh snapshot.
2. **Connection hangs**: Check console for WASM errors.
3. **Dialog not dismissed**: Must click "Keep current settings" before other tests.
4. **Reconnect fails**: Disconnect should reload page. If not, check console.
