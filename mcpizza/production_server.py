#!/usr/bin/env python3
"""
MCPizza Production Server - Real Domino's API Integration

This server can use real Domino's API calls when enabled.
"""

import asyncio
import json
import sys
import logging
import os
from typing import Any, Dict, List, Optional

# Configuration
ENABLE_REAL_API = os.getenv("MCPIZZA_REAL_API", "false").lower() == "true"
FALLBACK_TO_MOCK = os.getenv("MCPIZZA_FALLBACK_MOCK", "true").lower() == "true"

# Try to import pizzapi
try:
    from pizzapi import Address, Customer, Order, Store
    PIZZAPI_AVAILABLE = True
except ImportError as e:
    PIZZAPI_AVAILABLE = False
    logging.warning(f"pizzapi not available: {e}")

class ProductionPizzaOrderManager:
    """Production pizza ordering with real API support"""
    
    def __init__(self):
        self.store = None
        self.customer = None
        self.order = None
        self.items = []
        self.use_real_api = ENABLE_REAL_API and PIZZAPI_AVAILABLE
        
        if self.use_real_api:
            logging.info("🔴 REAL API MODE ENABLED - Will make actual Domino's API calls")
        else:
            logging.info("🟡 MOCK MODE - Using demo data")
    
    def _get_mock_store_data(self, address: str) -> Dict[str, Any]:
        """Fallback mock data"""
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
        
        return zip_mock_data.get(address, {
            "store_id": "9999",
            "phone": "(555) 555-0100",
            "address": f"123 Demo St {address}",
            "is_delivery_store": True,
            "min_delivery_order_amount": 10.00,
            "delivery_minutes": "25-35",
            "pickup_minutes": "15-25"
        })
    
    def find_store(self, address_str: str) -> Dict[str, Any]:
        """Find nearest Domino's store"""
        if self.use_real_api:
            try:
                logging.info(f"🔍 Finding real store near: {address_str}")
                
                # Parse address string
                parts = address_str.split(',')
                if len(parts) >= 3:
                    # Full address: street, city, state
                    street = parts[0].strip()
                    city = parts[1].strip()
                    region = parts[2].strip()
                elif len(parts) == 2:
                    # City, state or street, city
                    street = "123 Main St"  # Default
                    city = parts[0].strip()
                    region = parts[1].strip()
                else:
                    # Assume it's a zip code or city
                    street = "123 Main St"  # Default
                    city = "Main City"      # Default
                    region = address_str.strip()
                
                # Create address object
                address = Address(street=street, city=city, region=region)
                
                # Find closest store
                store = address.closest_store()
                
                if not store:
                    if FALLBACK_TO_MOCK:
                        logging.warning("No real store found, falling back to mock data")
                        mock_data = self._get_mock_store_data(address_str)
                        return {**mock_data, "status": "success", "source": "fallback_mock"}
                    else:
                        return {"error": "No Domino's stores found near that address"}
                
                self.store = store
                
                store_info = {
                    "store_id": store.data.get("StoreID"),
                    "phone": store.data.get("Phone"),
                    "address": f"{store.data.get('StreetName', '')} {store.data.get('City', '')} {store.data.get('Region', '')}",
                    "is_delivery_store": store.data.get("IsDeliveryStore"),
                    "min_delivery_order_amount": store.data.get("MinDeliveryOrderAmount"),
                    "delivery_minutes": store.data.get("ServiceEstimatedWaitMinutes", {}).get("Delivery"),
                    "pickup_minutes": store.data.get("ServiceEstimatedWaitMinutes", {}).get("Carryout"),
                    "status": "success",
                    "source": "real_api"
                }
                
                logging.info(f"✅ Found real store: {store_info['store_id']}")
                return store_info
                
            except Exception as e:
                logging.error(f"Real API failed: {e}")
                if FALLBACK_TO_MOCK:
                    logging.info("Falling back to mock data")
                    mock_data = self._get_mock_store_data(address_str)
                    return {**mock_data, "status": "success", "source": "fallback_mock", "api_error": str(e)}
                else:
                    return {"error": f"Store lookup failed: {str(e)}"}
        else:
            # Mock mode
            mock_data = self._get_mock_store_data(address_str)
            return {**mock_data, "status": "success", "source": "mock"}
    
    def search_menu(self, query: str) -> Dict[str, Any]:
        """Search menu for items"""
        if self.use_real_api and self.store:
            try:
                logging.info(f"🔍 Searching real menu for: {query}")
                
                menu = self.store.get_menu()
                matching_items = []
                query_lower = query.lower()
                
                # Search through menu categories
                for category_name, items in menu.data.items():
                    if isinstance(items, dict) and "Products" in items:
                        for product_code, product_data in items["Products"].items():
                            if isinstance(product_data, dict):
                                name = product_data.get("Name", "").lower()
                                description = product_data.get("Description", "").lower()
                                
                                if query_lower in name or query_lower in description:
                                    matching_items.append({
                                        "category": category_name,
                                        "code": product_code,
                                        "name": product_data.get("Name", ""),
                                        "description": product_data.get("Description", ""),
                                        "price": product_data.get("Price", "")
                                    })
                
                if not matching_items:
                    return {"error": f"No items found matching '{query}'", "source": "real_api"}
                
                logging.info(f"✅ Found {len(matching_items)} real menu items")
                return {"items": matching_items, "status": "success", "source": "real_api"}
                
            except Exception as e:
                logging.error(f"Real menu search failed: {e}")
                if FALLBACK_TO_MOCK:
                    return self._get_mock_menu_items(query)
                else:
                    return {"error": f"Menu search failed: {str(e)}"}
        else:
            # Mock mode or no store
            return self._get_mock_menu_items(query)
    
    def _get_mock_menu_items(self, query: str) -> Dict[str, Any]:
        """Mock menu items"""
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
            return {"error": f"No items found matching '{query}'", "source": "mock"}
            
        return {"items": matching_items, "status": "success", "source": "mock"}
    
    def add_to_order(self, item_code: str, quantity: int = 1, options: Dict = None) -> Dict[str, Any]:
        """Add item to order"""
        if self.use_real_api and self.store:
            try:
                logging.info(f"➕ Adding {quantity}x {item_code} to real order")
                
                if not self.order:
                    self.order = Order(self.store)
                
                if options is None:
                    options = {}
                
                # Add item to real order
                for _ in range(quantity):
                    self.order.add_item(item_code, options)
                
                self.items.append({
                    "code": item_code,
                    "quantity": quantity,
                    "options": options
                })
                
                return {
                    "message": f"Added {quantity}x {item_code} to order",
                    "status": "success",
                    "source": "real_api"
                }
                
            except Exception as e:
                logging.error(f"Real add to order failed: {e}")
                if FALLBACK_TO_MOCK:
                    return self._add_to_mock_order(item_code, quantity, options)
                else:
                    return {"error": f"Failed to add item: {str(e)}"}
        else:
            # Mock mode
            return self._add_to_mock_order(item_code, quantity, options)
    
    def _add_to_mock_order(self, item_code: str, quantity: int, options: Dict = None) -> Dict[str, Any]:
        """Add to mock order"""
        if options is None:
            options = {}
            
        self.items.append({
            "code": item_code,
            "quantity": quantity,
            "options": options
        })
        
        return {
            "message": f"Added {quantity}x {item_code} to order",
            "status": "success",
            "source": "mock"
        }
    
    def view_order(self) -> Dict[str, Any]:
        """View current order"""
        if self.use_real_api and self.order:
            try:
                order_data = self.order.data
                return {
                    "items": self.items,
                    "order_data": order_data,
                    "status": "success",
                    "source": "real_api"
                }
            except Exception as e:
                logging.error(f"Real view order failed: {e}")
                # Fall back to basic item list
                pass
        
        # Mock mode or fallback
        if not self.items:
            return {"message": "No items in order yet", "source": "mock"}
            
        return {
            "items": self.items,
            "total": "$35.36",
            "status": "success",
            "source": "mock"
        }

class ProductionMCPServer:
    """Production MCP Server with real API support"""
    
    def __init__(self):
        self.pizza_manager = ProductionPizzaOrderManager()
        
    def get_server_info(self):
        """Return server capabilities"""
        return {
            "name": "mcpizza-production",
            "version": "1.0.0",
            "protocolVersion": "2024-11-05",
            "real_api_enabled": self.pizza_manager.use_real_api
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
                        },
                        "options": {
                            "type": "object",
                            "description": "Item customization options",
                            "default": {}
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
                arguments.get("quantity", 1),
                arguments.get("options", {})
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
            logging.error(f"Request handling error: {e}")
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
        logging.info(f"🍕 MCPizza Production Server starting...")
        logging.info(f"   Real API: {'✅ ENABLED' if self.pizza_manager.use_real_api else '❌ DISABLED'}")
        logging.info(f"   Fallback: {'✅ ENABLED' if FALLBACK_TO_MOCK else '❌ DISABLED'}")
        
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
                logging.error(f"Server error: {e}")
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
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr
    )
    
    server = ProductionMCPServer()
    await server.run_stdio()

if __name__ == "__main__":
    asyncio.run(main())
