<<<<<<< HEAD
# MCPizza - Domino's Pizza Ordering MCP Server

An MCP (Model Context Protocol) server that enables AI assistants to order pizza using the unofficial Domino's API.

## 🍕 Features

- **Store Locator**: Find nearest Domino's stores by address/zip code
- **Menu Browsing**: Search for pizzas, wings, sides, and more
- **Order Management**: Add items to cart and calculate totals
- **Customer Info**: Handle delivery addresses and contact information  
- **Safe Preview**: Prepare orders without placing them (safety first!)

## 🚀 Quick Demo

```bash
# See it in action with mock data
python mcpizza/demo_no_real_api.py
```

## 📦 Installation

See [INSTALLATION.md](INSTALLATION.md) for detailed setup instructions.

Quick start:
```bash
# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup environment
uv venv && source .venv/bin/activate
uv pip install pizzapi requests pydantic

# Run demo
python mcpizza/demo_no_real_api.py
```

## 🛠 Available MCP Tools

| Tool | Description |
|------|-------------|
| `find_dominos_store` | Find nearest Domino's location |
| `get_store_menu_categories` | Get menu categories |
| `search_menu` | Search for specific menu items |
| `add_to_order` | Add items to your pizza order |
| `view_order` | View current order contents |
| `set_customer_info` | Set delivery information |
| `calculate_order_total` | Get order total with tax/fees |
| `prepare_order` | Prepare order for placement (safe mode) |

## 🎯 Usage Examples

```python
# Find store
result = server.call_tool("find_dominos_store", {"address": "10001"})

# Search for pizza
result = server.call_tool("search_menu", {"query": "pepperoni pizza"})

# Add to order
result = server.call_tool("add_to_order", {
    "item_code": "M_PEPPERONI", 
    "quantity": 1
})
```

## ⚠️ Safety & Disclaimers

- **Real order placement is DISABLED by default** for safety
- Uses unofficial Domino's API for educational purposes only
- All order functionality works except final placement step
- Use responsibly and in accordance with Domino's terms of service

## 🔧 Integration

Ready to integrate with MCP clients! The server provides a complete pizza ordering workflow while maintaining safety through disabled order placement.

## 📝 Requirements

- Python 3.9+
- pizzapi package for Domino's API access
- Valid address for store lookup
- Internet connection for API calls

---

Built with ❤️ for the MCP ecosystem
