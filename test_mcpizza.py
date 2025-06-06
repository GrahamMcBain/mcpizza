#!/usr/bin/env python3
"""
Test script for MCPizza server

This script tests the MCP server functionality without placing real orders.
"""

import asyncio
import json
from mcpizza.server import create_server
from mcp.types import CallToolRequest, CallToolRequestParams

async def test_find_store():
    """Test finding a store"""
    server = create_server()
    
    request = CallToolRequest(
        params=CallToolRequestParams(
            name="find_dominos_store",
            arguments={"address": "10001"}  # NYC zip code
        )
    )
    
    result = await server.call_tool(request)
    print("Find Store Result:")
    print(result.content[0].text)
    print("-" * 50)

async def test_search_menu():
    """Test searching menu after finding store"""
    server = create_server()
    
    # First find a store
    find_request = CallToolRequest(
        params=CallToolRequestParams(
            name="find_dominos_store", 
            arguments={"address": "10001"}
        )
    )
    await server.call_tool(find_request)
    
    # Then search menu
    search_request = CallToolRequest(
        params=CallToolRequestParams(
            name="search_menu",
            arguments={"query": "pizza", "store_id": "dummy"}
        )
    )
    
    result = await server.call_tool(search_request)
    print("Menu Search Result:")
    print(result.content[0].text)
    print("-" * 50)

async def test_view_order():
    """Test viewing empty order"""
    server = create_server()
    
    request = CallToolRequest(
        params=CallToolRequestParams(
            name="view_order",
            arguments={}
        )
    )
    
    result = await server.call_tool(request)
    print("View Order Result:")
    print(result.content[0].text)
    print("-" * 50)

async def main():
    """Run all tests"""
    print("Testing MCPizza Server")
    print("=" * 50)
    
    try:
        await test_find_store()
        await test_search_menu() 
        await test_view_order()
        print("✅ All tests completed")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
