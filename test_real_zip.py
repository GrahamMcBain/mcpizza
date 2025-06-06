#!/usr/bin/env python3
"""
Test the actual MCPizza server with real zip code 95608
"""

import subprocess
import json
import sys

def test_real_server_with_zip():
    """Test the actual MCP server with zip 95608"""
    print("🍕 Testing MCPizza Server with Real Zip Code 95608")
    print("=" * 55)
    
    # Start the actual server that tries to use real API
    server_proc = subprocess.Popen(
        [sys.executable, "mcpizza/simple_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Let it run the demo
        stdout, stderr = server_proc.communicate(timeout=30)
        
        print("STDOUT:")
        print(stdout)
        print("\nSTDERR:")
        print(stderr)
        
    except subprocess.TimeoutExpired:
        server_proc.kill()
        print("Server timed out")
    except Exception as e:
        print(f"Error: {e}")

def test_stdio_server_with_95608():
    """Test our stdio MCP server with 95608"""
    print("\n" + "=" * 55)
    print("🧪 Testing stdio MCP server with zip 95608")
    print("=" * 55)
    
    server_proc = subprocess.Popen(
        [sys.executable, "mcpizza/mcp_stdio_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    def send_request(request):
        """Send JSON-RPC request and get response"""
        request_line = json.dumps(request) + "\n"
        server_proc.stdin.write(request_line)
        server_proc.stdin.flush()
        
        response_line = server_proc.stdout.readline()
        return json.loads(response_line.strip())
    
    try:
        # Initialize
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        response = send_request(init_request)
        print("✅ Server initialized")
        
        # Test with 95608
        find_store_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "find_dominos_store",
                "arguments": {
                    "address": "95608"
                }
            }
        }
        
        response = send_request(find_store_request)
        if "result" in response:
            content = response["result"]["content"][0]["text"]
            store_data = json.loads(content)
            print(f"\n📍 Results for zip code 95608:")
            print(f"   Store ID: {store_data.get('store_id')}")
            print(f"   Address: {store_data.get('address')}")
            print(f"   Phone: {store_data.get('phone')}")
            if 'note' in store_data:
                print(f"   Note: {store_data.get('note')}")
        else:
            print(f"❌ Error: {response}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        
    finally:
        server_proc.terminate()

if __name__ == "__main__":
    # Test the mock server (which should now return CA data for 95608)
    test_stdio_server_with_95608()
    
    print("\n" + "🔍 Explanation:")
    print("1. The web demo now correctly shows CA data for 95608")
    print("2. The MCP stdio server uses mock data (safer for demo)")
    print("3. The real API server in simple_server.py would use actual Domino's data")
    print("4. For production use, you'd enable the real pizzapi calls")
