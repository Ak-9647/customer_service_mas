import logging
import re
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
from .order_agent import OrderAgent
from .refund_agent import RefundAgent
from .support_agent import GeneralSupportAgent

logger = logging.getLogger(__name__)

class CoordinatorAgent(BaseAgent):
    """Coordinator agent that routes messages to appropriate specialized agents"""
    
    def __init__(self):
        super().__init__(
            name="CoordinatorAgent",
            description="Routes customer inquiries to the most appropriate specialized agent"
        )
        
        # Initialize specialized agents
        self.order_agent = OrderAgent()
        self.refund_agent = RefundAgent()
        self.support_agent = GeneralSupportAgent()
        
        # Agent priority order (higher priority agents checked first)
        self.agents = [
            self.refund_agent,  # Check refunds first (more specific)
            self.order_agent,   # Then orders
            self.support_agent  # General support as fallback
        ]
        
        logger.info(f"🎯 Coordinator agent initialized with {len(self.agents)} specialized agents")
    
    def can_handle(self, message: str) -> bool:
        """Coordinator can handle any message by routing it"""
        return True
    
    def process_message(self, message: str) -> Dict[str, Any]:
        """Route message to the most appropriate agent"""
        message_lower = message.lower().strip()
        
        # Log the routing decision
        logger.info(f"🎯 Routing message: {message[:50]}...")
        
        # Check for context-based routing (follow-up questions)
        context_agent = self._check_context_routing(message)
        if context_agent:
            logger.info(f"🎯 Using context-based routing to: {context_agent.name}")
            result = context_agent.process_message(message)
            
            # Handle both string and dict responses
            if isinstance(result, str):
                result = {"message": result}
            
            result["routed_to"] = context_agent.name
            result["routing_reason"] = "context"
            self._update_conversation_context(message, result)
            return result
        
        # Advanced intent detection with confidence scoring
        intent_scores = self._calculate_intent_scores(message)
        
        # Find the best agent based on intent scores
        best_agent = self._select_best_agent(message, intent_scores)
        
        if best_agent:
            logger.info(f"🎯 Selected agent: {best_agent.name}")
            
            # Process with selected agent
            result = best_agent.process_message(message)
            
            # Handle both string and dict responses
            if isinstance(result, str):
                result = {"message": result}
            
            # Add routing metadata
            result["routed_to"] = best_agent.name
            result["routing_confidence"] = intent_scores.get(best_agent.__class__.__name__, 0)
            result["routing_reason"] = "intent_scoring"
            
            # Update conversation context
            self._update_conversation_context(message, result)
            
            return result
        
        # Fallback if no agent can handle it
        return self._handle_unroutable_message(message)
    
    def _check_context_routing(self, message: str) -> Optional[Any]:
        """Check if message should be routed based on conversation context"""
        message_lower = message.lower().strip()
        
        # Check recent conversation history for context
        if len(self.conversation_history) >= 1:
            last_entry = self.conversation_history[-1]
            last_response = last_entry.get('response', '').lower() if isinstance(last_entry, dict) else ''
            
            # If we just asked for order number and user provides digits
            if ('order number' in last_response or 'provide your order' in last_response) and re.search(r'\b\d{4,6}\b', message):
                # Check if it was in refund context
                if 'refund' in last_response:
                    logger.info(f"🎯 Context routing: Order ID provided after refund request - routing to RefundAgent")
                    return self.refund_agent
                else:
                    logger.info(f"🎯 Context routing: Order ID provided after request - routing to OrderAgent")
                    return self.order_agent
            
            # Check if previous message was about refunds and current message has order ID
            if len(self.conversation_history) >= 2:
                prev_entry = self.conversation_history[-2]
                prev_message = prev_entry.get('message', '').lower() if isinstance(prev_entry, dict) else ''
                if any(keyword in prev_message for keyword in ['refund', 'return', 'money back']) and re.search(r'\b\d{4,6}\b', message):
                    logger.info(f"🎯 Context routing: Order ID provided in refund context - routing to RefundAgent")
                    return self.refund_agent
        
        return None
    
    def _update_conversation_context(self, message: str, result: Dict[str, Any]):
        """Update conversation context for better routing"""
        # Add to conversation history for context routing
        self.add_to_history(message, result.get("message", ""))
        
        # Update context for other uses
        self.update_context("last_agent_used", result.get("routed_to"))
        self.update_context("last_category", result.get("category"))
        self.update_context("last_message", message)
        self.update_context("last_response", result.get("message", "")[:100])
    
    def _calculate_intent_scores(self, message: str) -> Dict[str, float]:
        """Calculate confidence scores for each agent's ability to handle the message"""
        message_lower = message.lower().strip()
        scores = {}
        
        # Refund intent scoring (most specific, highest priority)
        refund_score = 0
        refund_keywords = [
            'refund', 'return', 'money back', 'cancel order', 'get my money',
            'charge back', 'dispute', 'unsatisfied', 'not happy', 'want to return'
        ]
        
        for keyword in refund_keywords:
            if keyword in message_lower:
                refund_score += 2  # High weight for refund keywords
        
        # Boost score if there's an order ID with refund context
        if re.search(r'\b(refund|return|cancel)\s+(?:order\s+)?(\d{4,6})\b', message_lower):
            refund_score += 3
        
        scores["RefundAgent"] = refund_score
        
        # Order intent scoring
        order_score = 0
        order_keywords = [
            'order', 'status', 'track', 'tracking', 'shipped', 'delivery',
            'where is', 'when will', 'arrive', 'delivered', 'package'
        ]
        
        for keyword in order_keywords:
            if keyword in message_lower:
                order_score += 1.5  # Medium weight for order keywords
        
        # Boost score if there's an order ID pattern
        if re.search(r'\b(check|status|track)\s+(?:order\s+)?(\d{4,6})\b', message_lower):
            order_score += 2
        
        # If both refund and order patterns match, prioritize refund
        if refund_score > 0 and order_score > 0:
            refund_score += 1  # Boost refund priority
        
        scores["OrderAgent"] = order_score
        
        # General support scoring (catches everything else)
        support_score = 1  # Base score for general support
        
        # Check for specific support categories
        support_categories = {
            "shipping": ["shipping", "delivery", "ship", "when will", "arrive", "tracking", "fedex", "ups", "usps"],
            "returns": ["return policy", "exchange", "send back"],
            "payment": ["payment", "charge", "billing", "credit card", "paypal", "apple pay", "payment methods"],
            "account": ["account", "login", "password", "profile", "email", "update", "change"],
            "contact": ["contact", "phone", "email", "speak to", "human", "representative", "hours"],
            "product": ["product", "item", "quality", "size", "color", "material", "specifications"]
        }
        
        # Score specific support categories higher
        for category, keywords in support_categories.items():
            for keyword in keywords:
                if keyword in message_lower:
                    support_score += 2  # High score for specific support topics
                    break
        
        # Handle greetings
        greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
        if any(greeting in message_lower for greeting in greetings):
            # Only boost greeting score if no specific support category matched
            if support_score <= 1:  # No specific category matched
                support_score += 2
        
        # General keywords get lower score
        general_keywords = ["help", "support", "question", "info"]
        for keyword in general_keywords:
            if keyword in message_lower:
                support_score += 0.5  # Lower weight for general keywords
        
        scores["GeneralSupportAgent"] = support_score
        
        logger.info(f"🎯 Intent scores: {scores}")
        return scores
    
    def _select_best_agent(self, message: str, intent_scores: Dict[str, float]) -> BaseAgent:
        """Select the best agent based on intent scores and agent capabilities"""
        
        # Find the agent with the highest score
        best_score = 0
        best_agent = None
        
        for agent in self.agents:
            agent_name = agent.__class__.__name__
            score = intent_scores.get(agent_name, 0)
            
            # Also check if the agent can handle the message
            if agent.can_handle(message) and score > best_score:
                best_score = score
                best_agent = agent
        
        # If no agent has a good score, use general support as fallback
        if not best_agent or best_score < 1:
            best_agent = self.support_agent
        
        return best_agent
    
    def _handle_unroutable_message(self, message: str) -> Dict[str, Any]:
        """Handle messages that can't be routed to any specific agent"""
        return {
            "message": """🤔 I'm not sure how to help with that specific request. 

Let me connect you with our general support team, or you can try rephrasing your question.

Common things I can help with:
• Order status and tracking
• Refunds and returns
• Shipping information
• General customer support

What would you like help with?""",
            "routed_to": "Unroutable",
            "suggestions": [
                "Check order status",
                "Request a refund",
                "Shipping information",
                "General help"
            ]
        }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            "coordinator": self.get_status(),
            "agents": {
                agent.__class__.__name__: agent.get_status()
                for agent in self.agents
            }
        }
    
    def get_routing_history(self) -> List[Dict[str, Any]]:
        """Get history of routing decisions"""
        return [
            {
                "message": interaction["message"][:50] + "...",
                "agent": interaction.get("routed_to", "Unknown"),
                "timestamp": interaction["timestamp"]
            }
            for interaction in self.conversation_history[-10:]  # Last 10 interactions
        ]
    
    def force_route_to_agent(self, message: str, agent_name: str) -> Dict[str, Any]:
        """Force routing to a specific agent (for testing/debugging)"""
        agent_map = {
            "order": self.order_agent,
            "refund": self.refund_agent,
            "support": self.support_agent
        }
        
        agent = agent_map.get(agent_name.lower())
        if not agent:
            return {"error": f"Unknown agent: {agent_name}"}
        
        logger.info(f"🎯 Force routing to {agent.name}")
        result = agent.process_message(message)
        result["routed_to"] = agent.name
        result["forced_routing"] = True
        
        return result
    
    def _get_fallback_response(self, message: str) -> str:
        """Coordinator fallback (should rarely be used)"""
        return "I'm the coordinator agent. Let me route your message to the appropriate specialist." 