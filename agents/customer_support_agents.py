import logging
from .coordinator_agent import CoordinatorAgent

logger = logging.getLogger(__name__)

# Initialize the multi-agent system
try:
    # Create the coordinator agent which manages all specialized agents
    coordinator_agent = CoordinatorAgent()
    logger.info("✅ Multi-agent customer support system initialized successfully")
    logger.info(f"🎯 Coordinator agent: {coordinator_agent.name}")
    logger.info(f"🤖 Specialized agents: {len(coordinator_agent.agents)}")
    
    # Log agent details
    for agent in coordinator_agent.agents:
        logger.info(f"   - {agent.name}: {agent.description}")
    
except Exception as e:
    logger.error(f"❌ Failed to initialize multi-agent system: {e}")
    
    # Fallback to a simple coordinator if initialization fails
    class FallbackCoordinator:
        def __init__(self):
            self.name = "FallbackCoordinator"
            logger.info("🔄 Using fallback coordinator")
        
        def run(self, message: str) -> str:
            return "I'm currently experiencing technical difficulties. Please try again later or contact support directly."
        
        def invoke(self, input_data: dict) -> dict:
            message = input_data.get("input", "")
            response = self.run(message)
            return {"output": response}
        
        def __call__(self, message: str) -> str:
            return self.run(message)
    
    coordinator_agent = FallbackCoordinator()
    logger.info("✅ Fallback coordinator initialized")

# Export the coordinator agent for use by main.py
root_agent = coordinator_agent

logger.info("✅ Enhanced customer support agents initialized")
