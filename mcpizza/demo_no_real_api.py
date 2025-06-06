#!/usr/bin/env python3
"""
MCPizza Demo - Pizza Ordering Simulation

This demonstrates the pizza ordering workflow without hitting real APIs,
showing how the MCP server would work.
"""

import json
from typing import Dict, Any

class MockPizzaOrderManager:
    """Mock pizza ordering for demonstration"""
    
    def __init__(self):
        self.store = None
        self.customer = None
        self.order = None
        self.items = []
        
    def find_store(self, address: str) -> Dict[str, Any]:
        """Mock store finding"""
        self.store = {
            "store_id": "3681",
            "phone": "(212) 555-0123",
            "address": "123 Broadway New York",
            "is_delivery_store": True,
            "min_delivery_order_amount": 10.00,
            "delivery_minutes": "25-35",
            "pickup_minutes": "15-25"
        }
        
        return {**self.store, "status": "success"}
    
    def get_menu_categories(self) -> Dict[str, Any]:
        """Mock menu categories"""
        categories = [
            "Pizza", "Sandwiches", "Wings", "Pasta", "Sides", 
            "Desserts", "Drinks", "Salads"
        ]
        
        return {
            "categories": categories,
            "store_id": self.store["store_id"] if self.store else "3681",
            "status": "success"
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
            ],
            "sides": [
                {
                    "category": "Sides",
                    "code": "BREADSTICKS",
                    "name": "Garlic Breadsticks",
                    "description": "Warm breadsticks with garlic seasoning",
                    "price": "$6.99"
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
    
    def add_to_order(self, item_code: str, quantity: int = 1, options: Dict = None) -> Dict[str, Any]:
        """Mock adding to order"""
        if options is None:
            options = {}
            
        self.items.append({
            "code": item_code,
            "quantity": quantity,
            "options": options
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
            "order_total": "$28.97",
            "tax": "$2.40",
            "delivery_fee": "$3.99",
            "grand_total": "$35.36",
            "status": "success"
        }
    
    def set_customer_info(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock customer info setting"""
        self.customer = customer_data
        return {"message": "Customer information set successfully", "status": "success"}
    
    def calculate_total(self) -> Dict[str, Any]:
        """Mock total calculation"""
        return {
            "subtotal": "$28.97",
            "tax": "$2.40", 
            "delivery_fee": "$3.99",
            "grand_total": "$35.36",
            "status": "success"
        }
    
    def prepare_order_preview(self) -> Dict[str, Any]:
        """Mock order preview"""
        if not self.customer:
            return {"error": "Customer information required"}
            
        return {
            "message": "Order ready for placement",
            "items": self.items,
            "customer": self.customer,
            "total": "$35.36",
            "warning": "⚠️  THIS IS A MOCK DEMO - NO REAL ORDER PLACED ⚠️",
            "status": "success"
        }

def demo_pizza_ordering():
    """Complete pizza ordering demo"""
    print("🍕 MCPizza Demo - Pizza Ordering Simulation")
    print("=" * 50)
    
    manager = MockPizzaOrderManager()
    
    # Step 1: Find store
    print("\n1. Finding store...")
    result = manager.find_store("New York, NY 10001")
    print(f"✅ Found store: {result['store_id']} at {result['address']}")
    print(f"   📞 {result['phone']}")
    print(f"   🚚 Delivery: {result['delivery_minutes']} min")
    
    # Step 2: Get menu categories
    print("\n2. Getting menu categories...")
    result = manager.get_menu_categories()
    categories = result["categories"]
    print(f"✅ Found {len(categories)} menu categories:")
    for cat in categories:
        print(f"   - {cat}")
    
    # Step 3: Search for pizza
    print("\n3. Searching for pizza...")
    result = manager.search_menu("pizza")
    items = result["items"]
    print(f"✅ Found {len(items)} pizza items:")
    for item in items:
        print(f"   - {item['name']} ({item['code']}) - {item['price']}")
    
    # Step 4: Add items to order
    print("\n4. Adding pizza and sides to order...")
    manager.add_to_order("M_PEPPERONI", 1)
    print("✅ Added 1x Medium Pepperoni Pizza")
    
    # Add wings
    result = manager.search_menu("wings")
    if "items" in result:
        manager.add_to_order("HOT_WINGS", 1)
        print("✅ Added 1x Hot Buffalo Wings")
    
    # Add breadsticks  
    manager.add_to_order("BREADSTICKS", 1)
    print("✅ Added 1x Garlic Breadsticks")
    
    # Step 5: View order
    print("\n5. Viewing order...")
    result = manager.view_order()
    print(f"✅ Order contains {len(result['items'])} items:")
    for item in result['items']:
        print(f"   - {item['quantity']}x {item['code']}")
    print(f"   💰 Total: {result['grand_total']}")
    
    # Step 6: Set customer info
    print("\n6. Setting customer information...")
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
    print(f"✅ {result['message']}")
    print(f"   👤 {customer_data['first_name']} {customer_data['last_name']}")
    print(f"   📧 {customer_data['email']}")
    print(f"   📍 {customer_data['address']['street']}, {customer_data['address']['city']}")
    
    # Step 7: Calculate final total
    print("\n7. Calculating final total...")
    result = manager.calculate_total()
    print("✅ Order breakdown:")
    print(f"   Subtotal: {result['subtotal']}")
    print(f"   Tax: {result['tax']}")
    print(f"   Delivery: {result['delivery_fee']}")
    print(f"   🎯 Grand Total: {result['grand_total']}")
    
    # Step 8: Order preview (but don't place)
    print("\n8. Preparing order preview...")
    result = manager.prepare_order_preview()
    print(f"✅ {result['message']}")
    print(f"⚠️  {result['warning']}")
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed successfully!")
    print("\nWhat MCPizza can do:")
    print("✅ Find nearby Domino's stores")
    print("✅ Browse and search menus") 
    print("✅ Add items to cart")
    print("✅ Calculate totals with tax/fees")
    print("✅ Manage customer information")
    print("✅ Prepare orders for placement")
    print("\n🔧 Ready to integrate with MCP clients!")

if __name__ == "__main__":
    demo_pizza_ordering()
