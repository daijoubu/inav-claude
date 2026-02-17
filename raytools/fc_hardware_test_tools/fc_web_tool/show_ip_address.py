#!/usr/bin/env python3
"""
Desktop Icon: Display Raspberry Pi IP Address
Shows the current IP address in a desktop window for easy access to the web interface
"""

import tkinter as tk
import socket
import subprocess

def get_ip_address():
    """Get the primary IP address of this device"""
    try:
        # Create a socket to determine the primary network interface
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to an external address (doesn't actually send data)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "Not connected"

def get_all_interfaces():
    """Get all network interfaces and their IP addresses"""
    interfaces = []
    try:
        # Use hostname -I to get all IP addresses
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True, check=True)
        ips = result.stdout.strip().split()

        for ip in ips:
            if ip.startswith('169.254.'):  # Skip link-local addresses
                continue
            interfaces.append(ip)

        return interfaces
    except Exception:
        return []

def create_window():
    """Create the IP address display window"""
    root = tk.Tk()
    root.title("FC Test Tool - IP Address")
    root.geometry("450x320")
    root.configure(bg='#1a1a1a')

    # Title
    title = tk.Label(root, text="Flight Controller Test Tool",
                    font=('Arial', 16, 'bold'),
                    bg='#1a1a1a', fg='#ffffff')
    title.pack(pady=20)

    # Primary IP
    primary_ip = get_ip_address()

    ip_frame = tk.Frame(root, bg='#2a2a2a', padx=20, pady=15)
    ip_frame.pack(padx=20, pady=10, fill='x')

    ip_label = tk.Label(ip_frame, text="Connect from your device:",
                       font=('Arial', 11), bg='#2a2a2a', fg='#888888')
    ip_label.pack()

    ip_value = tk.Label(ip_frame, text=f"http://{primary_ip}:5000",
                       font=('Arial', 18, 'bold'), bg='#2a2a2a', fg='#4caf50')
    ip_value.pack(pady=5)

    # All interfaces
    all_ips = get_all_interfaces()
    if len(all_ips) > 1:
        other_frame = tk.Frame(root, bg='#2a2a2a', padx=20, pady=15)
        other_frame.pack(padx=20, pady=10, fill='x')

        other_label = tk.Label(other_frame, text="Other addresses:",
                             font=('Arial', 10), bg='#2a2a2a', fg='#888888')
        other_label.pack()

        for ip in all_ips:
            if ip != primary_ip:
                other_ip = tk.Label(other_frame, text=f"http://{ip}:5000",
                                  font=('Arial', 11), bg='#2a2a2a', fg='#888888')
                other_ip.pack()

    # Instructions
    instructions = tk.Label(root,
                          text="Open this address in a web browser\non your phone or computer",
                          font=('Arial', 10), bg='#1a1a1a', fg='#888888',
                          justify='center')
    instructions.pack(pady=15)

    # Close button
    close_btn = tk.Button(root, text="Close", command=root.destroy,
                         bg='#0066cc', fg='white', font=('Arial', 12, 'bold'),
                         padx=20, pady=10, relief='flat', cursor='hand2')
    close_btn.pack(pady=10)

    # Keep window on top
    root.attributes('-topmost', True)

    root.mainloop()

if __name__ == "__main__":
    create_window()
