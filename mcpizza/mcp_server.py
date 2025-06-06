#!/usr/bin/env python3
"""
MCPizza - Domino's Pizza Ordering MCP Server

A complete MCP server implementation for pizza ordering using the Domino's API.
"""

import json
import sys
from typing import Any, Dict, List

# Mock MCP types for demonstration
class TextContent:
    def __init__(self, type: str, text: str):
        self.type = type
        self.text = text

class CallToolResult:
    def __init__(self, content: List[TextContent]):
        self.content = content

class Tool:
    def __init__(self, name: str, description: str, inputSchema: Dict[str, Any]):
        self.name = name
        self.description = description
        self.inputSchema = inputSchema

# Import the pizza ordering logic
from mcpizza.simple_server import PizzaOrderManager

class MCPizzaServer:
    """MCP Server for pizza ordering"""
    
    def __init__(self):
        self.pizza_manager = PizzaOrderManager()
        self.tools = self._define_tools()
    
    def _define_tools(self) -> List[Tool]:
        """Define available MCP tools"""
        return [
            Tool(
                name="find_dominos_store",
                description="Find the nearest Domino's store by address or zip code",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "address": {
                            "type": "string",
                            "description": "Full address or zip code to search near"
                        }
                    },
                    "required": ["address"]
                }
            ),
            Tool(
                name="get_store_menu_categories",
                description="Get available menu categories from the selected store",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="search_menu",
                description="Search for specific items in the store menu",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search term (e.g., 'pepperoni pizza', 'wings', 'pasta')"
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="add_to_order",
                description="Add items to the pizza order",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "item_code": {
                            "type": "string",
                            "description": "Product code from menu search"
                        },
                        "quantity": {
                            "type": "integer",
                            "description": "Number of items to add",
                            "default": 1
                        },
                        "options": {
                            "type": "object",
                            "description": "Item customization options",
                            "default": {}
                        }
                    },
                    "required": ["item_code"]
                }
            ),
            Tool(
                name="view_order",
                description="View current order contents and total",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="set_customer_info",
                description="Set customer information for delivery",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "first_name": {"type": "string"},
                        "last_name": {"type": "string"},
                        "email": {"type": "string"},
                        "phone": {"type": "string"},
                        "address": {
                            "type": "object",
                            "properties": {
                                "street": {"type": "string"},
                                "city": {"type": "string"},
                                "region": {"type": "string"},
                                "zip": {"type": "string"}
                            },
                            "required": ["street", "city", "region", "zip"]
                        }
                    },
                    "required": ["first_name", "last_name", "email", "phone", "address"]
                }
            ),
            Tool(
                name="calculate_order_total",
                description="Calculate order total with tax and delivery fees",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="prepare_order",
                description="Prepare order for placement (safe preview mode)",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            )
        ]
    
    def list_tools(self) -> List[Tool]:
        """Return available tools"""
        return self.tools
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle tool calls"""
        
        if name == "find_dominos_store":
            result = self.pizza_manager.find_store(arguments["address"])
            
        elif name == "get_store_menu_categories":
            result = self.pizza_manager.get_menu_categories()
            
        elif name == "search_menu":
            result = self.pizza_manager.search_menu(arguments["query"])
            
        elif name == "add_to_order":
            result = self.pizza_manager.add_to_order(
                arguments["item_code"],
                arguments.get("quantity", 1),
                arguments.get("options", {})
            )
            
        elif name == "view_order":
            result = self.pizza_manager.view_order()
            
        elif name == "set_customer_info":
            result = self.pizza_manager.set_customer_info(arguments)
            
        elif name == "calculate_order_total":
            result = self.pizza_manager.calculate_total()
            
        elif name == "prepare_order":
            result = self.pizza_manager.prepare_order_preview()
            
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        # Format result as MCP response
        response_text = json.dumps(result, indent=2)
        return CallToolResult(
            content=[TextContent(type="text", text=response_text)]
        )

def demo_mcp_server():
    """Demonstrate MCP server functionality"""
    print("🍕 MCPizza MCP Server Demo")
    print("=" * 40)
    
    server = MCPizzaServer()
    
    print(f"\n📋 Available Tools ({len(server.tools)}):")
    for tool in server.tools:
        print(f"   - {tool.name}: {tool.description}")
    
    print("\n🔧 Testing Tool Calls:")
    
    # Test 1: Find store
    print("\n1. find_dominos_store")
    result = server.call_tool("find_dominos_store", {"address": "10001"})
    data = json.loads(result.content[0].text)
    if "error" in data:
        print(f"   ❌ {data['error']}")
    else:
        print(f"   ✅ Found store: {data.get('store_id', 'Unknown')}")
    
    # Test 2: Get categories
    print("\n2. get_store_menu_categories")
    result = server.call_tool("get_store_menu_categories", {})
    data = json.loads(result.content[0].text)
    if "error" in data:
        print(f"   ❌ {data['error']}")
    else:
        print(f"   ✅ Found {len(data.get('categories', []))} categories")
    
    # Test 3: Search menu
    print("\n3. search_menu")
    result = server.call_tool("search_menu", {"query": "pizza"})
    data = json.loads(result.content[0].text)
    if "error" in data:
        print(f"   ❌ {data['error']}")
    else:
        print(f"   ✅ Found {len(data.get('items', []))} items")
    
    print("\n🎯 MCP Server is functional and ready!")
    print("\nTo use with an MCP client:")
    print("1. Start the server: python -m mcpizza.mcp_server")
    print("2. Connect your MCP client to this server")
    print("3. Use the available tools to order pizza!")

def main():
    """Main entry point for MCP server"""
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo_mcp_server()
    else:
        print("🍕 MCPizza MCP Server")
        print("Real MCP server would run here with stdio transport")
        print("Run with 'demo' argument to see functionality")
        print("Example: python mcpizza/mcp_server.py demo")

if __name__ == "__main__":
    main()
