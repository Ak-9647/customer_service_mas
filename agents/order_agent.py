"""
Order Agent - Handles order lookups, status checks, and order-related inquiries
Enhanced with comprehensive database integration
"""

import re
import logging
from typing import Dict, Any
from .base_agent import BaseAgent
from persistence.database import enhanced_db

logger = logging.getLogger(__name__)

class OrderAgent(BaseAgent):
    """Specialized agent for handling order-related inquiries"""
    
    def __init__(self):
        super().__init__(
            name="OrderAgent",
            description="Handles order lookups, status checks, and order-related inquiries"
        )
        self.order_patterns = [
            r'\border\s*(?:id|number|#)?\s*(\d{4,6})\b',
            r'\b(\d{4,6})\s*order\b',
            r'#(\d{4,6})\b',
            r'\btrack(?:ing)?\s*(?:number|#)?\s*(\d{4,6})\b'
        ]
    
    def can_handle(self, message: str) -> bool:
        """Check if this message is about orders"""
        message_lower = message.lower().strip()
        
        # Order-related keywords
        order_keywords = [
            'order', 'status', 'track', 'tracking', 'shipment', 'delivery',
            'shipped', 'delivered', 'pending', 'processing', 'where is my',
            'when will', 'estimated delivery', 'order number'
        ]
        
        # Check for order keywords
        has_order_keyword = any(keyword in message_lower for keyword in order_keywords)
        
        # Check for order ID patterns
        has_order_id = any(re.search(pattern, message_lower) for pattern in self.order_patterns)
        
        return has_order_keyword or has_order_id
    
    def process_message(self, message: str) -> Dict[str, Any]:
        """Process order-related messages"""
        message_lower = message.lower().strip()
        
        # Extract order ID from message
        order_id = self._extract_order_id(message)
        
        if order_id:
            return self._handle_order_lookup(order_id)
        else:
            # No order ID provided, ask for it
            return {
                "message": "I'd be happy to help you check your order status! Please provide your order number (usually 4-6 digits).",
                "category": "order_inquiry",
                "agent": self.name,
                "needs_order_id": True
            }
    
    def _extract_order_id(self, message: str) -> int:
        """Extract order ID from message using regex patterns"""
        for pattern in self.order_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except (ValueError, IndexError):
                    continue
        return None
    
    def _handle_order_lookup(self, order_id: int) -> Dict[str, Any]:
        """Handle order lookup request"""
        logger.info(f"🔍 Looking up order {order_id}...")
        
        # Get order from enhanced database
        order_data = enhanced_db.get_order(order_id)
        
        if not order_data:
            return {
                "message": f"❌ I couldn't find order #{order_id}. Please check the order number and try again. Order numbers are usually 4-6 digits.",
                "category": "order_not_found",
                "agent": self.name,
                "order_id": order_id
            }
        
        # Format comprehensive order details
        response = self._format_order_details(order_data)
        
        return {
            "message": response,
            "category": "order_details",
            "agent": self.name,
            "order_id": order_id,
            "order_status": order_data["status"],
            "customer_name": order_data["customer_name"]
        }
    
    def _format_order_details(self, order_data: Dict) -> str:
        """Format order details into a comprehensive response"""
        # Build items list with enhanced details
        items_list = []
        for item in order_data["items"]:
            item_text = f"{item['name']} (Qty: {item['quantity']}) - ${item['price']:.2f}"
            if item.get('brand'):
                item_text += f" by {item['brand']}"
            items_list.append(item_text)
        
        items_text = "\n".join([f"   • {item}" for item in items_list])
        
        # Status-specific information
        status_info = self._get_status_specific_info(order_data)
        
        # Build comprehensive response
        response = f"""📦 **Order {order_data['order_id']} Details:**
                        
👤 **Customer:** {order_data['customer_name']}
📧 **Email:** {order_data['customer_email']}
📋 **Items:**
{items_text}

💰 **Order Summary:**
   • Subtotal: ${order_data['total'] - order_data.get('tax', 0) - order_data.get('shipping_cost', 0) + order_data.get('discount', 0):.2f}
   • Shipping: ${order_data.get('shipping_cost', 0):.2f}
   • Tax: ${order_data.get('tax', 0):.2f}
   • Discount: -${order_data.get('discount', 0):.2f}
   • **Total: ${order_data['total']:.2f}**

📊 **Status:** {order_data['status'].title()}
📅 **Order Date:** {order_data['order_date']}
💳 **Payment:** {order_data['payment_method']}
🏠 **Shipping Address:** {order_data['shipping_address']}

{status_info}"""

        return response
    
    def _get_status_specific_info(self, order_data: Dict) -> str:
        """Get status-specific information"""
        status = order_data['status'].lower()
        
        if status == 'pending':
            return "⏳ **Status Info:** Your order is being prepared for processing. You'll receive an update within 24 hours."
        
        elif status == 'processing':
            return "🔄 **Status Info:** Your order is currently being processed and will ship soon. Estimated processing time: 1-2 business days."
        
        elif status == 'shipped':
            tracking_info = ""
            if order_data.get('tracking_number'):
                tracking_info = f"📍 **Tracking Number:** {order_data['tracking_number']}\n"
            
            estimated_delivery = order_data.get('estimated_delivery', 'Not available')
            return f"""🚚 **Status Info:** Your order has been shipped!
{tracking_info}📅 **Estimated Delivery:** {estimated_delivery}
🚛 **In Transit:** Package is on its way to you"""
        
        elif status == 'delivered':
            delivery_info = ""
            if order_data.get('delivery_date'):
                delivery_info += f"📅 **Delivered:** {order_data['delivery_date']}\n"
            if order_data.get('delivery_confirmation'):
                delivery_info += f"📍 **Location:** {order_data['delivery_confirmation']}\n"
            
            return f"""✅ **Status Info:** Your order has been delivered!
{delivery_info}🎉 **Enjoy your purchase!** If you have any issues, please let us know."""
        
        elif status == 'cancelled':
            return "❌ **Status Info:** This order has been cancelled. If you need assistance with a refund or have questions, please let me know."
        
        else:
            return f"📋 **Status Info:** Current status is {status.title()}. If you need more information, please contact our support team."
    
    def get_order_summary(self, order_id: int) -> Dict[str, Any]:
        """Get a brief order summary"""
        order_data = enhanced_db.get_order(order_id)
        
        if not order_data:
            return {"error": "Order not found"}
        
        return {
            "order_id": order_data["order_id"],
            "customer_name": order_data["customer_name"],
            "status": order_data["status"],
            "total": order_data["total"],
            "order_date": order_data["order_date"],
            "item_count": len(order_data["items"])
        } 