# MCPizza - Cloudflare Remote MCP Server

A remote MCP server for ordering pizza using the Domino's API, deployed on Cloudflare Workers.

## 🍕 Features

- **Store Locator**: Find nearest Domino's stores by address/zip code
- **Menu Browsing**: Search for pizzas, wings, sides, and more
- **Order Management**: Add items to cart and calculate totals
- **Customer Info**: Handle delivery addresses and contact information  
- **Safe Preview**: Prepare orders without placing them (safety first!)

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
npm install

# Start development server
npm start
```

Your MCP server will be running at `http://localhost:8787/sse`

### Deploy to Cloudflare

```bash
# Deploy to Cloudflare Workers
npm run deploy
```

After deployment, your server will be available at: `mcpizza-cloudflare.<your-account>.workers.dev/sse`

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

Test with the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector@latest
```

Then connect to `http://localhost:8787/sse` and try:

1. **Find a store**: `find_dominos_store` with address "95608"
2. **Search menu**: `search_menu` with query "pepperoni pizza"
3. **Add to order**: `add_to_order` with item_code "M_PEPPERONI"
4. **View order**: `view_order` to see your cart
5. **Calculate total**: `calculate_order_total` for pricing

## 🔧 Connect to Claude Desktop

Update your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "mcpizza": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "http://localhost:8787/sse"
      ]
    }
  }
}
```

Or use your deployed URL:
```json
{
  "mcpServers": {
    "mcpizza": {
      "command": "npx",
      "args": [
        "mcp-remote", 
        "https://mcpizza-cloudflare.your-account.workers.dev/sse"
      ]
    }
  }
}
```

## 🌐 Connect to Cloudflare AI Playground

1. Go to https://playground.ai.cloudflare.com/
2. Enter your deployed MCP server URL
3. Start ordering pizza with AI assistance!

## ⚠️ Safety & Disclaimers

- **Real order placement is DISABLED by default** for safety
- Uses mock data for demonstration purposes
- All order functionality works except final placement step
- Use responsibly and in accordance with Domino's terms of service

## 🛠 Development

The main server logic is in [`src/index.ts`](src/index.ts). To add new tools:

1. Add your tool definition in the `init()` method
2. Use `this.server.tool(...)` to define the tool
3. Implement the tool logic in the PizzaOrderManager class

---

Built with ❤️ for the MCP ecosystem using Cloudflare Workers
