#!/usr/bin/env python3
"""
Test script for production MCPizza server
"""

import subprocess
import json
import sys
import os

def test_production_server(use_real_api=False, test_zip="95608"):
    """Test the production server"""
    
    # Set environment variables
    env = os.environ.copy()
    env["MCPIZZA_REAL_API"] = "true" if use_real_api else "false"
    env["MCPIZZA_FALLBACK_MOCK"] = "true"
    
    print(f"🍕 Testing MCPizza Production Server")
    print(f"   Mode: {'🔴 REAL API' if use_real_api else '🟡 MOCK'}")
    print(f"   Test Zip: {test_zip}")
    print("=" * 50)
    
    # Start the server
    server_proc = subprocess.Popen(
        [sys.executable, "mcpizza/production_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
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
            server_info = response["result"]["serverInfo"]
            print(f"✅ Server initialized: {server_info['name']} v{server_info['version']}")
            print(f"   Real API: {server_info.get('real_api_enabled', False)}")
        else:
            print(f"❌ Init failed: {response}")
            return
        
        # Test 2: Find store with user's zip
        print(f"\n2. Testing find_dominos_store with {test_zip}...")
        find_store_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "find_dominos_store",
                "arguments": {
                    "address": test_zip
                }
            }
        }
        
        response = send_request(find_store_request)
        if "result" in response:
            content = response["result"]["content"][0]["text"]
            store_data = json.loads(content)
            print(f"✅ Found store:")
            print(f"   Store ID: {store_data.get('store_id')}")
            print(f"   Address: {store_data.get('address')}")
            print(f"   Phone: {store_data.get('phone')}")
            print(f"   Source: {store_data.get('source', 'unknown')}")
            if 'api_error' in store_data:
                print(f"   API Error: {store_data['api_error']}")
        else:
            print(f"❌ Find store failed: {response}")
        
        # Test 3: Search menu
        print("\n3. Testing search_menu...")
        search_request = {
            "jsonrpc": "2.0",
            "id": 3,
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
                print(f"   Source: {menu_data.get('source', 'unknown')}")
                for item in menu_data["items"][:2]:  # Show first 2
                    print(f"   - {item['name']} ({item['code']}) - {item['price']}")
            else:
                print(f"❌ No items found: {menu_data}")
        else:
            print(f"❌ Menu search failed: {response}")
        
        print(f"\n🎯 Test completed!")
        print(f"   {'Real API calls made' if use_real_api else 'Mock data used'}")
        
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
    import argparse
    
    parser = argparse.ArgumentParser(description='Test MCPizza Production Server')
    parser.add_argument('--real-api', action='store_true', help='Use real Domino\'s API')
    parser.add_argument('--zip', default='95608', help='Zip code to test with')
    
    args = parser.parse_args()
    
    if args.real_api:
        print("⚠️  REAL API MODE - This will make actual calls to Domino's API")
        confirm = input("Continue? (y/N): ")
        if confirm.lower() != 'y':
            print("Cancelled.")
            sys.exit(0)
    
    test_production_server(use_real_api=args.real_api, test_zip=args.zip)
