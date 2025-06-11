#!/usr/bin/env python3
"""
Simple SSE endpoint for MCP
"""

import json
import os
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Send SSE headers immediately
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Send immediate data
            connection_msg = json.dumps({"type": "connection", "status": "connected"})
            self.wfile.write(f"data: {connection_msg}\n\n".encode())
            self.wfile.flush()
            
            # Send server info
            server_info = json.dumps({
                "name": "MCPizza",
                "version": "1.0.0",
                "description": "Domino's Pizza MCP Server",
                "status": "ready"
            })
            self.wfile.write(f"data: {server_info}\n\n".encode())
            self.wfile.flush()
            
        except Exception as e:
            # If SSE fails, send error as regular response
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            request_data = json.loads(body)
            
            # Simple echo response for testing
            response = {
                "jsonrpc": "2.0",
                "id": request_data.get("id"),
                "result": {
                    "message": "MCPizza server received request",
                    "method": request_data.get("method", "unknown"),
                    "server": "running"
                }
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
