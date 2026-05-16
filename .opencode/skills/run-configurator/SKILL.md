---
name: run-configurator
description: Launch INAV Configurator in development mode for testing
triggers:
  - run configurator
  - start configurator
  - launch configurator
  - start the configurator
  - run the configurator
  - launch the configurator app
---

# Run INAV Configurator

Launch the INAV Configurator desktop application in development mode for testing changes.

## Quick Start

```bash
cd inav-configurator
ENABLE_REMOTE_DEBUGGING=1 NODE_ENV=development npm start --remote-debugging-port=9222
```

This launches the Electron app in development mode with hot-reload enabled.

## Running in Background

If you need to continue working while the configurator runs:

```bash
cd inav-configurator
ENABLE_REMOTE_DEBUGGING=1 NODE_ENV=development npm start --remote-debugging-port=9222 &
```

Or use the Bash tool with `run_in_background: true` parameter.

## Why NODE_ENV=development?

The `NODE_ENV=development` environment variable:
- Enables development features and debugging
- Enables hot-reload for faster iteration
- May show additional console logging
- Required for proper development mode operation

## Common Issues

| Problem | Solution |
|---------|----------|
| `npm start` fails | New installations: Run `npm install` first to ensure dependencies are installed |
| Missing NODE_ENV warning | Always use `ENABLE_REMOTE_DEBUGGING=1 NODE_ENV=development npm start --remote-debugging-port=9222` |
| Port already in use | Another instance may be running - check with `ps aux \| grep electron` |
| Changes not reflected | The app should hot-reload, but you may need to restart |

## Development Workflow

1. Make changes to configurator code
2. Run configurator to test changes: `ENABLE_REMOTE_DEBUGGING=1 NODE_ENV=development npm start --remote-debugging-port=9222 &`
3. The app should automatically reload when files change
4. Check browser console (Ctrl+Shift+I / Cmd+Option+I) for errors

## Stopping the Configurator

- If running in foreground: Press Ctrl+C in the terminal
- If running in background: `pkill -f "electron.*configurator"` or use the app's quit button

## Building for Distribution

This skill runs the configurator in development mode. To create distributable packages:

```bash
cd inav-configurator
npm run package  # Package the app
npm run make     # Create installers
```

---

## Related Skills

- **build-sitl** - Build SITL firmware to test with configurator
- **test-crsf-sitl** - Complete CRSF telemetry testing workflow (uses configurator for setup)
- **sitl-arm** - Arm SITL for testing (often used with configurator)
- **pr-review** - Test configurator PRs locally using this skill
