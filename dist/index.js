#!/usr/bin/env node

/**
 * MCPizza - MCP Server Wrapper
 * Proxies requests to the deployed Vercel endpoint
 */

const https = require('https');
const http = require('http');

const VERCEL_ENDPOINT = 'https://mcpizza.vercel.app/api/mcp-http';

// Simple HTTP proxy to Vercel endpoint
function proxyRequest(data) {
  return new Promise((resolve, reject) => {
    const options = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data)
      }
    };

    const req = https.request(VERCEL_ENDPOINT, options, (res) => {
      let responseData = '';
      
      res.on('data', (chunk) => {
        responseData += chunk;
      });
      
      res.on('end', () => {
        try {
          resolve(JSON.parse(responseData));
        } catch (e) {
          reject(new Error(`Invalid JSON response: ${responseData}`));
        }
      });
    });

    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

// Handle stdio communication
process.stdin.on('data', async (data) => {
  try {
    const request = JSON.parse(data.toString().trim());
    const response = await proxyRequest(JSON.stringify(request));
    process.stdout.write(JSON.stringify(response) + '\n');
  } catch (error) {
    const errorResponse = {
      jsonrpc: '2.0',
      id: null,
      error: {
        code: -32603,
        message: error.message
      }
    };
    process.stdout.write(JSON.stringify(errorResponse) + '\n');
  }
});

// Keep process alive
process.stdin.resume();

console.error('MCPizza MCP Server started - proxying to Vercel endpoint');
