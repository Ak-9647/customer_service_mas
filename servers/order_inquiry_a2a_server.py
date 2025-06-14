from langchain.tools import tool
from langchain.agents import AgentExecutor
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from python_a2a import to_a2a_server
import requests
import os

@tool
def remote_lookup_order(order_id: int) -> dict:
    """Looks up an order by ID using the remote MCP server."""
    url = "http://localhost:5002/rpc"
    payload = {
        "method": "lookup_order",
        "params": {"order_id": order_id}
    }
    response = requests.post(url, json=payload)
    try:
        return response.json()
    except Exception:
        return {"error": "Invalid response from MCP server"}

llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful order inquiry assistant."),
    ("human", "{input}")
])

agent_executor = AgentExecutor(
    tools=[remote_lookup_order],
    llm=llm,
    prompt=prompt
)

a2a_server = to_a2a_server(agent_executor)

if __name__ == "__main__":
    a2a_server.run(port=5001)
