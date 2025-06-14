from python_a2a.mcp import FastMCPServer, mcp_server, text_response
from tools.database_tools import lookup_order_by_id
import json

@mcp_server.tool(name="lookup_order")
def lookup_order_wrapper(order_id: int):
    result = lookup_order_by_id(order_id)
    return text_response(json.dumps(result))

if __name__ == "__main__":
    server = FastMCPServer()
    server.run(port=5002)

