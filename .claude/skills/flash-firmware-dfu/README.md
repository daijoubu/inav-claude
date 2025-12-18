# Flight Controller CLI Tools

Python scripts for interacting with INAV flight controller CLI via serial port.

## Scripts

### fc-cli.py - Modular CLI Command Tool ⭐ RECOMMENDED

Flexible tool for sending any CLI command to the flight controller.

**Usage:**
```bash
./fc-cli.py <command> [port]
```

**Examples:**
```bash
# Show task execution times
./fc-cli.py tasks

# Show firmware version
./fc-cli.py version

# Reboot to DFU mode
./fc-cli.py dfu

# Custom CLI command
./fc-cli.py "get gyro_lpf1_static_hz"

# Specify port
./fc-cli.py tasks /dev/ttyUSB0
```

**Built-in commands:**
- `dfu` - Reboot to DFU bootloader
- `tasks` - Show task execution times (scheduler performance)
- `status` - Flight controller status
- `version` - Firmware version
- Any other CLI command works too!

### reboot-to-dfu.py - DFU Reboot Only

Standalone script that only reboots to DFU mode. Kept for backwards compatibility.

**Usage:**
```bash
./reboot-to-dfu.py [port]
```

**Note:** `fc-cli.py dfu` does the same thing and is more flexible.

## How It Works

Both scripts implement the correct CLI entry protocol from `inav-configurator/js/protocols/stm32.js`:

1. Open serial port (default 115200 baud)
2. Send `####\r\n` to enter CLI mode
3. **Wait for "CLI" prompt in response** (with timeout)
4. Send the command
5. Read response (except `dfu` which disconnects immediately)

### Why This Approach?

Simple shell commands like this **don't work reliably**:
```bash
# ❌ DON'T DO THIS - race condition!
echo -ne '####\r\n' > /dev/ttyACM0
sleep 0.25  # Blindly sleep, doesn't check if CLI is ready
echo -ne 'tasks\r\n' > /dev/ttyACM0
```

The problem:
- Doesn't wait for actual CLI prompt
- Can't read the response
- Race condition if FC takes >250ms to respond

## Requirements

```bash
pip3 install pyserial
```

## Adding New Commands to fc-cli.py

Edit `fc-cli.py` and add to the `COMMANDS` dictionary:

```python
COMMANDS = {
    'mynewcommand': {
        'handler': lambda cli: cmd_generic(cli, 'mynewcommand'),
        'description': 'What this command does',
        'read_response': True,
    },
}
```

For commands needing custom handling, create a handler function:

```python
def cmd_mycommand(cli):
    """Custom handler for mycommand."""
    response = cli.send_command('mycommand', read_response=True)
    cli.close()

    # Custom processing of response
    print("Custom output:", response)
    return 0

COMMANDS = {
    'mycommand': {
        'handler': cmd_mycommand,
        'description': 'My custom command',
        'read_response': True,
    },
}
```

## Development Notes

### Based on Working Code

These scripts replicate the proven DFU reboot logic from `inav-configurator/js/protocols/stm32.js:184`.

**Key insight:** Must wait for CLI prompt before sending command, not just sleep.

### Future Extensions

Easy to add:
- `dump` - Backup all settings
- `diff` - Show non-default settings
- `get <setting>` - Read specific setting
- `set <setting> <value>` - Change setting
- Custom analysis of `tasks` output (parse and display as table)

## Testing

```bash
# Test help
./fc-cli.py --help

# Test with invalid port (should error gracefully)
./fc-cli.py tasks /dev/null
```

## Files

- `fc-cli.py` - Main modular CLI tool
- `reboot-to-dfu.py` - Standalone DFU reboot script
- `reboot-to-dfu.sh` - Bash version (less reliable, kept for reference)
- `SKILL.md` - Full skill documentation
- `README.md` - This file
