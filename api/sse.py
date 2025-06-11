#!/usr/bin/env python3
"""
MCPizza SSE Endpoint for Amp MCP Client
Server-Sent Events interface for MCP protocol
"""

import json
import os
import logging
import asyncio
from http.server import BaseHTTPRequestHandler
import urllib.parse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcpizza-sse")

try:
    from pizzapi import *
    from pizzapi import PaymentObject
    PIZZAPI_AVAILABLE = True
except ImportError:
    logger.warning("pizzapi not available, using mock mode")
    PIZZAPI_AVAILABLE = False

# Import our MCP handlers from the main API
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Global order state
pizza_order_state = {
    "store": None,
    "customer": None, 
    "order": None,
    "items": []
}

def get_mock_store_data():
    """Mock store data for fallback"""
    return {
        "store_id": "4521",
        "phone": "(555) 123-PIZZA",
        "address": "123 Mock St, Demo City",
        "is_delivery_store": True,
        "min_delivery_order_amount": 10.00,
        "delivery_minutes": "25-35",
        "pickup_minutes": "15-25",
        "source": "mock"
    }

def get_mock_menu_items(query=""):
    """Mock menu items for fallback"""
    items = [
        {
            "category": "Pizza",
            "code": "12SCREEN",
            "name": "Large Pepperoni Pizza", 
            "description": "Large pizza with pepperoni",
            "price": "$12.99",
            "source": "mock"
        },
        {
            "category": "Pizza",
            "code": "14SCREEN", 
            "name": "X-Large Cheese Pizza",
            "description": "Extra large cheese pizza",
            "price": "$15.99",
            "source": "mock"
        },
        {
            "category": "Wings",
            "code": "W08PHOTR",
            "name": "Hot Traditional Wings",
            "description": "8 piece traditional wings", 
            "price": "$8.99",
            "source": "mock"
        }
    ]
    
    if query:
        query = query.lower()
        items = [item for item in items if query in item["name"].lower() or query in item["description"].lower()]
    
    return items

def find_dominos_store(address: str):
    """Find nearest Domino's store"""
    use_real_api = os.getenv("MCPIZZA_REAL_API", "false").lower() == "true"
    use_fallback = os.getenv("MCPIZZA_FALLBACK_MOCK", "true").lower() == "true"
    
    if use_real_api and PIZZAPI_AVAILABLE:
        try:
            logger.info(f"🔍 Finding real store near: {address}")
            store = StoreLocator.find_closest_store_to_customer(address)
            
            if store:
                pizza_order_state["store"] = store
                return {
                    "store_id": store.data.get("StoreID"),
                    "phone": store.data.get("Phone"),
                    "address": f"{store.data.get('StreetName', '')} {store.data.get('City', '')}",
                    "is_delivery_store": store.data.get("IsDeliveryStore"),
                    "min_delivery_order_amount": store.data.get("MinDeliveryOrderAmount"),
                    "delivery_minutes": store.data.get("ServiceEstimatedWaitMinutes", {}).get("Delivery"),
                    "pickup_minutes": store.data.get("ServiceEstimatedWaitMinutes", {}).get("Carryout"),
                    "source": "real_api"
                }
        except Exception as e:
            logger.error(f"Real API failed: {e}")
            if not use_fallback:
                raise
    
    # Use mock data
    logger.info("🟡 Using mock store data")
    return get_mock_store_data()

def search_menu(query: str, store_id: str = None):
    """Search menu items"""
    use_real_api = os.getenv("MCPIZZA_REAL_API", "false").lower() == "true"
    use_fallback = os.getenv("MCPIZZA_FALLBACK_MOCK", "true").lower() == "true"
    
    if use_real_api and PIZZAPI_AVAILABLE and pizza_order_state.get("store"):
        try:
            logger.info(f"🔍 Searching real menu for: {query}")
            menu = pizza_order_state["store"].get_menu()
            
            matching_items = []
            for category_name, items in menu.data.items():
                if isinstance(items, dict) and "Products" in items:
                    for product_code, product_data in items["Products"].items():
                        if isinstance(product_data, dict):
                            name = product_data.get("Name", "").lower()
                            description = product_data.get("Description", "").lower()
                            
                            if query.lower() in name or query.lower() in description:
                                matching_items.append({
                                    "category": category_name,
                                    "code": product_code,
                                    "name": product_data.get("Name", ""),
                                    "description": product_data.get("Description", ""),
                                    "price": product_data.get("Price", ""),
                                    "source": "real_api"
                                })
            
            if matching_items:
                return matching_items
        except Exception as e:
            logger.error(f"Real menu search failed: {e}")
            if not use_fallback:
                raise
    
    # Use mock data
    logger.info(f"🟡 Using mock menu data for query: {query}")
    return get_mock_menu_items(query)

def add_to_order(item_code: str, quantity: int = 1):
    """Add item to order"""
    pizza_order_state["items"].append({
        "code": item_code,
        "quantity": quantity,
        "timestamp": "mock"
    })
    return f"Added {quantity}x {item_code} to order"

def view_order():
    """View current order"""
    return {
        "items": pizza_order_state["items"],
        "item_count": len(pizza_order_state["items"]),
        "note": "Order state resets between API calls in serverless mode"
    }

def handle_mcp_request(message):
    """Handle MCP protocol messages"""
    try:
        method = message.get("method")
        params = message.get("params", {})
        
        if method == "initialize":
            return {
                "result": {
                    "protocolVersion": "1.0.0",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "MCPizza",
                        "version": "1.0.0"
                    }
                }
            }
        
        elif method == "tools/list":
            return {
                "result": {
                    "tools": [
                        {
                            "name": "find_dominos_store",
                            "description": "Find the nearest Domino's store by address or zip code",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "address": {"type": "string", "description": "Full address or zip code"}
                                },
                                "required": ["address"]
                            }
                        },
                        {
                            "name": "search_menu",
                            "description": "Search for menu items by name or description", 
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string", "description": "Search term (e.g., 'pepperoni pizza', 'wings')"},
                                    "store_id": {"type": "string", "description": "Optional store ID"}
                                },
                                "required": ["query"]
                            }
                        },
                        {
                            "name": "add_to_order",
                            "description": "Add items to pizza order",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "item_code": {"type": "string", "description": "Product code from menu search"},
                                    "quantity": {"type": "integer", "description": "Number of items", "default": 1}
                                },
                                "required": ["item_code"]
                            }
                        },
                        {
                            "name": "view_order",
                            "description": "View current order contents",
                            "inputSchema": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }
                        }
                    ]
                }
            }
        
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            
            if tool_name == "find_dominos_store":
                result = find_dominos_store(tool_args["address"])
                return {
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    }
                }
            
            elif tool_name == "search_menu":
                result = search_menu(tool_args["query"], tool_args.get("store_id"))
                return {
                    "result": {
                        "content": [
                            {
                                "type": "text", 
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    }
                }
            
            elif tool_name == "add_to_order":
                result = add_to_order(tool_args["item_code"], tool_args.get("quantity", 1))
                return {
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": result
                            }
                        ]
                    }
                }
            
            elif tool_name == "view_order":
                result = view_order()
                return {
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    }
                }
            
            else:
                return {"error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}}
        
        else:
            return {"error": {"code": -32601, "message": f"Unknown method: {method}"}}
            
    except Exception as e:
        logger.error(f"MCP request failed: {e}")
        return {"error": {"code": -32603, "message": str(e)}}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Send SSE headers
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Headers', 'Cache-Control')
            self.end_headers()
            
            # Send initial server info
            server_info = {
                "jsonrpc": "2.0",
                "method": "server/info",
                "params": {
                    "name": "MCPizza",
                    "version": "1.0.0",
                    "description": "Domino's Pizza Ordering MCP Server",
                    "real_api_enabled": os.getenv("MCPIZZA_REAL_API", "false") == "true",
                    "fallback_enabled": os.getenv("MCPIZZA_FALLBACK_MOCK", "true") == "true"
                }
            }
            
            self.wfile.write(f"data: {json.dumps(server_info)}\n\n".encode())
            self.wfile.flush()
            
        except Exception as e:
            logger.error(f"SSE GET error: {e}")
            self.send_response(500)
            self.end_headers()
    
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length).decode('utf-8')
                message = json.loads(body)
            else:
                message = {}
            
            response = handle_mcp_request(message)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            logger.error(f"POST error: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": {"code": -32603, "message": str(e)}}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
