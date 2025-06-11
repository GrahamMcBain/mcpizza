# 🍕 MCPizza - Global Installation Guide

**Order Domino's pizza directly from your AI assistant!**

MCPizza is a Model Context Protocol (MCP) server that enables AI assistants like Claude to search for pizza, browse menus, and help you place orders through the Domino's API.

## 🚀 Quick Setup

### For Claude Desktop Users

1. **Open Claude Desktop Settings**
   - Click the gear icon in Claude Desktop
   - Navigate to the "Developer" tab
   - Find the "Edit Config" button

2. **Add MCPizza Server Configuration**
   
   Add this to your `claude_desktop_config.json`:

   ```json
   {
     "mcpServers": {
       "mcpizza": {
         "command": "npx",
         "args": [
           "@modelcontextprotocol/server-fetch",
           "https://mcpizza.vercel.app/api/mcp"
         ]
       }
     }
   }
   ```

3. **Restart Claude Desktop**
   
   Close and reopen Claude Desktop to load the new server.

4. **Test It Out!**
   
   Try asking Claude: *"Can you help me order a pizza? I'm in zip code 10001"*

## 🛠 Alternative Installation Methods

### Method 1: Direct HTTP MCP Client
```json
{
  "mcpServers": {
    "mcpizza": {
      "command": "curl",
      "args": [
        "-X", "POST",
        "-H", "Content-Type: application/json",
        "https://mcpizza.vercel.app/api/mcp"
      ]
    }
  }
}
```

### Method 2: Local Clone + Remote API
```bash
# Clone the repository
git clone https://github.com/GrahamMcBain/mcpizza.git
cd mcpizza

# Configure for remote API
export MCPIZZA_REMOTE_URL="https://mcpizza.vercel.app/api/mcp"
```

Then add to your MCP client config:
```json
{
  "mcpServers": {
    "mcpizza": {
      "command": "python",
      "args": ["mcpizza/client_wrapper.py"],
      "env": {
        "MCPIZZA_REMOTE_URL": "https://mcpizza.vercel.app/api/mcp"
      }
    }
  }
}
```

## 🍕 Available Commands

Once installed, your AI assistant can help you:

- **Find Stores**: `"Find the nearest Domino's to zip code 12345"`
- **Browse Menu**: `"What pizzas are available?"`
- **Search Items**: `"Show me pepperoni pizza options"`
- **Build Orders**: `"Add a large pepperoni pizza to my order"`
- **View Cart**: `"What's in my current order?"`

## 🔧 Features

- ✅ **Real-time Domino's Data** - Live menu and store information
- ✅ **Fallback Safety** - Mock data if API is unavailable  
- ✅ **No Setup Required** - Works immediately after config
- ✅ **Privacy Focused** - No data stored, stateless operation
- ✅ **Fast Response** - Serverless deployment for quick access

## 🌍 Server Information

- **Hosted on**: Vercel (Serverless)
- **API Endpoint**: https://mcpizza.vercel.app/api/mcp
- **Real API**: Enabled with fallback to mock data
- **Rate Limits**: Subject to Vercel's limits
- **Uptime**: 99.9% expected (Vercel SLA)

## ⚠️ Important Notes

### Order Placement
- **ORDERING IS DISABLED** for safety - this server helps you browse and prepare orders only
- You'll need to complete actual purchases through official Domino's channels
- Customer data is not stored or transmitted for security

### API Usage
- Uses the unofficial `pizzapi` library for educational purposes
- Real store and menu data when available
- Respects Domino's terms of service
- Falls back to demo data if API is unavailable

## 🐛 Troubleshooting

### Server Not Responding
- Check if the Vercel endpoint is accessible: https://mcpizza.vercel.app/api/mcp
- Verify your MCP client configuration syntax
- Restart your MCP client (Claude Desktop, etc.)

### No Real Data
- The server may be in fallback mode using mock data
- This is normal if Domino's API is temporarily unavailable
- All functionality still works with demo data

### Configuration Issues
- Ensure your `claude_desktop_config.json` has valid JSON syntax
- Check that the server name "mcpizza" is unique in your config
- Verify the API endpoint URL is correct

## 📞 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/GrahamMcBain/mcpizza/issues)
- **Server Status**: Check https://mcpizza.vercel.app/api/mcp for server health
- **MCP Documentation**: [Model Context Protocol Docs](https://modelcontextprotocol.io/)

## 🎉 Example Usage

After installation, try these with your AI assistant:

```
"I want to order pizza. I'm at 123 Main St, New York, NY 10001"
"What pizza deals are available right now?"
"Add a large pepperoni pizza and an order of wings to my cart"
"How much will my order cost with delivery?"
```

---

**Built with ❤️ for the MCP community**

*MCPizza makes AI-assisted pizza ordering simple, safe, and fun!*
