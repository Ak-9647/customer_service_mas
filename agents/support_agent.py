import logging
from typing import Dict, Any
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class GeneralSupportAgent(BaseAgent):
    """General support agent for handling miscellaneous customer inquiries"""
    
    def __init__(self):
        super().__init__(
            name="GeneralSupportAgent",
            description="Handles general customer support inquiries, greetings, and miscellaneous questions"
        )
        self.support_categories = {
            "shipping": {
                "keywords": ["shipping", "delivery", "ship", "when will", "arrive", "tracking", "fedex", "ups", "usps"],
                "response": """🚚 **Shipping Information:**

📦 **Standard Shipping:** 3-5 business days (FREE on orders $50+)
⚡ **Express Shipping:** 1-2 business days ($9.99)
🌟 **Overnight:** Next business day ($19.99)

📍 **Tracking:** You'll receive a tracking number via email once your order ships
🌍 **International:** 7-14 business days (additional fees may apply)

Need help with a specific order? Please provide your order number!"""
            },
            "returns": {
                "keywords": ["return", "exchange", "send back", "return policy"],
                "response": """🔄 **Return & Exchange Policy:**

✅ **Return Window:** 30 days from delivery date
📦 **Condition:** Items must be unused and in original packaging
💰 **Refund:** Full refund to original payment method
🔄 **Exchanges:** Free exchanges for size/color (subject to availability)

**Return Process:**
1. Contact us with your order number
2. We'll provide a prepaid return label
3. Ship the item back to us
4. Refund processed within 3-5 business days

Want to start a return? Please provide your order number!"""
            },
            "payment": {
                "keywords": ["payment", "charge", "billing", "credit card", "paypal", "apple pay", "payment methods"],
                "response": """💳 **Payment Information:**

**Accepted Payment Methods:**
💳 All major credit cards (Visa, MasterCard, Amex, Discover)
📱 PayPal & PayPal Pay in 4
🍎 Apple Pay & Google Pay
🏦 Shop Pay & Afterpay

**Security:** All payments are encrypted and secure
💰 **Currency:** USD (international cards accepted)
📧 **Receipts:** Emailed immediately after purchase

Having payment issues? Please describe the problem and I'll help!"""
            },
            "account": {
                "keywords": ["account", "login", "password", "profile", "email", "update", "change"],
                "response": """👤 **Account Management:**

**Account Features:**
📧 Update email and shipping addresses
📱 Save payment methods securely
📦 Track order history
❤️ Create wishlists
🔔 Manage email preferences

**Need Help?**
🔑 Forgot password? Use the "Reset Password" link
📧 Change email? Contact us with your order number
🏠 Update address? Log in to your account settings

What specific account help do you need?"""
            },
            "contact": {
                "keywords": ["contact", "phone", "email", "speak to", "human", "representative", "hours"],
                "response": """📞 **Contact Information:**

**Customer Service:**
📧 Email: support@company.com
📱 Phone: 1-800-SUPPORT (1-800-786-7678)
💬 Live Chat: Available on our website

**Hours:**
🕘 Monday-Friday: 9:00 AM - 6:00 PM EST
🕘 Saturday: 10:00 AM - 4:00 PM EST
🕘 Sunday: Closed

**Response Times:**
📧 Email: Within 24 hours
📱 Phone: Average wait time 2-3 minutes
💬 Chat: Immediate response during business hours

How else can I help you today?"""
            },
            "product": {
                "keywords": ["product", "item", "quality", "size", "color", "material", "specifications"],
                "response": """🛍️ **Product Information:**

**Product Details:**
📏 Size guides available on each product page
🎨 Color accuracy guaranteed (30-day return if not satisfied)
🏷️ All materials and care instructions listed
⭐ Customer reviews and ratings available

**Quality Guarantee:**
✅ 30-day satisfaction guarantee
🔧 1-year warranty on applicable items
🏆 Premium quality materials
📸 High-resolution product photos

Looking for specific product information? Please let me know the item name or order number!"""
            }
        }
    
    def can_handle(self, message: str) -> bool:
        """Check if this message is a general support inquiry"""
        message_lower = message.lower().strip()
        
        # Handle greetings and general inquiries
        greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
        general_inquiries = ["help", "support", "question", "info", "information"]
        
        # Check if it's a greeting or general inquiry (but not if it has specific keywords)
        is_greeting = any(greeting in message_lower for greeting in greetings)
        is_general = any(inquiry in message_lower for inquiry in general_inquiries)
        
        # Don't handle as greeting if it has specific support category keywords
        has_specific_keywords = any(
            any(keyword in message_lower for keyword in category["keywords"])
            for category in self.support_categories.values()
        )
        
        if is_greeting and has_specific_keywords:
            is_greeting = False  # Prioritize specific support over greeting
        
        # Check if it matches any support category
        matches_category = any(
            any(keyword in message_lower for keyword in category["keywords"])
            for category in self.support_categories.values()
        )
        
        return is_greeting or is_general or matches_category
    
    def process_message(self, message: str) -> Dict[str, Any]:
        """Process general support messages"""
        message_lower = message.lower().strip()
        
        # First check for specific support categories (highest priority)
        for category_name, category_info in self.support_categories.items():
            if any(keyword in message_lower for keyword in category_info["keywords"]):
                logger.info(f"🎯 GeneralSupportAgent: Matched category '{category_name}' for message: {message[:50]}...")
                return {
                    "message": category_info["response"],
                    "category": category_name,
                    "agent": self.name
                }
        
        # Then handle greetings (but only if no specific category matched)
        if self._is_greeting(message_lower):
            logger.info(f"🎯 GeneralSupportAgent: Handling greeting for message: {message[:50]}...")
            return self._handle_greeting(message)
        
        # Handle general help requests as fallback
        logger.info(f"🎯 GeneralSupportAgent: Using general help for message: {message[:50]}...")
        return self._handle_general_help(message)
    
    def _is_greeting(self, message_lower: str) -> bool:
        """Check if message is a greeting"""
        greetings = [
            "hello", "hi", "hey", "good morning", "good afternoon", 
            "good evening", "howdy", "greetings", "what's up", "sup"
        ]
        return any(greeting in message_lower for greeting in greetings)
    
    def _handle_greeting(self, message: str) -> Dict[str, Any]:
        """Handle greeting messages"""
        return {
            "message": """👋 **Hello! Welcome to Customer Support!**

I'm here to help you with:
🛍️ Order inquiries and tracking
💰 Refunds and returns  
🚚 Shipping information
💳 Payment questions
👤 Account management
📞 Contact information

What can I help you with today?""",
            "suggestions": [
                "Check my order status",
                "I need a refund",
                "Shipping information",
                "Return policy",
                "Contact information"
            ]
        }
    
    def _handle_general_help(self, message: str) -> Dict[str, Any]:
        """Handle general help requests"""
        return {
            "message": """🤝 **I'm here to help!**

I can assist you with:

📦 **Orders & Tracking**
- Check order status
- Track shipments
- Update delivery information

💰 **Returns & Refunds**
- Process returns
- Handle refunds
- Exchange items

🚚 **Shipping & Delivery**
- Shipping options and costs
- Delivery timeframes
- International shipping

💳 **Payments & Billing**
- Payment methods
- Billing questions
- Transaction issues

👤 **Account Support**
- Login help
- Update account info
- Manage preferences

What specific area would you like help with?""",
            "categories": list(self.support_categories.keys())
        }
    
    def get_faq(self) -> Dict[str, Any]:
        """Get frequently asked questions"""
        return {
            "message": """❓ **Frequently Asked Questions:**

**Q: How long does shipping take?**
A: Standard shipping is 3-5 business days, Express is 1-2 days.

**Q: What's your return policy?**
A: 30 days from delivery, items must be unused and in original packaging.

**Q: Do you ship internationally?**
A: Yes! International shipping takes 7-14 business days.

**Q: What payment methods do you accept?**
A: All major credit cards, PayPal, Apple Pay, and more.

**Q: How can I track my order?**
A: You'll receive a tracking number via email once your order ships.

**Q: Can I change my order after placing it?**
A: Contact us within 1 hour of placing your order for changes.

Need help with something else?""",
            "type": "faq"
        }
    
    def _get_fallback_response(self, message: str) -> str:
        """Custom fallback for general support agent"""
        return """I'm here to help with general customer support questions! 

I can assist with:
• Order tracking and status
• Shipping and delivery info  
• Return and refund policies
• Payment and billing questions
• Account management
• Contact information

What would you like help with today?""" 