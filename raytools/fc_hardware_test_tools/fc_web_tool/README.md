# Flight Controller Web Test Tool

A web-based interface for testing flight controllers via MSP protocol. Works on any Linux system (Ubuntu, Raspberry Pi, Debian, etc.) with mobile-friendly interface accessible from phones and tablets.

## Platform Support

✅ **Linux** (Ubuntu, Debian, Raspberry Pi, etc.)
✅ **macOS** (with minor adjustments for USB device paths)
⚠️ **Windows** (not tested, may require WSL)

**No Raspberry Pi-specific dependencies** - uses standard USB serial communication, so it works on any system with Python 3 and USB ports.

## Features

- **Motor Testing**: Test motors at various throttle levels
- **Serial Port Configuration**: Configure MSP and other serial functions
- **ADC Monitoring**: Real-time battery voltage, current, and RSSI
- **Mobile-Friendly**: Responsive design optimized for phones and tablets
- **Auto-Connect**: Automatically finds and connects to flight controller
- **Cross-Platform**: Works on desktop Linux, Raspberry Pi, and macOS

## Requirements

**Ubuntu/Debian/Raspberry Pi:**

Modern Debian-based systems (including recent Raspberry Pi OS) use "externally-managed" Python environments to prevent breaking system packages. You have three options:

**Option 1: System Packages (Recommended for Raspberry Pi)**
```bash
sudo apt-get update
sudo apt-get install python3-flask python3-flask-socketio python3-serial python3-tk
```

**Option 2: Virtual Environment (Recommended for development)**
```bash
python3 -m venv venv
source venv/bin/activate
pip install flask flask-socketio pyserial
```

**Option 3: Override (Quick but not recommended)**
```bash
pip3 install --user --break-system-packages flask flask-socketio pyserial
```

The **install.sh script** will detect this situation and offer these choices automatically.

**macOS:**
```bash
# Install Python 3 via Homebrew if needed
brew install python3

pip3 install flask flask-socketio pyserial
```

**Fedora/RHEL:**
```bash
sudo dnf install python3 python3-pip python3-tkinter

pip3 install flask flask-socketio pyserial
```

## Installation

### 1. Install Python dependencies

```bash
cd raytools/fc_hardware_test_tools
pip3 install flask flask-socketio pyserial
```

### 2. Make scripts executable

```bash
chmod +x fc_web_tool.py show_ip_address.py
```

### 3. Install Desktop Icon (Optional - Linux Desktop Environments)

To create a desktop icon that shows your system's IP address:

```bash
# Copy desktop file to desktop
cp fc-tool-ip.desktop ~/Desktop/
chmod +x ~/Desktop/fc-tool-ip.desktop

# Or install system-wide
sudo cp fc-tool-ip.desktop /usr/share/applications/
```

**Note:** Desktop icon works on Linux desktop environments (GNOME, KDE, XFCE, etc.). Not applicable for headless servers.

### 4. Auto-Start on Boot (Optional - Linux with systemd)

To automatically start the web server when the system boots:

```bash
# Install systemd service
sudo cp fc-web-tool.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable fc-web-tool.service
sudo systemctl start fc-web-tool.service

# Check status
sudo systemctl status fc-web-tool.service
```

**Note:** Requires systemd (most modern Linux distributions). For other init systems, adapt accordingly.

## Usage

### Manual Start

```bash
cd raytools/fc_hardware_test_tools
python3 fc_web_tool.py
```

The server will start on port 5000. Access from:
- Same device: http://localhost:5000
- Other devices: http://\<server-ip-address\>:5000

### Finding the IP Address

**Linux:**
1. Click the desktop icon "FC Tool IP Address" (if installed)
2. Or run: `hostname -I`
3. Or check the web server startup message
4. Or use: `ip addr show`

**macOS:**
1. Run: `ifconfig | grep "inet " | grep -v 127.0.0.1`
2. Or check System Preferences → Network

### Using the Web Interface

1. **Connect your flight controller** via USB
2. **Open the web interface** on your phone or computer
3. The tool will automatically connect to the flight controller
4. Use the tabs to access different functions:
   - **Motors**: Test motor output (remove propellers!)
   - **Serial**: Configure serial port functions
   - **ADC**: Monitor battery and RSSI
   - **System**: View logs and reboot FC

## Safety

⚠️ **WARNING**: Motor testing will spin motors. Always remove propellers before testing!

## Troubleshooting

### Server won't start
- Check if port 5000 is already in use: `sudo lsof -i :5000`
- Try a different port by editing `fc_web_tool.py` (change port number at the end)

### Can't connect from phone/other device
- Make sure client and server are on the same network
- Check firewall: `sudo ufw allow 5000` (Linux) or allow port in firewall settings
- Verify IP address with `hostname -I` (Linux) or `ifconfig` (macOS)

### Flight controller not detected
- Check USB connection
- **Linux:** Verify device appears: `ls -la /dev/ttyACM*`
- **macOS:** Verify device appears: `ls -la /dev/cu.usbmodem*`
- **Linux permissions:** `sudo usermod -a -G dialout $USER` (then logout/login)
- **macOS permissions:** Usually not required, but ensure security settings allow USB access

### Service won't start
```bash
# View logs
sudo journalctl -u fc-web-tool.service -f

# Restart service
sudo systemctl restart fc-web-tool.service
```

## Development

To run in development mode with auto-reload:

```bash
cd raytools/fc_hardware_test_tools
FLASK_ENV=development python3 fc_web_tool.py
```

## Platform-Specific Notes

### macOS
- USB devices appear as `/dev/cu.usbmodem*` instead of `/dev/ttyACM*`
- You may need to modify `fc_web_tool.py` line 679 to search for the correct pattern:
  ```python
  ports = sorted(glob.glob('/dev/cu.usbmodem*'))
  ```

### Ubuntu Desktop / Linux Workstation
- Works identically to Raspberry Pi
- All features fully supported
- Can run on your main development machine

### Headless Servers
- Desktop icon (`show_ip_address.py`) requires a display
- All other features work fine
- Use `hostname -I` or check server logs for IP address

## Architecture

- **Backend**: Flask + Flask-SocketIO (Python)
- **Frontend**: HTML + JavaScript + WebSockets
- **Protocol**: MSP v1 and MSP v2 support
- **Communication**: Real-time bidirectional updates via Socket.IO
- **Platform**: Pure Python, no hardware-specific dependencies

## Files

- `fc_web_tool.py` - Main web server application
- `show_ip_address.py` - Desktop icon script to display IP
- `templates/index.html` - Web interface (mobile-optimized)
- `fc-tool-ip.desktop` - Desktop entry file
- `fc-web-tool.service` - Systemd service file

## Original GUI Tool

The original Tkinter GUI version is still available as `fc_gui_tool.py` if you prefer a desktop application.

## License

Part of the raytools collection for flight controller hardware testing.
