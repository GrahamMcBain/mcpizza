#!/bin/bash

# MCPizza mcptools Testing Script

echo "🍕 MCPizza + mcptools Testing Script"
echo "===================================="

# Check if mcp command is available
if ! command -v mcp &> /dev/null; then
    echo "❌ mcptools not found. Install with:"
    echo "   brew tap f/mcptools && brew install mcp"
    echo "   OR: go install github.com/f/mcptools/cmd/mcptools@latest"
    exit 1
fi

echo "✅ mcptools found"

# Test 1: Mock mode
echo ""
echo "🧪 Test 1: Mock Mode"
echo "-------------------"
echo "mcp tools python mcpizza/production_server.py"
mcp tools python mcpizza/production_server.py

echo ""
echo "🧪 Test 2: Find Store (Mock)"
echo "---------------------------"
echo "mcp call find_dominos_store --params '{\"address\":\"95608\"}' python mcpizza/production_server.py"
mcp call find_dominos_store --params '{"address":"95608"}' python mcpizza/production_server.py

echo ""
echo "🧪 Test 3: Real API Mode"
echo "-----------------------"
echo "MCPIZZA_REAL_API=true mcp call find_dominos_store --params '{\"address\":\"95608\"}' python mcpizza/production_server.py"
MCPIZZA_REAL_API=true mcp call find_dominos_store --params '{"address":"95608"}' python mcpizza/production_server.py

echo ""
echo "🧪 Test 4: Interactive Shell"
echo "---------------------------"
echo "Starting interactive shell (type 'help' for commands)..."
echo "Example commands:"
echo "  > call find_dominos_store {\"address\":\"95608\"}"
echo "  > call search_menu {\"query\":\"pizza\"}"
echo "  > exit"
echo ""
mcp shell python mcpizza/production_server.py
