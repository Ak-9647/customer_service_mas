import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all customer support agents"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.conversation_history = []
        self.user_context = {}
        self.instance_id = str(uuid.uuid4())[:8]
        self.created_at = datetime.now()
        
        logger.info(f"🆔 Created {self.__class__.__name__} instance: {self.instance_id}")
    
    def add_to_history(self, message: str, response: str):
        """Add interaction to conversation history"""
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "response": response,
            "agent": self.name
        })
        
        # Keep only last 10 interactions to manage memory
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    def update_context(self, key: str, value: Any):
        """Update user context information"""
        self.user_context[key] = value
        logger.debug(f"Updated context for {self.instance_id}: {key} = {value}")
    
    def get_context(self, key: str, default=None):
        """Get user context information"""
        return self.user_context.get(key, default)
    
    @abstractmethod
    def can_handle(self, message: str) -> bool:
        """Check if this agent can handle the given message"""
        pass
    
    @abstractmethod
    def process_message(self, message: str) -> Dict[str, Any]:
        """Process the message and return response data"""
        pass
    
    def run(self, message: str) -> str:
        """Main entry point for processing messages"""
        try:
            if not self.can_handle(message):
                return self._get_fallback_response(message)
            
            result = self.process_message(message)
            response = self._format_response(result)
            
            # Add to history
            self.add_to_history(message, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in {self.name}: {e}")
            return f"I apologize, but I encountered an error while processing your request. Please try again or contact support."
    
    def _format_response(self, result: Dict[str, Any]) -> str:
        """Format the response data into a user-friendly string"""
        if "error" in result:
            return f"❌ {result['error']}"
        
        if "message" in result:
            return result["message"]
        
        return str(result)
    
    def _get_fallback_response(self, message: str) -> str:
        """Default response when agent cannot handle the message"""
        return f"I'm {self.name}, but I'm not sure how to help with that specific request. Let me transfer you to our general support."
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status information"""
        return {
            "name": self.name,
            "instance_id": self.instance_id,
            "created_at": self.created_at.isoformat(),
            "interactions_count": len(self.conversation_history),
            "context_keys": list(self.user_context.keys())
        } 