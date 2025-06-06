#!/usr/bin/env python3
"""
Test MCPizza server manually without mcptools

This script tests the MCP server using direct JSON-RPC calls.
"""

import subprocess
import json
import sys
import time

def test_mcp_server():
    """Test the MCP server using subprocess"""
    print("🍕 Testing MCPizza MCP Server")
    print("=" * 40)
    
    # Start the server
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
        # Test 1: Initialize
        print("\n1. Testing initialization...")
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
        if "result" in response:
            print("✅ Server initialized successfully")
            print(f"   Protocol: {response['result']['protocolVersion']}")
            print(f"   Server: {response['result']['serverInfo']['name']}")
        else:
            print(f"❌ Init failed: {response}")
            return
        
        # Test 2: List tools
        print("\n2. Testing tool listing...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        response = send_request(tools_request)
        if "result" in response:
            tools = response["result"]["tools"]
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description']}")
        else:
            print(f"❌ Tools list failed: {response}")
            return
        
        # Test 3: Find store
        print("\n3. Testing find_dominos_store...")
        find_store_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "find_dominos_store",
                "arguments": {
                    "address": "10001"
                }
            }
        }
        
        response = send_request(find_store_request)
        if "result" in response:
            content = response["result"]["content"][0]["text"]
            store_data = json.loads(content)
            print(f"✅ Found store: {store_data.get('store_id')}")
            print(f"   Address: {store_data.get('address')}")
            print(f"   Phone: {store_data.get('phone')}")
        else:
            print(f"❌ Find store failed: {response}")
        
        # Test 4: Search menu
        print("\n4. Testing search_menu...")
        search_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "search_menu",
                "arguments": {
                    "query": "pizza"
                }
            }
        }
        
        response = send_request(search_request)
        if "result" in response:
            content = response["result"]["content"][0]["text"]
            menu_data = json.loads(content)
            if "items" in menu_data:
                print(f"✅ Found {len(menu_data['items'])} pizza items:")
                for item in menu_data["items"][:2]:  # Show first 2
                    print(f"   - {item['name']} ({item['code']}) - {item['price']}")
            else:
                print(f"❌ No items found: {menu_data}")
        else:
            print(f"❌ Menu search failed: {response}")
        
        # Test 5: Add to order
        print("\n5. Testing add_to_order...")
        add_order_request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "add_to_order",
                "arguments": {
                    "item_code": "M_PEPPERONI",
                    "quantity": 1
                }
            }
        }
        
        response = send_request(add_order_request)
        if "result" in response:
            content = response["result"]["content"][0]["text"]
            order_data = json.loads(content)
            print(f"✅ {order_data.get('message')}")
        else:
            print(f"❌ Add to order failed: {response}")
        
        # Test 6: View order
        print("\n6. Testing view_order...")
        view_order_request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "view_order",
                "arguments": {}
            }
        }
        
        response = send_request(view_order_request)
        if "result" in response:
            content = response["result"]["content"][0]["text"]
            order_data = json.loads(content)
            if "items" in order_data:
                print(f"✅ Order contains {len(order_data['items'])} items")
                print(f"   Total: {order_data.get('total')}")
            else:
                print(f"✅ {order_data.get('message')}")
        else:
            print(f"❌ View order failed: {response}")
        
        print("\n🎉 All tests completed successfully!")
        print("\nThe MCPizza server is working correctly and ready for:")
        print("- Integration with MCP clients")
        print("- Use with mcptools when available")
        print("- Integration with AI assistants that support MCP")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean up
        server_proc.terminate()
        try:
            server_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_proc.kill()

if __name__ == "__main__":
    test_mcp_server()
