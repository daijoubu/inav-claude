#!/bin/bash
# Installation script for FC Web Test Tool

echo "======================================"
echo "FC Web Test Tool Installation"
echo "======================================"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if running on Pi
if [[ ! -f /proc/device-tree/model ]] || ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
echo ""

# Try to install with pip first
if pip3 install --user flask flask-socketio pyserial 2>&1 | grep -q "externally-managed-environment"; then
    echo "⚠️  Externally-managed Python environment detected (Debian/Ubuntu policy)"
    echo ""
    echo "Choose installation method:"
    echo "  1) Use system packages (apt) - Recommended for Pi"
    echo "  2) Create virtual environment - Recommended for development"
    echo "  3) Override with --break-system-packages - Quick but not recommended"
    echo ""
    read -p "Enter choice (1-3): " -n 1 -r
    echo
    echo ""

    case $REPLY in
        1)
            echo "📦 Installing via apt (system packages)..."
            sudo apt-get update
            sudo apt-get install -y python3-flask python3-flask-socketio python3-serial python3-pip
            echo "✅ System packages installed!"
            INSTALL_METHOD="system"
            ;;
        2)
            echo "📦 Creating virtual environment..."
            python3 -m venv venv
            source venv/bin/activate
            pip install flask flask-socketio pyserial
            echo "✅ Virtual environment created at: $SCRIPT_DIR/venv"
            echo ""
            echo "⚠️  IMPORTANT: To use the tool, activate the venv first:"
            echo "   source $SCRIPT_DIR/venv/bin/activate"
            echo "   python3 fc_web_tool.py"
            INSTALL_METHOD="venv"
            ;;
        3)
            echo "📦 Installing with --break-system-packages..."
            pip3 install --user --break-system-packages flask flask-socketio pyserial
            echo "✅ Packages installed (system override)"
            INSTALL_METHOD="user"
            ;;
        *)
            echo "❌ Invalid choice. Please run the script again."
            exit 1
            ;;
    esac
else
    echo "✅ Python packages installed successfully!"
    INSTALL_METHOD="user"
fi

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x fc_web_tool.py show_ip_address.py

echo ""
echo "✅ Basic installation complete!"
echo ""

# Ask about optional installations
echo "Optional installations:"
echo ""

# Desktop icon
read -p "Install desktop icon to show IP address? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📌 Installing desktop icon..."
    mkdir -p ~/Desktop
    cp fc-tool-ip.desktop ~/Desktop/
    chmod +x ~/Desktop/fc-tool-ip.desktop
    echo "   Desktop icon created!"
fi

echo ""

# Auto-start service
if [[ "$INSTALL_METHOD" == "venv" ]]; then
    echo "⚠️  Auto-start service not compatible with virtual environment"
    echo "   To run on boot with venv, create a wrapper script or use system packages instead."
    echo "   For now, start manually: source venv/bin/activate && python3 fc_web_tool.py"
else
    read -p "Install auto-start service (requires sudo)? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🚀 Installing systemd service..."

        # Update service file paths to match actual location
        sed "s|/home/raymorris/Documents/planes/inavflight/raytools/fc_hardware_test_tools|$SCRIPT_DIR|g" \
            fc-web-tool.service > /tmp/fc-web-tool.service

        sudo cp /tmp/fc-web-tool.service /etc/systemd/system/
        sudo systemctl daemon-reload
        sudo systemctl enable fc-web-tool.service

        read -p "   Start service now? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            sudo systemctl start fc-web-tool.service
            echo "   Service started!"
            sleep 1
            sudo systemctl status fc-web-tool.service --no-pager
        else
            echo "   Service enabled but not started. Start with:"
            echo "   sudo systemctl start fc-web-tool.service"
        fi
    fi
fi

echo ""

# Check for serial port permissions
if ! groups | grep -q dialout; then
    echo "⚠️  User not in 'dialout' group (needed for serial access)"
    read -p "Add user to dialout group? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo usermod -a -G dialout $USER
        echo "   Added to dialout group. You need to logout and login again!"
    fi
fi

echo ""
echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo ""
echo "To start manually:"
echo "  python3 $SCRIPT_DIR/fc_web_tool.py"
echo ""
echo "To view IP address:"
echo "  python3 $SCRIPT_DIR/show_ip_address.py"
echo ""
echo "Or click the desktop icon!"
echo ""
