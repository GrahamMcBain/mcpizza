#!/usr/bin/env node

/**
 * MCPizza - MCP Server
 * Proxies to Vercel backend for pizza ordering functionality
 */

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const fetch = require('node-fetch');

const VERCEL_ENDPOINT = 'https://mcpizza.vercel.app/api/mcp';

class MCPizzaServer {
  constructor() {
    this.server = new Server(
      {
        name: 'MCPizza',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupHandlers();
  }

  setupHandlers() {
    // List available tools
    this.server.setRequestHandler('tools/list', async () => {
      return {
        tools: [
          {
            name: 'find_dominos_store',
            description: 'Find the nearest Domino\'s store by address or zip code',
            inputSchema: {
              type: 'object',
              properties: {
                address: {
                  type: 'string',
                  description: 'Full address or zip code to search near'
                }
              },
              required: ['address']
            }
          },
          {
            name: 'search_menu',
            description: 'Search for menu items by name or description',
            inputSchema: {
              type: 'object',
              properties: {
                query: {
                  type: 'string',
                  description: 'Search term (e.g., "pepperoni pizza", "wings")'
                }
              },
              required: ['query']
            }
          },
          {
            name: 'add_to_order',
            description: 'Add items to pizza order',
            inputSchema: {
              type: 'object',
              properties: {
                item_code: {
                  type: 'string',
                  description: 'Product code from menu search'
                },
                quantity: {
                  type: 'integer',
                  description: 'Number of items to add',
                  default: 1
                }
              },
              required: ['item_code']
            }
          },
          {
            name: 'view_order',
            description: 'View current order contents and total',
            inputSchema: {
              type: 'object',
              properties: {},
              required: []
            }
          }
        ]
      };
    });

    // Handle tool calls
    this.server.setRequestHandler('tools/call', async (request) => {
      const { name, arguments: args } = request.params;

      try {
        // Proxy the request to our Vercel backend
        const response = await fetch(VERCEL_ENDPOINT, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            jsonrpc: '2.0',
            id: 1,
            method: 'tools/call',
            params: {
              name,
              arguments: args
            }
          })
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.error) {
          throw new Error(data.error.message);
        }

        return data.result;

      } catch (error) {
        return {
          content: [
            {
              type: 'text',
              text: `Error: ${error.message}`
            }
          ]
        };
      }
    });
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('MCPizza MCP Server running...');
  }
}

// Start the server
const server = new MCPizzaServer();
server.run().catch(console.error);
