#!/usr/bin/env python3
"""
Simple HTTP server for testing WASM

Serves files with proper CORS and COOP/COEP headers required for WASM.
"""

import http.server
import socketserver
import os

PORT = 8888

class WasmHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Required for SharedArrayBuffer and WASM threads
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
        self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

    def log_message(self, format, *args):
        # Add timestamp to log
        print(f"[{self.log_date_time_string()}] {format % args}")

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    print(f"\n🌐 Starting WASM test server on http://localhost:{PORT}")
    print(f"📁 Serving from: {os.getcwd()}")
    print(f"\n📋 Open: http://localhost:{PORT}/test_serial_available.html")
    print(f"\n💡 Press Ctrl+C to stop\n")

    with socketserver.TCPServer(("", PORT), WasmHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Server stopped")
