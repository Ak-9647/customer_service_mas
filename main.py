import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, Union
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import agents after environment is loaded
try:
    from agents.customer_support_agents import root_agent as coordinator_agent
    logger.info("✅ Multi-agent coordinator loaded successfully")
    logger.info(f"🎯 Agent type: {type(coordinator_agent).__name__}")
    if hasattr(coordinator_agent, 'agents'):
        logger.info(f"🤖 Specialized agents: {len(coordinator_agent.agents)}")
except Exception as e:
    logger.error(f"❌ Failed to load coordinator agent: {e}")
    coordinator_agent = None

# Create FastAPI app
app = FastAPI(
    title="ADK Agent API",
    description="Multi-layer agent architecture with ADK",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class MessagePart(BaseModel):
    text: str

class Message(BaseModel):
    parts: list[MessagePart]
    role: str = "user"

class RunRequest(BaseModel):
    appName: str
    userId: str
    sessionId: str
    newMessage: Message

class SimpleMessageRequest(BaseModel):
    message: str

class RunResponse(BaseModel):
    reply: str
    status: str = "success"

class SimpleMessageResponse(BaseModel):
    response: str
    status: str = "success"

# In-memory session storage (replace with real persistence in production)
sessions: Dict[str, Dict[str, Any]] = {}

@app.get("/")
async def root():
    return {
        "message": "ADK Agent API is running",
        "agent_loaded": coordinator_agent is not None,
        "endpoints": ["/run", "/api/run", "/run_sse", "/list-apps", "/health"]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "agent_loaded": coordinator_agent is not None,
        "environment": {
            "openai_key_set": bool(os.getenv("OPENAI_API_KEY")),
            "google_key_set": bool(os.getenv("GOOGLE_API_KEY"))
        }
    }

@app.get("/list-apps")
async def list_apps():
    return {
        "apps": ["agents"],
        "description": "Available ADK applications"
    }

@app.post("/apps/agents/users/{user_id}/sessions/{session_id}")
async def create_session(user_id: str, session_id: str):
    """Create or initialize a session"""
    session_key = f"{user_id}:{session_id}"
    if session_key not in sessions:
        sessions[session_key] = {
            "user_id": user_id,
            "session_id": session_id,
            "messages": [],
            "created_at": "2024-01-01T00:00:00Z"
        }
        logger.info(f"Created new session: {session_key}")
    return {"status": "created", "session_id": session_id}

# Enhanced simple API endpoint for the modern frontend
@app.post("/api/run", response_model=SimpleMessageResponse)
async def run_simple_api(request: SimpleMessageRequest):
    """Enhanced API endpoint for the modern frontend with sophisticated agent"""
    try:
        if not coordinator_agent:
            raise HTTPException(status_code=500, detail="Agent not loaded")
        
        message_text = request.message.strip()
        if not message_text:
            raise HTTPException(status_code=400, detail="No message text provided")
        
        logger.info(f"🎯 Processing enhanced message: {message_text}")
        logger.info(f"🤖 Agent type: {type(coordinator_agent)}")
        logger.info(f"🤖 Agent methods: {[method for method in dir(coordinator_agent) if not method.startswith('_')]}")
        
        # Process with sophisticated agent
        try:
            # Use the sophisticated agent's run method
            if hasattr(coordinator_agent, 'run'):
                logger.info("🚀 Using agent.run() method")
                result = coordinator_agent.run(message_text)
            elif hasattr(coordinator_agent, 'invoke'):
                logger.info("🚀 Using agent.invoke() method")
                result = coordinator_agent.invoke({"input": message_text})
            elif hasattr(coordinator_agent, '__call__'):
                logger.info("🚀 Using agent.__call__() method")
                result = coordinator_agent(message_text)
            else:
                logger.warning("🚀 No suitable agent method found, using fallback")
                result = f"Agent received: {message_text}"
            
            # Handle different result types
            if isinstance(result, dict):
                reply = result.get('output', result.get('response', str(result)))
            elif isinstance(result, str):
                reply = result
            else:
                reply = str(result)
                
        except Exception as agent_error:
            logger.error(f"❌ Agent processing error: {agent_error}")
            reply = f"I apologize, but I encountered an error processing your request. Please try again or contact our support team for assistance."
        
        logger.info(f"✅ Enhanced agent response: {reply[:100]}...")
        return SimpleMessageResponse(response=reply)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in run_simple_api: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/run", response_model=RunResponse)
async def run_agent(request: RunRequest):
    """Run the agent with a message (original ADK format)"""
    try:
        if not coordinator_agent:
            raise HTTPException(status_code=500, detail="Agent not loaded")
        
        # Extract message text
        message_text = ""
        if request.newMessage.parts:
            message_text = request.newMessage.parts[0].text
        
        if not message_text:
            raise HTTPException(status_code=400, detail="No message text provided")
        
        logger.info(f"Processing message: {message_text}")
        
        # Store session
        session_key = f"{request.userId}:{request.sessionId}"
        if session_key not in sessions:
            sessions[session_key] = {
                "user_id": request.userId,
                "session_id": request.sessionId,
                "messages": []
            }
        
        sessions[session_key]["messages"].append({
            "role": "user",
            "text": message_text
        })
        
        # Process with agent
        try:
            # Use the sophisticated agent's run method
            if hasattr(coordinator_agent, 'run'):
                result = coordinator_agent.run(message_text)
            elif hasattr(coordinator_agent, 'run_live'):
                # run_live returns an async generator, we need to collect the results
                response_parts = []
                async for chunk in coordinator_agent.run_live(message_text):
                    if hasattr(chunk, 'text'):
                        response_parts.append(chunk.text)
                    elif isinstance(chunk, str):
                        response_parts.append(chunk)
                    else:
                        response_parts.append(str(chunk))
                result = ''.join(response_parts) if response_parts else "No response from agent"
            elif hasattr(coordinator_agent, 'invoke'):
                result = coordinator_agent.invoke({"input": message_text})
            elif hasattr(coordinator_agent, '__call__'):
                result = coordinator_agent(message_text)
            else:
                # Fallback - try to get a response
                result = f"Agent received: {message_text}"
            
            # Handle different result types
            if isinstance(result, dict):
                reply = result.get('output', result.get('response', str(result)))
            elif isinstance(result, str):
                reply = result
            else:
                reply = str(result)
                
        except Exception as agent_error:
            logger.error(f"Agent processing error: {agent_error}")
            reply = f"I apologize, but I encountered an error processing your request: {str(agent_error)}"
        
        # Store agent response
        sessions[session_key]["messages"].append({
            "role": "assistant", 
            "text": reply
        })
        
        logger.info(f"Agent response: {reply}")
        return RunResponse(reply=reply)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in run_agent: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/run_sse")
async def run_agent_sse(request: RunRequest):
    """Run agent with Server-Sent Events (placeholder)"""
    # For now, just return the same as /run
    return await run_agent(request)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🚀 Starting Enhanced ADK Agent API on {host}:{port}")
    logger.info(f"🔑 OpenAI API Key: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Not set'}")
    logger.info(f"🔑 Google API Key: {'✅ Set' if os.getenv('GOOGLE_API_KEY') else '❌ Not set'}")
    
    uvicorn.run(app, host=host, port=port)
