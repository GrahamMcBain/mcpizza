#!/usr/bin/env python3
"""
MCPizza - Simplified Domino's Pizza Ordering Server

This is a simplified version that demonstrates the pizza ordering functionality
without requiring the full MCP SDK.
"""

import json
import logging
from typing import Any, Dict, List, Optional

try:
    from pizzapi import Address, Customer, Order, Store
except ImportError:
    print("pizzapi not installed. Install with: pip install pizzapi")
    exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcpizza")

class PizzaOrderManager:
    """Manages pizza orders"""
    
    def __init__(self):
        self.store = None
        self.customer = None
        self.order = None
        self.items = []
    
    def find_store(self, address_str: str) -> Dict[str, Any]:
        """Find nearest Domino's store"""
        try:
            logger.info(f"Finding store near: {address_str}")
            
            # Parse address string - try to extract components
            parts = address_str.split(',')
            if len(parts) >= 2:
                city = parts[-2].strip()
                region = parts[-1].strip()
                street = parts[0].strip()
            else:
                # Assume it's a zip code
                street = "123 Main St"  # Placeholder
                city = "New York"       # Placeholder  
                region = address_str.strip()
            
            # Create address object
            address = Address(street=street, city=city, region=region)
            
            # Find closest store
            store = address.closest_store()
            
            if not store:
                return {"error": "No Domino's stores found near that address"}
            
            self.store = store
            
            store_info = {
                "store_id": store.data.get("StoreID"),
                "phone": store.data.get("Phone"), 
                "address": f"{store.data.get('StreetName', '')} {store.data.get('City', '')}",
                "is_delivery_store": store.data.get("IsDeliveryStore"),
                "min_delivery_order_amount": store.data.get("MinDeliveryOrderAmount"),
                "delivery_minutes": store.data.get("ServiceEstimatedWaitMinutes", {}).get("Delivery"),
                "pickup_minutes": store.data.get("ServiceEstimatedWaitMinutes", {}).get("Carryout"),
                "status": "success"
            }
            
            logger.info(f"Found store: {store_info['store_id']}")
            return store_info
            
        except Exception as e:
            logger.error(f"Error finding store: {e}")
            return {"error": f"Error finding store: {str(e)}"}
    
    def search_menu(self, query: str) -> Dict[str, Any]:
        """Search menu for items"""
        try:
            if not self.store:
                return {"error": "No store selected. Use find_store first."}
            
            logger.info(f"Searching menu for: {query}")
            
            # Get menu from store
            try:
                menu = self.store.get_menu()
                logger.info(f"Menu loaded successfully")
            except Exception as menu_error:
                logger.warning(f"Menu loading error: {menu_error}")
                # Try to continue with limited menu
                return {"error": f"Menu loading issue: {str(menu_error)}"}
            
            matching_items = []
            query_lower = query.lower()
            
            # Search through menu categories
            try:
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
            except Exception as search_error:
                logger.warning(f"Menu search error: {search_error}")
                # Return a simplified response
                return {"error": f"Menu search issue, but store found. Try 'get_menu' first: {str(search_error)}"}
            
            if not matching_items:
                return {"error": f"No items found matching '{query}'"}
            
            logger.info(f"Found {len(matching_items)} matching items")
            return {"items": matching_items, "status": "success"}
            
        except Exception as e:
            logger.error(f"Error searching menu: {e}")
            return {"error": f"Error searching menu: {str(e)}"}
    
    def get_menu_categories(self) -> Dict[str, Any]:
        """Get menu categories without detailed search"""
        try:
            if not self.store:
                return {"error": "No store selected. Use find_store first."}
            
            menu = self.store.get_menu()
            categories = list(menu.data.keys())
            
            return {
                "categories": categories,
                "store_id": self.store.data.get("StoreID"),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error getting menu categories: {e}")
            return {"error": f"Error getting menu categories: {str(e)}"}
    
    def add_to_order(self, item_code: str, quantity: int = 1, options: Dict = None) -> Dict[str, Any]:
        """Add item to order"""
        try:
            if not self.store:
                return {"error": "No store selected. Use find_store first."}
            
            if not self.order:
                self.order = Order(self.store)
            
            if options is None:
                options = {}
            
            logger.info(f"Adding {quantity}x {item_code} to order")
            
            # Add item to order
            for _ in range(quantity):
                self.order.add_item(item_code, options)
            
            self.items.append({
                "code": item_code,
                "quantity": quantity,
                "options": options
            })
            
            return {
                "message": f"Added {quantity}x {item_code} to order",
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error adding item: {e}")
            return {"error": f"Error adding item: {str(e)}"}
    
    def view_order(self) -> Dict[str, Any]:
        """View current order"""
        try:
            if not self.order:
                return {"message": "No items in order yet"}
            
            return {
                "items": self.items,
                "order_data": self.order.data,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error viewing order: {e}")
            return {"error": f"Error viewing order: {str(e)}"}
    
    def set_customer_info(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Set customer information"""
        try:
            address = Address(
                street=customer_data["address"]["street"],
                city=customer_data["address"]["city"],
                region=customer_data["address"]["region"],
                zip=customer_data["address"]["zip"]
            )
            
            self.customer = Customer(
                first_name=customer_data["first_name"],
                last_name=customer_data["last_name"],
                email=customer_data["email"],
                phone=customer_data["phone"],
                address=address
            )
            
            logger.info("Customer information set")
            return {"message": "Customer information set successfully", "status": "success"}
            
        except Exception as e:
            logger.error(f"Error setting customer info: {e}")
            return {"error": f"Error setting customer info: {str(e)}"}
    
    def calculate_total(self) -> Dict[str, Any]:
        """Calculate order total"""
        try:
            if not self.order:
                return {"error": "No order to calculate"}
            
            if self.customer:
                self.order.set_customer(self.customer)
            
            amounts = self.order.data.get("Amounts", {})
            
            return {
                "amounts": amounts,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error calculating total: {e}")
            return {"error": f"Error calculating total: {str(e)}"}
    
    def prepare_order_preview(self) -> Dict[str, Any]:
        """Get order preview without placing it"""
        try:
            if not self.order:
                return {"error": "No order to preview"}
            
            if not self.customer:
                return {"error": "Customer information required"}
            
            self.order.set_customer(self.customer)
            
            return {
                "message": "Order ready for placement",
                "items": self.items,
                "order_summary": self.order.data,
                "warning": "⚠️  ACTUAL ORDER PLACEMENT DISABLED FOR SAFETY ⚠️",
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error preparing order: {e}")
            return {"error": f"Error preparing order: {str(e)}"}

def demo_pizza_ordering():
    """Demonstration of pizza ordering functionality"""
    print("🍕 MCPizza Demo - Domino's Pizza Ordering")
    print("=" * 50)
    
    manager = PizzaOrderManager()
    
    # Step 1: Find store
    print("\n1. Finding store...")
    result = manager.find_store("10001")  # NYC zip code
    if "error" in result:
        print(f"❌ {result['error']}")
        return
    print(f"✅ Found store: {result['store_id']}")
    
    # Step 2: Get menu categories
    print("\n2. Getting menu categories...")
    result = manager.get_menu_categories()
    if "error" in result:
        print(f"❌ {result['error']}")
        return
    
    categories = result["categories"]
    print(f"✅ Found {len(categories)} menu categories:")
    for cat in categories[:5]:  # Show first 5
        print(f"   - {cat}")
    
    # Step 2b: Search for pizza
    print("\n2b. Searching for pizza...")
    result = manager.search_menu("pizza")
    if "error" in result:
        print(f"❌ {result['error']}")
        print("   Continuing with demo using known item codes...")
        items = [{"name": "Medium Pizza", "code": "S_PIZZA"}]  # Fallback
    else:
        items = result["items"][:3]  # Show first 3 items
        print(f"✅ Found {len(result['items'])} pizza items. First 3:")
        for item in items:
            print(f"   - {item['name']} ({item['code']})")
    
    # Step 3: Add item to order (using first pizza found)
    if items:
        print("\n3. Adding pizza to order...")
        pizza_code = items[0]["code"]
        result = manager.add_to_order(pizza_code, 1)
        if "error" in result:
            print(f"❌ {result['error']}")
        else:
            print(f"✅ {result['message']}")
    
    # Step 4: View order
    print("\n4. Viewing order...")
    result = manager.view_order()
    if "error" in result:
        print(f"❌ {result['error']}")
    else:
        print(f"✅ Order contains {len(result['items'])} items")
    
    # Step 5: Set customer info
    print("\n5. Setting customer info...")
    customer_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone": "555-123-4567",
        "address": {
            "street": "123 Main St",
            "city": "New York", 
            "region": "NY",
            "zip": "10001"
        }
    }
    
    result = manager.set_customer_info(customer_data)
    if "error" in result:
        print(f"❌ {result['error']}")
    else:
        print(f"✅ {result['message']}")
    
    # Step 6: Calculate total
    print("\n6. Calculating total...")
    result = manager.calculate_total()
    if "error" in result:
        print(f"❌ {result['error']}")
    else:
        amounts = result["amounts"]
        print(f"✅ Order total: ${amounts.get('Customer', 0)}")
    
    # Step 7: Prepare order (but don't place it)
    print("\n7. Preparing order preview...")
    result = manager.prepare_order_preview()
    if "error" in result:
        print(f"❌ {result['error']}")
    else:
        print(f"✅ {result['message']}")
        print(f"⚠️  {result['warning']}")
    
    print("\n🎉 Demo completed successfully!")

if __name__ == "__main__":
    demo_pizza_ordering()
