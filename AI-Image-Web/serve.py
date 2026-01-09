#!/usr/bin/env python3
"""
Simple static server for the project folder.
Run: python serve.py 5500
Then open http://localhost:5500/index.html
"""
import http.server
import socketserver
import sys

PORT = 5500
if len(sys.argv) > 1:
    try:
        PORT = int(sys.argv[1])
    except Exception:
        pass

Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving HTTP on 0.0.0.0 port {PORT} (http://localhost:{PORT}/) ...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down')
        httpd.server_close()
