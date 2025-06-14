"""
Refund Agent - Handles refund requests, processing, and refund-related inquiries
Enhanced with comprehensive database integration and business logic
"""

import re
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from .base_agent import BaseAgent
from persistence.database import enhanced_db
from persistence.memory_manager import log_refund_request, complete_refund

logger = logging.getLogger(__name__)

class RefundAgent(BaseAgent):
    """Specialized agent for handling refund requests and processing"""
    
    def __init__(self):
        super().__init__(
            name="RefundAgent",
            description="Handles refund requests, processing, and refund-related inquiries"
        )
        self.refund_patterns = [
            r'\brefund\s+(?:order\s+)?(\d{4,6})\b',
            r'\breturn\s+(?:order\s+)?(\d{4,6})\b',
            r'\bcancel\s+(?:order\s+)?(\d{4,6})\b',
            r'\b(\d{4,6})\s+refund\b'
        ]
        
        # Business rules for refunds
        self.refund_window_days = 30
        self.processing_fee = 2.99
        self.processing_fee_threshold = 50.00
    
    def can_handle(self, message: str) -> bool:
        """Check if this message is about refunds"""
        message_lower = message.lower().strip()
        
        # Refund-related keywords
        refund_keywords = [
            'refund', 'return', 'money back', 'cancel order', 'get my money',
            'charge back', 'dispute', 'unsatisfied', 'not happy', 'want to return',
            'return policy', 'refund policy', 'how to return', 'send back'
        ]
        
        # Check for refund keywords
        has_refund_keyword = any(keyword in message_lower for keyword in refund_keywords)
        
        # Check for order ID with refund context
        has_refund_order_pattern = bool(re.search(r'\b(refund|return|cancel)\s+(?:order\s+)?(\d{4,6})\b', message_lower))
        
        # Check for policy questions
        has_policy_question = any(pattern in message_lower for pattern in [
            'refund policy', 'return policy', 'how to refund', 'can i return'
        ])
        
        return has_refund_keyword or has_refund_order_pattern or has_policy_question
    
    def process_message(self, message: str) -> str:
        """Process refund-related messages"""
        message_lower = message.lower().strip()
        
        # Check if this is just an order ID (common after asking for order number)
        order_id_match = re.match(r'^\s*(\d{4,6})\s*$', message)
        if order_id_match:
            order_id = int(order_id_match.group(1))
            logger.info(f"🔍 Processing order ID {order_id} for refund...")
            return self._process_refund_request(order_id, "Customer request")
        
        # Extract order ID from message
        order_id = self._extract_order_id(message)
        
        if order_id:
            # Determine refund reason from message
            reason = self._extract_refund_reason(message)
            logger.info(f"💰 Processing refund request for order {order_id}...")
            return self._process_refund_request(order_id, reason)
        
        # Handle general refund policy questions
        if any(keyword in message_lower for keyword in ['policy', 'how', 'what', 'when', 'process']):
            return self._get_refund_policy()
        
        # If no order ID found, ask for it
        return self._ask_for_order_details()
    
    def _handle_policy_question(self, message: str) -> Dict[str, Any]:
        """Handle refund policy questions"""
        return {
            "message": """📋 **Comprehensive Refund & Return Policy:**

✅ **Eligibility Requirements:**
   • Items must be returned within 30 days of delivery
   • Items must be in original condition and packaging
   • Digital products are non-refundable
   • Custom/personalized items are non-refundable

💰 **Refund Details:**
   • Processing fee: $2.99 for orders over $50
   • Refunds processed to original payment method
   • Processing time: 3-5 business days
   • Shipping costs are non-refundable (unless item defective)

🔄 **Return Process:**
   1. Request refund with order number
   2. Receive return authorization and label
   3. Package and ship item back
   4. Refund processed upon receipt

❓ **Need to start a refund?** Just provide your order number and I'll help you immediately!""",
            "category": "refund_policy_detailed",
            "agent": self.name
        }
    
    def _extract_order_id(self, message: str) -> int:
        """Extract order ID from refund-related message"""
        # Try refund-specific patterns first
        for pattern in self.refund_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except (ValueError, IndexError):
                    continue
        
        # Fallback to general order ID pattern
        general_pattern = r'\b(\d{4,6})\b'
        matches = re.findall(general_pattern, message)
        if matches:
            try:
                return int(matches[0])
            except ValueError:
                pass
        
        return None
    
    def _extract_refund_reason(self, message: str) -> str:
        """Extract refund reason from message"""
        message_lower = message.lower()
        
        # Common refund reasons
        if any(word in message_lower for word in ['defective', 'broken', 'damaged', 'faulty']):
            return "Product defective/damaged"
        elif any(word in message_lower for word in ['wrong', 'incorrect', 'mistake']):
            return "Wrong item received"
        elif any(word in message_lower for word in ['late', 'delayed', 'slow']):
            return "Late delivery"
        elif any(word in message_lower for word in ['changed mind', 'don\'t want', 'no longer need']):
            return "Changed mind"
        else:
            return "Customer request"
    
    def _process_refund_request(self, order_id: int, reason: str) -> str:
        """Process refund request and return string response"""
        logger.info(f"🔍 Looking up order {order_id}...")
        
        # Get order from enhanced database
        order_data = enhanced_db.get_order(order_id)
        
        if not order_data:
            return f"❌ I couldn't find order #{order_id}. Please check the order number and try again."
        
        # Check refund eligibility
        eligibility_check = self._check_refund_eligibility(order_data)
        
        if not eligibility_check["eligible"]:
            return eligibility_check["message"]
        
        # Process the refund
        refund_result = self._process_refund(order_data, reason)
        return refund_result["message"]
    
    def _check_refund_eligibility(self, order_data: Dict) -> Dict[str, Any]:
        """Check if order is eligible for refund"""
        order_status = order_data["status"].lower()
        order_date = datetime.strptime(order_data["order_date"], "%Y-%m-%d")
        days_since_order = (datetime.now() - order_date).days
        
        # Check order status
        if order_status == "cancelled":
            return {
                "eligible": False,
                "reason": "already_cancelled",
                "message": f"❌ Order {order_data['order_id']} has already been cancelled. If you need assistance, please contact our support team."
            }
        
        if order_status == "pending":
            return {
                "eligible": True,
                "reason": "pending_cancellation",
                "message": "✅ Order is still pending and can be cancelled."
            }
        
        if order_status == "processing":
            return {
                "eligible": False,
                "reason": "processing",
                "message": f"❌ Order {order_data['order_id']} is still being processed. Please wait for shipment before requesting a refund, or contact support to cancel the order."
            }
        
        # Check refund window for shipped/delivered orders
        if order_status in ["shipped", "delivered"]:
            if days_since_order > self.refund_window_days:
                return {
                    "eligible": False,
                    "reason": "outside_window",
                    "message": f"❌ Order {order_data['order_id']} was placed {days_since_order} days ago, which is outside our {self.refund_window_days}-day refund window. Please contact our support team for special consideration."
                }
        
        return {
            "eligible": True,
            "reason": "eligible",
            "message": "✅ Order is eligible for refund."
        }
    
    def _process_refund(self, order_data: Dict, reason: str) -> Dict[str, Any]:
        """Process the refund with comprehensive logging"""
        logger.info(f"💰 Processing refund request for order {order_data['order_id']}...")
        
        # Calculate refund amounts
        original_amount = order_data["total"]
        processing_fee = self.processing_fee if original_amount > self.processing_fee_threshold else 0.00
        refund_amount = original_amount - processing_fee
        
        # Generate transaction IDs
        log_id = str(uuid.uuid4())
        transaction_id = str(uuid.uuid4())
        
        try:
            # Log refund initiation
            log_refund_request(
                log_id=log_id,
                order_id=order_data["order_id"],
                reason=reason,
                priority="standard",
                estimated_amount=original_amount
            )
            
            # Complete refund processing
            complete_refund(
                log_id=log_id,
                transaction_id=transaction_id,
                processing_time_seconds=96,  # Simulated processing time
                refund_method="Original payment method"
            )
            
            # Format success response
            response = f"""✅ **Refund Processed Successfully!**

🆔 **Order ID:** {order_data['order_id']}
💰 **Original Amount:** ${original_amount:.2f}
💸 **Refund Amount:** ${refund_amount:.2f}
💳 **Processing Fee:** ${processing_fee:.2f}
🔄 **Transaction ID:** {transaction_id}

📋 **Refund Details:**
   • **Reason:** {reason}
   • **Method:** Original payment method ({order_data['payment_method']})
   • **Processing Time:** 3-5 business days
   • **Status:** Completed

📧 **Next Steps:**
   • You'll receive a confirmation email shortly
   • Refund will appear on your statement within 3-5 business days
   • Keep this transaction ID for your records

🤝 **Thank you for your business!** If you have any questions about this refund, please reference transaction ID {transaction_id}."""
            
            return {
                "message": response,
                "category": "refund_processed",
                "agent": self.name,
                "order_id": order_data["order_id"],
                "transaction_id": transaction_id,
                "refund_amount": refund_amount,
                "processing_fee": processing_fee
            }
            
        except Exception as e:
            logger.error(f"Error processing refund: {e}")
            return {
                "message": f"❌ There was an error processing your refund for order {order_data['order_id']}. Please contact our support team for assistance. Reference: {log_id}",
                "category": "refund_error",
                "agent": self.name,
                "order_id": order_data["order_id"],
                "error": str(e)
            }
    
    def get_refund_status(self, transaction_id: str) -> Dict[str, Any]:
        """Get refund status by transaction ID"""
        # This would query the refund logs in a real implementation
        return {
            "transaction_id": transaction_id,
            "status": "completed",
            "estimated_completion": "3-5 business days"
        }
    
    def _get_fallback_response(self, message: str) -> str:
        """Custom fallback for refund agent"""
        return "I specialize in refunds and returns. Please provide your order number for a refund request, or I can transfer you to general support."
    
    def _get_refund_policy(self) -> str:
        """Return refund policy information"""
        return """📋 **Refund Policy & Process:**

✅ **Eligibility:** Orders can be refunded within 30 days of delivery
⏰ **Processing Time:** 3-5 business days
💳 **Refund Method:** Original payment method
💰 **Processing Fee:** $2.99 for orders over $50

**To request a refund:**
1. Provide your order number
2. Tell me the reason for the refund
3. I'll process it immediately if eligible

What's your order number?"""
    
    def _ask_for_order_details(self) -> str:
        """Ask for order details to process refund"""
        return """📋 **Refund Policy & Process:**

✅ **Eligibility:** Orders can be refunded within 30 days of delivery
⏰ **Processing Time:** 3-5 business days
💳 **Refund Method:** Original payment method
💰 **Processing Fee:** $2.99 for orders over $50

**To request a refund:**
1. Provide your order number
2. Tell me the reason for the refund
3. I'll process it immediately if eligible

What's your order number?""" 