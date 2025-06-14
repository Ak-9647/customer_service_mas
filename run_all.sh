#!/bin/bash

# Create the network if it doesn't exist
docker network inspect agent-net >/dev/null 2>&1 || docker network create agent-net

# Build the image
docker build -t adk-app .

echo "\nStarting MCP server..."
docker run --rm --name mcp-server --network agent-net -p 5002:5002 --env-file .env adk-app python servers/database_mcp_server.py &
sleep 3

echo "\nStarting A2A agent server..."
docker run --rm --name a2a-server --network agent-net -p 5001:5001 --env-file .env adk-app python servers/order_inquiry_a2a_server.py &
sleep 3

echo "\nStarting main ADK app..."
docker run --rm --name adk-main-app --network agent-net -p 8080:8080 --env-file .env adk-app 