#!/bin/bash
echo "🛑 Deteniendo Calculator MCP Server..."

if [ "$(docker ps -q -f name=calculator-mcp-server)" ]; then
    docker stop calculator-mcp-server
    docker rm calculator-mcp-server
    echo "✅ Calculator MCP Server detenido"
else
    echo "ℹ️  El servidor no está corriendo"
fi