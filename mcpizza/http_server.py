#!/usr/bin/env python3
"""
MCPizza HTTP Server - Domino's Pizza Ordering MCP Server via HTTP
"""

import asyncio
import logging
from mcp.server.fastmcp import FastMCP

# Import all the tools and logic from the main server
from server import (
    pizza_order,
    find_dominos_store_impl,
    get_store_menu_categories_impl,
    search_menu_impl,
    add_to_order_impl,
    view_order_impl,
    set_customer_info_impl,
    calculate_order_total_impl,
    prepare_order_impl,
    TOOLS
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcpizza-http")

# Create FastMCP server
mcp = FastMCP("MCPizza")

# Register all tools
@mcp.tool()
def find_dominos_store(address: str) -> str:
    """Find nearest Domino's store by address or zip code"""
    return find_dominos_store_impl({"address": address})

@mcp.tool()
def get_store_menu_categories(store_id: str) -> str:
    """Get menu categories for a specific store"""
    return get_store_menu_categories_impl({"store_id": store_id})

@mcp.tool()
def search_menu(query: str, store_id: str = None) -> str:
    """Search menu items by name or description"""
    args = {"query": query}
    if store_id:
        args["store_id"] = store_id
    return search_menu_impl(args)

@mcp.tool()
def add_to_order(item_code: str, quantity: int = 1, size: str = None, crust: str = None, toppings: list = None) -> str:
    """Add item to current order"""
    args = {"item_code": item_code, "quantity": quantity}
    if size:
        args["size"] = size
    if crust:
        args["crust"] = crust
    if toppings:
        args["toppings"] = toppings
    return add_to_order_impl(args)

@mcp.tool()
def view_order() -> str:
    """View current order contents and total"""
    return view_order_impl({})

@mcp.tool()
def set_customer_info(name: str, phone: str, address: str, city: str, state: str, zip_code: str, email: str = None) -> str:
    """Set customer delivery information"""
    args = {
        "name": name,
        "phone": phone, 
        "address": address,
        "city": city,
        "state": state,
        "zip_code": zip_code
    }
    if email:
        args["email"] = email
    return set_customer_info_impl(args)

@mcp.tool()
def calculate_order_total() -> str:
    """Calculate order total with tax and fees"""
    return calculate_order_total_impl({})

@mcp.tool()
def prepare_order() -> str:
    """Prepare order for placement (safe preview mode)"""
    return prepare_order_impl({})

if __name__ == "__main__":
    # Run the HTTP server
    mcp.run(debug=True, host="localhost", port=8000)
