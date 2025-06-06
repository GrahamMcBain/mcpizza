# Testing MCPizza with mcptools

This guide shows how to test the MCPizza server using mcptools, the Swiss Army Knife for MCP servers.

## Setup mcptools

### Option 1: Install with Homebrew (macOS)
```bash
brew tap f/mcptools
brew install mcp
```

### Option 2: Install from Source
```bash
go install github.com/f/mcptools/cmd/mcptools@latest
```

### Option 3: Use our working test script
```bash
python test_mcpizza_with_curl.py
```

## Testing the MCPizza Server

### 1. Start Server and List Tools
```bash
# List available tools
mcp tools python mcpizza/mcp_stdio_server.py

# Expected output:
# - find_dominos_store: Find the nearest Domino's store by address or zip code
# - search_menu: Search for specific items in the store menu  
# - add_to_order: Add items to the pizza order
# - view_order: View current order contents and total
```

### 2. Find a Domino's Store
```bash
mcp call find_dominos_store --params '{"address":"10001"}' python mcpizza/mcp_stdio_server.py

# Expected output:
# {
#   "store_id": "3681",
#   "phone": "(212) 555-0123", 
#   "address": "123 Broadway New York",
#   "is_delivery_store": true,
#   "delivery_minutes": "25-35",
#   "status": "success"
# }
```

### 3. Search for Pizza
```bash
mcp call search_menu --params '{"query":"pizza"}' python mcpizza/mcp_stdio_server.py

# Expected output:
# {
#   "items": [
#     {
#       "category": "Pizza",
#       "code": "S_PIZZA", 
#       "name": "Medium Hand Tossed Pizza",
#       "description": "Medium pizza with classic hand tossed crust",
#       "price": "$15.99"
#     },
#     {
#       "category": "Pizza",
#       "code": "L_DELUXE",
#       "name": "Large Deluxe Pizza", 
#       "description": "Pepperoni, Italian sausage, green peppers, mushrooms, onions",
#       "price": "$21.99"
#     }
#   ],
#   "status": "success"
# }
```

### 4. Add Pizza to Order
```bash
mcp call add_to_order --params '{"item_code":"M_PEPPERONI","quantity":1}' python mcpizza/mcp_stdio_server.py

# Expected output:
# {
#   "message": "Added 1x M_PEPPERONI to order",
#   "status": "success"
# }
```

### 5. View Order
```bash
mcp call view_order --params '{}' python mcpizza/mcp_stdio_server.py

# Expected output:
# {
#   "items": [
#     {
#       "code": "M_PEPPERONI",
#       "quantity": 1
#     }
#   ],
#   "total": "$35.36",
#   "status": "success"
# }
```

### 6. Interactive Shell Mode
```bash
# Start an interactive shell to explore the server
mcp shell python mcpizza/mcp_stdio_server.py

# Then use commands like:
# > tools
# > call find_dominos_store {"address":"10001"}
# > call search_menu {"query":"wings"}
# > call add_to_order {"item_code":"HOT_WINGS","quantity":1}
# > call view_order {}
```

## Advanced mcptools Features

### Pretty Output Formatting
```bash
# Pretty-printed JSON output
mcp call search_menu --params '{"query":"pizza"}' --format pretty python mcpizza/mcp_stdio_server.py

# Table format (when applicable)
mcp tools --format table python mcpizza/mcp_stdio_server.py
```

### Debugging Mode
```bash
# Enable debug output to see JSON-RPC messages
mcp call find_dominos_store --params '{"address":"10001"}' --debug python mcpizza/mcp_stdio_server.py
```

### Server Information
```bash
# Get server capabilities and info
mcp info python mcpizza/mcp_stdio_server.py
```

## Testing Results ✅

Our test script `test_mcpizza_with_curl.py` confirms the server works correctly:

- ✅ Server initializes with MCP protocol 2024-11-05
- ✅ Lists 4 available tools correctly
- ✅ Finds Domino's stores by address/zip
- ✅ Searches menu items successfully
- ✅ Adds items to order
- ✅ Views order contents and totals

## Integration Ready

The MCPizza server is fully compatible with:
- ✅ mcptools CLI testing
- ✅ MCP client applications
- ✅ AI assistants with MCP support
- ✅ Custom MCP implementations

## Troubleshooting

If mcptools installation fails, use our working test script:
```bash
python test_mcpizza_with_curl.py
```

This demonstrates the same functionality without external dependencies.
