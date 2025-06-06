# MCPizza Installation Guide

## Quick Start

1. **Clone and setup:**
   ```bash
   git clone <your-repo>
   cd MCPIZZA
   ```

2. **Install uv (Python package manager):**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source $HOME/.local/bin/env
   ```

3. **Create virtual environment and install dependencies:**
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install pizzapi requests pydantic
   ```

4. **Run the demo:**
   ```bash
   # Mock demo (recommended first)
   python mcpizza/demo_no_real_api.py
   
   # Real API demo (may have issues with menu loading)
   PYTHONPATH=. python mcpizza/simple_server.py
   
   # MCP server demo
   PYTHONPATH=. python mcpizza/mcp_server.py demo
   ```

## What's Included

### Core Files
- `mcpizza/simple_server.py` - Core pizza ordering logic
- `mcpizza/mcp_server.py` - MCP server implementation  
- `mcpizza/demo_no_real_api.py` - Working demonstration
- `mcpizza/config.py` - Configuration management
- `mcpizza/exceptions.py` - Custom exceptions

### Features Implemented
- ✅ Find nearby Domino's stores
- ✅ Browse menu categories (with fallback for API issues)
- ✅ Search for menu items
- ✅ Add items to order
- ✅ Calculate totals with tax/fees
- ✅ Customer information management
- ✅ Order preparation (safe mode - no real orders placed)

### MCP Tools Available
1. `find_dominos_store` - Find nearest location
2. `get_store_menu_categories` - Get menu categories  
3. `search_menu` - Search for specific items
4. `add_to_order` - Add items to cart
5. `view_order` - View order contents
6. `set_customer_info` - Set delivery information
7. `calculate_order_total` - Get order total
8. `prepare_order` - Prepare order (safe preview)

## Known Issues

The pizzapi library has some issues with certain menu items (like "CouponPizza") that cause errors when loading full menus. The server includes fallback handling for this.

## Safety Features

- ⚠️ **Real order placement is disabled by default** for safety
- All order operations work up to the final placement step
- Mock demo shows full functionality without API dependencies
- Comprehensive error handling and logging

## Next Steps

To enable real orders:
1. Set `enable_real_orders = True` in config
2. Uncomment the `order.place()` call in the code
3. Add proper payment integration
4. Add order confirmation flows

## Integration

To integrate with MCP clients:
1. Implement proper MCP stdio transport
2. Handle authentication if needed
3. Add rate limiting and proper error responses
4. Consider adding order tracking tools
