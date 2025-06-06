#!/usr/bin/env python3
"""
MCPizza - Domino's Pizza Ordering MCP Server

This server provides tools for ordering pizza through the unofficial Domino's API.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    GetToolRequest,
    GetToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
)

try:
    from pizzapi import *
    from pizzapi import PaymentObject
except ImportError:
    print("pizzapi not installed. Install with: pip install pizzapi")
    exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcpizza")

class PizzaOrder:
    """Manages a pizza order state"""
    def __init__(self):
        self.store = None
        self.customer = None
        self.order = None
        self.items = []

pizza_order = PizzaOrder()

# Available tools
TOOLS = [
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
        name="get_store_menu",
        description="Get the full menu from a Domino's store",
        inputSchema={
            "type": "object",
            "properties": {
                "store_id": {
                    "type": "string",
                    "description": "Store ID from find_dominos_store result"
                }
            },
            "required": ["store_id"]
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
                },
                "store_id": {
                    "type": "string",
                    "description": "Store ID from find_dominos_store result"
                }
            },
            "required": ["query", "store_id"]
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
        name="apply_coupon",
        description="Apply a coupon code to the order",
        inputSchema={
            "type": "object",
            "properties": {
                "coupon_code": {
                    "type": "string",
                    "description": "Domino's coupon code"
                }
            },
            "required": ["coupon_code"]
        }
    ),
    Tool(
        name="place_order",
        description="Place the pizza order (requires customer info and payment)",
        inputSchema={
            "type": "object",
            "properties": {
                "payment_info": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "enum": ["card", "cash"]},
                        "card_number": {"type": "string", "description": "Credit card number (required for card payments)"},
                        "expiration": {"type": "string", "description": "Card expiration in MMYY format (required for card payments)"},
                        "cvv": {"type": "string", "description": "3-digit security code (required for card payments)"},
                        "billing_zip": {"type": "string", "description": "Billing zip code (required for card payments)"},
                        "tip_amount": {"type": "number", "description": "Tip amount", "default": 0}
                    },
                    "required": ["type"]
                }
            },
            "required": ["payment_info"]
        }
    )
]

async def handle_find_dominos_store(arguments: Dict[str, Any]) -> CallToolResult:
    """Find nearest Domino's store"""
    try:
        address = arguments["address"]
        
        # Find nearest store
        my_local_dominos = StoreLocator.find_closest_store_to_customer(address)
        
        if not my_local_dominos:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="No Domino's stores found near that address."
                )]
            )
        
        # Store the found store globally for use in other tools
        pizza_order.store = my_local_dominos
        
        store_info = {
            "store_id": my_local_dominos.data.get("StoreID"),
            "phone": my_local_dominos.data.get("Phone"),
            "address": f"{my_local_dominos.data.get('StreetName', '')} {my_local_dominos.data.get('City', '')}",
            "is_delivery_store": my_local_dominos.data.get("IsDeliveryStore"),
            "min_delivery_order_amount": my_local_dominos.data.get("MinDeliveryOrderAmount"),
            "delivery_minutes": my_local_dominos.data.get("ServiceEstimatedWaitMinutes", {}).get("Delivery"),
            "pickup_minutes": my_local_dominos.data.get("ServiceEstimatedWaitMinutes", {}).get("Carryout")
        }
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Found Domino's store:\n{json.dumps(store_info, indent=2)}"
            )]
        )
        
    except Exception as e:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Error finding store: {str(e)}"
            )]
        )

async def handle_get_store_menu(arguments: Dict[str, Any]) -> CallToolResult:
    """Get store menu"""
    try:
        if not pizza_order.store:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="No store selected. Use find_dominos_store first."
                )]
            )
        
        menu = pizza_order.store.get_menu()
        
        # Extract useful menu categories
        categories = {}
        for category_name, items in menu.data.items():
            if isinstance(items, dict) and "Products" in items:
                products = []
                for product_code, product_data in items["Products"].items():
                    if isinstance(product_data, dict):
                        products.append({
                            "code": product_code,
                            "name": product_data.get("Name", ""),
                            "description": product_data.get("Description", ""),
                            "price": product_data.get("Price", "")
                        })
                categories[category_name] = products
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Store menu categories:\n{json.dumps(list(categories.keys()), indent=2)}\n\nUse search_menu to find specific items."
            )]
        )
        
    except Exception as e:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Error getting menu: {str(e)}"
            )]
        )

async def handle_search_menu(arguments: Dict[str, Any]) -> CallToolResult:
    """Search menu for items"""
    try:
        if not pizza_order.store:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="No store selected. Use find_dominos_store first."
                )]
            )
        
        query = arguments["query"].lower()
        menu = pizza_order.store.get_menu()
        
        matching_items = []
        
        # Search through menu categories
        for category_name, items in menu.data.items():
            if isinstance(items, dict) and "Products" in items:
                for product_code, product_data in items["Products"].items():
                    if isinstance(product_data, dict):
                        name = product_data.get("Name", "").lower()
                        description = product_data.get("Description", "").lower()
                        
                        if query in name or query in description:
                            matching_items.append({
                                "category": category_name,
                                "code": product_code,
                                "name": product_data.get("Name", ""),
                                "description": product_data.get("Description", ""),
                                "price": product_data.get("Price", "")
                            })
        
        if not matching_items:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"No items found matching '{query}'"
                )]
            )
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Found {len(matching_items)} items:\n{json.dumps(matching_items, indent=2)}"
            )]
        )
        
    except Exception as e:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Error searching menu: {str(e)}"
            )]
        )

async def handle_add_to_order(arguments: Dict[str, Any]) -> CallToolResult:
    """Add item to order"""
    try:
        if not pizza_order.store:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="No store selected. Use find_dominos_store first."
                )]
            )
        
        if not pizza_order.order:
            # Initialize order
            pizza_order.order = Order(pizza_order.store)
        
        item_code = arguments["item_code"]
        quantity = arguments.get("quantity", 1)
        options = arguments.get("options", {})
        
        # Add item to order
        for _ in range(quantity):
            pizza_order.order.add_item(item_code, options)
        
        pizza_order.items.append({
            "code": item_code,
            "quantity": quantity,
            "options": options
        })
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Added {quantity}x {item_code} to order"
            )]
        )
        
    except Exception as e:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Error adding item: {str(e)}"
            )]
        )

async def handle_view_order(arguments: Dict[str, Any]) -> CallToolResult:
    """View current order"""
    try:
        if not pizza_order.order:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="No items in order yet."
                )]
            )
        
        order_data = pizza_order.order.data
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Current order:\n{json.dumps(pizza_order.items, indent=2)}\n\nOrder data: {json.dumps(order_data, indent=2)}"
            )]
        )
        
    except Exception as e:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Error viewing order: {str(e)}"
            )]
        )

async def handle_set_customer_info(arguments: Dict[str, Any]) -> CallToolResult:
    """Set customer information"""
    try:
        customer_data = {
            "FirstName": arguments["first_name"],
            "LastName": arguments["last_name"], 
            "Email": arguments["email"],
            "Phone": arguments["phone"],
            "Address": {
                "Street": arguments["address"]["street"],
                "City": arguments["address"]["city"],
                "Region": arguments["address"]["region"],
                "PostalCode": arguments["address"]["zip"]
            }
        }
        
        pizza_order.customer = Customer(
            first_name=arguments["first_name"],
            last_name=arguments["last_name"],
            email=arguments["email"], 
            phone=arguments["phone"],
            address=Address(
                street=arguments["address"]["street"],
                city=arguments["address"]["city"],
                state=arguments["address"]["region"],
                zip=arguments["address"]["zip"]
            )
        )
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text="Customer information set successfully"
            )]
        )
        
    except Exception as e:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Error setting customer info: {str(e)}"
            )]
        )

async def handle_calculate_order_total(arguments: Dict[str, Any]) -> CallToolResult:
    """Calculate order total"""
    try:
        if not pizza_order.order:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="No order to calculate."
                )]
            )
        
        if pizza_order.customer:
            pizza_order.order.set_customer(pizza_order.customer)
        
        # Get order pricing
        order_data = pizza_order.order.data
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Order total calculation:\n{json.dumps(order_data.get('Amounts', {}), indent=2)}"
            )]
        )
        
    except Exception as e:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Error calculating total: {str(e)}"
            )]
        )

async def handle_apply_coupon(arguments: Dict[str, Any]) -> CallToolResult:
    """Apply coupon to order"""
    try:
        if not pizza_order.order:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="No order to apply coupon to."
                )]
            )
        
        coupon_code = arguments["coupon_code"]
        
        # Apply coupon
        pizza_order.order.add_coupon(coupon_code)
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Applied coupon: {coupon_code}"
            )]
        )
        
    except Exception as e:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Error applying coupon: {str(e)}"
            )]
        )

async def handle_place_order(arguments: Dict[str, Any]) -> CallToolResult:
    """Place the order"""
    try:
        if not pizza_order.order:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="No order to place."
                )]
            )
        
        if not pizza_order.customer:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Customer information required. Use set_customer_info first."
                )]
            )
        
        payment_info = arguments["payment_info"]
        
        # Set customer info on order
        pizza_order.order.set_customer(pizza_order.customer)
        
        # Handle payment based on type
        if payment_info["type"] == "cash":
            # For cash orders, just validate and prepare
            result = {"Status": "Success", "OrderID": "CASH_ORDER", "Message": "Cash order prepared for pickup"}
            
        elif payment_info["type"] == "card":
            # Validate required card fields
            required_fields = ["card_number", "expiration", "cvv", "billing_zip"]
            missing_fields = [field for field in required_fields if field not in payment_info or not payment_info[field]]
            
            if missing_fields:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Missing required card information: {', '.join(missing_fields)}"
                    )]
                )
            
            # Create payment object
            card = PaymentObject(
                number=payment_info["card_number"],
                expiration=payment_info["expiration"],
                cvv=payment_info["cvv"],
                zip=payment_info["billing_zip"]
            )
            
            # Add tip if provided
            tip_amount = payment_info.get("tip_amount", 0)
            if tip_amount > 0:
                pizza_order.order.add_item({'Code': 'DELIVERY_TIP', 'Qty': 1, 'Price': tip_amount})
            
            # Place the actual order
            result = pizza_order.order.place(card)
            
        else:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Invalid payment type. Must be 'card' or 'cash'."
                )]
            )
        
        # Format success response
        if isinstance(result, dict) and result.get("Status") == "Success":
            order_id = result.get("OrderID", "Unknown")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"🍕 Order placed successfully!\n\nOrder ID: {order_id}\nPayment: {payment_info['type']}\n\nYour pizza is being prepared!"
                )]
            )
        else:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Order placement failed: {result}"
                )]
            )
        
    except Exception as e:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Error placing order: {str(e)}"
            )]
        )

# Tool handlers mapping
TOOL_HANDLERS = {
    "find_dominos_store": handle_find_dominos_store,
    "get_store_menu": handle_get_store_menu,
    "search_menu": handle_search_menu,
    "add_to_order": handle_add_to_order,
    "view_order": handle_view_order,
    "set_customer_info": handle_set_customer_info,
    "calculate_order_total": handle_calculate_order_total,
    "apply_coupon": handle_apply_coupon,
    "place_order": handle_place_order,
}

def create_server() -> Server:
    """Create the MCP server instance"""
    server = Server("mcpizza")

    @server.list_tools()
    async def handle_list_tools() -> ListToolsResult:
        """List available tools"""
        return ListToolsResult(tools=TOOLS)

    @server.call_tool()
    async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
        """Handle tool calls"""
        if request.params.name not in TOOL_HANDLERS:
            raise ValueError(f"Unknown tool: {request.params.name}")
        
        handler = TOOL_HANDLERS[request.params.name]
        return await handler(request.params.arguments or {})

    return server

async def main():
    """Run the server"""
    server = create_server()
    options = InitializationOptions(
        server_name="mcpizza",
        server_version="0.1.0"
    )
    await stdio_server(server, options)

if __name__ == "__main__":
    asyncio.run(main())
