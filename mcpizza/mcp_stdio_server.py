#!/usr/bin/env python3
"""
MCPizza - Domino's Pizza Ordering MCP Server with stdio transport

A proper MCP server implementation using JSON-RPC over stdio transport.
"""

import asyncio
import json
import sys
import logging
from typing import Any, Dict, List, Optional

# Mock pizza ordering for reliable demonstration
class MockPizzaOrderManager:
    """Mock pizza ordering for demonstration"""
    
    def __init__(self):
        self.store = None
        self.customer = None
        self.order = None
        self.items = []
        
    def find_store(self, address: str) -> Dict[str, Any]:
        """Mock store finding with location-aware data"""
        # Mock data based on zip codes
        zip_mock_data = {
            '95608': {
                "store_id": "4521",
                "phone": "(916) 555-0199", 
                "address": "1234 Main St Carmichael, CA",
                "is_delivery_store": True,
                "min_delivery_order_amount": 10.00,
                "delivery_minutes": "20-30",
                "pickup_minutes": "10-20"
            },
            '10001': {
                "store_id": "3681",
                "phone": "(212) 555-0123",
                "address": "123 Broadway New York, NY", 
                "is_delivery_store": True,
                "min_delivery_order_amount": 10.00,
                "delivery_minutes": "25-35",
                "pickup_minutes": "15-25"
            },
            '90210': {
                "store_id": "2105",
                "phone": "(310) 555-0156",
                "address": "456 Rodeo Dr Beverly Hills, CA",
                "is_delivery_store": True,
                "min_delivery_order_amount": 15.00,
                "delivery_minutes": "30-40", 
                "pickup_minutes": "15-25"
            }
        }
        
        # Get mock data for this zip or create generic one
        self.store = zip_mock_data.get(address, {
            "store_id": "9999",
            "phone": "(555) 555-0100",
            "address": f"123 Demo St {address}",
            "is_delivery_store": True,
            "min_delivery_order_amount": 10.00,
            "delivery_minutes": "25-35",
            "pickup_minutes": "15-25"
        })
        
        return {
            **self.store, 
            "status": "success",
            "note": "⚠️ Mock demo data - real server would use actual Domino's API"
        }
    
    def search_menu(self, query: str) -> Dict[str, Any]:
        """Mock menu search"""
        mock_items = {
            "pizza": [
                {
                    "category": "Pizza",
                    "code": "S_PIZZA",
                    "name": "Medium Hand Tossed Pizza",
                    "description": "Medium pizza with classic hand tossed crust",
                    "price": "$15.99"
                },
                {
                    "category": "Pizza", 
                    "code": "L_DELUXE",
                    "name": "Large Deluxe Pizza",
                    "description": "Pepperoni, Italian sausage, green peppers, mushrooms, onions",
                    "price": "$21.99"
                },
                {
                    "category": "Pizza",
                    "code": "M_PEPPERONI", 
                    "name": "Medium Pepperoni Pizza",
                    "description": "Classic pepperoni pizza",
                    "price": "$17.99"
                }
            ],
            "wings": [
                {
                    "category": "Wings",
                    "code": "HOT_WINGS",
                    "name": "Hot Buffalo Wings",
                    "description": "Spicy buffalo wings with celery",
                    "price": "$9.99"
                }
            ]
        }
        
        query_lower = query.lower()
        matching_items = []
        
        for category, items in mock_items.items():
            if query_lower in category or any(query_lower in item["name"].lower() for item in items):
                matching_items.extend(items)
        
        if not matching_items:
            return {"error": f"No items found matching '{query}'"}
            
        return {"items": matching_items, "status": "success"}
    
    def add_to_order(self, item_code: str, quantity: int = 1) -> Dict[str, Any]:
        """Mock adding to order"""
        self.items.append({
            "code": item_code,
            "quantity": quantity
        })
        
        return {
            "message": f"Added {quantity}x {item_code} to order",
            "status": "success"
        }
    
    def view_order(self) -> Dict[str, Any]:
        """Mock order viewing"""
        if not self.items:
            return {"message": "No items in order yet"}
            
        return {
            "items": self.items,
            "total": "$35.36",
            "status": "success"
        }

class MCPizzaJSONRPCServer:
    """JSON-RPC MCP Server for pizza ordering"""
    
    def __init__(self):
        self.pizza_manager = MockPizzaOrderManager()
        self.request_id = 0
        
    def get_server_info(self):
        """Return server capabilities"""
        return {
            "name": "mcpizza",
            "version": "0.1.0",
            "protocolVersion": "2024-11-05"
        }
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """Return available tools"""
        return [
            {
                "name": "find_dominos_store",
                "description": "Find the nearest Domino's store by address or zip code",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "address": {
                            "type": "string",
                            "description": "Full address or zip code to search near"
                        }
                    },
                    "required": ["address"]
                }
            },
            {
                "name": "search_menu",
                "description": "Search for specific items in the store menu",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search term (e.g., 'pepperoni pizza', 'wings', 'pasta')"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "add_to_order",
                "description": "Add items to the pizza order",
                "inputSchema": {
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
                        }
                    },
                    "required": ["item_code"]
                }
            },
            {
                "name": "view_order",
                "description": "View current order contents and total",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool calls"""
        
        if name == "find_dominos_store":
            result = self.pizza_manager.find_store(arguments["address"])
            
        elif name == "search_menu":
            result = self.pizza_manager.search_menu(arguments["query"])
            
        elif name == "add_to_order":
            result = self.pizza_manager.add_to_order(
                arguments["item_code"],
                arguments.get("quantity", 1)
            )
            
        elif name == "view_order":
            result = self.pizza_manager.view_order()
            
        else:
            return {
                "isError": True,
                "content": [{
                    "type": "text",
                    "text": f"Unknown tool: {name}"
                }]
            }
        
        # Format as MCP response
        return {
            "content": [{
                "type": "text", 
                "text": json.dumps(result, indent=2)
            }]
        }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle JSON-RPC request"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": self.get_server_info()
                    }
                }
                
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": self.list_tools()
                    }
                }
                
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                result = self.call_tool(tool_name, arguments)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
                
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
                
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def run_stdio(self):
        """Run server with stdio transport"""
        while True:
            try:
                # Read JSON-RPC request from stdin
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                    
                line = line.strip()
                if not line:
                    continue
                
                request = json.loads(line)
                response = await self.handle_request(request)
                
                # Write JSON-RPC response to stdout
                print(json.dumps(response), flush=True)
                
            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)
                
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0", 
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)

async def main():
    """Main entry point"""
    # Configure logging to stderr so it doesn't interfere with JSON-RPC on stdout
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr
    )
    
    server = MCPizzaJSONRPCServer()
    logging.info("🍕 MCPizza server starting...")
    await server.run_stdio()

if __name__ == "__main__":
    asyncio.run(main())
