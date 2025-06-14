"""
Enhanced Database Module with Comprehensive Dummy Data
Provides robust mock data for testing and development
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class EnhancedDatabase:
    """Enhanced database with comprehensive dummy data"""
    
    def __init__(self):
        self.customers = self._generate_customers()
        self.products = self._generate_products()
        self.orders = self._generate_orders()
        self.support_tickets = self._generate_support_tickets()
        self.refund_logs = []
        self.shipping_carriers = self._generate_shipping_data()
        
        logger.info(f"🗄️ Enhanced database initialized:")
        logger.info(f"   📊 {len(self.customers)} customers")
        logger.info(f"   📦 {len(self.products)} products")
        logger.info(f"   🛒 {len(self.orders)} orders")
        logger.info(f"   🎫 {len(self.support_tickets)} support tickets")
    
    def _generate_customers(self) -> Dict[int, Dict]:
        """Generate comprehensive customer data"""
        customers = {}
        
        # Predefined customers for testing
        test_customers = [
            {
                "customer_id": 1001,
                "name": "John Doe",
                "email": "john.doe@email.com",
                "phone": "+1-555-0123",
                "address": "123 Main St, Anytown, USA 12345",
                "join_date": "2023-01-15",
                "tier": "Gold",
                "total_orders": 12,
                "total_spent": 1299.87
            },
            {
                "customer_id": 1002,
                "name": "Bob Johnson",
                "email": "bob.johnson@email.com",
                "phone": "+1-555-0456",
                "address": "789 Pine St, Riverside, USA 54321",
                "join_date": "2023-03-22",
                "tier": "Silver",
                "total_orders": 8,
                "total_spent": 687.43
            },
            {
                "customer_id": 1003,
                "name": "Alice Smith",
                "email": "alice.smith@email.com",
                "phone": "+1-555-0789",
                "address": "456 Oak Ave, Springfield, USA 67890",
                "join_date": "2023-06-10",
                "tier": "Bronze",
                "total_orders": 3,
                "total_spent": 234.56
            }
        ]
        
        # Add test customers
        for customer in test_customers:
            customers[customer["customer_id"]] = customer
        
        # Generate additional random customers
        names = [
            "Emma Wilson", "Michael Brown", "Sarah Davis", "David Miller", "Lisa Garcia",
            "James Rodriguez", "Maria Martinez", "Robert Anderson", "Jennifer Taylor", "William Thomas"
        ]
        
        for i, name in enumerate(names, start=1004):
            customers[i] = {
                "customer_id": i,
                "name": name,
                "email": f"{name.lower().replace(' ', '.')}@email.com",
                "phone": f"+1-555-{random.randint(1000, 9999)}",
                "address": f"{random.randint(100, 999)} {random.choice(['Main', 'Oak', 'Pine', 'Elm', 'Cedar'])} {random.choice(['St', 'Ave', 'Blvd', 'Dr'])}, {random.choice(['Springfield', 'Riverside', 'Fairview', 'Georgetown', 'Madison'])}, USA {random.randint(10000, 99999)}",
                "join_date": (datetime.now() - timedelta(days=random.randint(30, 730))).strftime("%Y-%m-%d"),
                "tier": random.choice(["Bronze", "Silver", "Gold", "Platinum"]),
                "total_orders": random.randint(1, 25),
                "total_spent": round(random.uniform(50, 2500), 2)
            }
        
        return customers
    
    def _generate_products(self) -> Dict[int, Dict]:
        """Generate comprehensive product catalog"""
        products = {
            1: {
                "product_id": 1,
                "name": "Premium Wireless Headphones",
                "category": "Electronics",
                "price": 79.99,
                "description": "High-quality wireless headphones with noise cancellation",
                "brand": "AudioTech",
                "stock": 150,
                "rating": 4.5,
                "reviews": 1247
            },
            2: {
                "product_id": 2,
                "name": "Phone Case",
                "category": "Accessories",
                "price": 19.99,
                "description": "Protective case for smartphones",
                "brand": "ProtectPro",
                "stock": 500,
                "rating": 4.2,
                "reviews": 892
            },
            3: {
                "product_id": 3,
                "name": "Gaming Mouse",
                "category": "Electronics",
                "price": 59.99,
                "description": "High-precision gaming mouse with RGB lighting",
                "brand": "GameGear",
                "stock": 75,
                "rating": 4.7,
                "reviews": 634
            },
            4: {
                "product_id": 4,
                "name": "Mouse Pad",
                "category": "Accessories",
                "price": 14.99,
                "description": "Large gaming mouse pad with smooth surface",
                "brand": "GameGear",
                "stock": 200,
                "rating": 4.3,
                "reviews": 445
            },
            5: {
                "product_id": 5,
                "name": "Bluetooth Speaker",
                "category": "Electronics",
                "price": 89.99,
                "description": "Portable Bluetooth speaker with premium sound",
                "brand": "SoundWave",
                "stock": 120,
                "rating": 4.6,
                "reviews": 789
            },
            6: {
                "product_id": 6,
                "name": "USB-C Cable",
                "category": "Accessories",
                "price": 12.99,
                "description": "High-speed USB-C charging cable",
                "brand": "ChargeFast",
                "stock": 300,
                "rating": 4.1,
                "reviews": 567
            },
            7: {
                "product_id": 7,
                "name": "Wireless Charger",
                "category": "Electronics",
                "price": 34.99,
                "description": "Fast wireless charging pad",
                "brand": "ChargeFast",
                "stock": 85,
                "rating": 4.4,
                "reviews": 321
            },
            8: {
                "product_id": 8,
                "name": "Laptop Stand",
                "category": "Accessories",
                "price": 45.99,
                "description": "Adjustable aluminum laptop stand",
                "brand": "DeskPro",
                "stock": 60,
                "rating": 4.8,
                "reviews": 234
            }
        }
        
        return products
    
    def _generate_orders(self) -> Dict[int, Dict]:
        """Generate comprehensive order data"""
        orders = {}
        
        # Predefined test orders
        test_orders = [
            {
                "order_id": 12345,
                "customer_id": 1001,
                "items": [
                    {"product_id": 1, "quantity": 1, "price": 79.99},
                    {"product_id": 2, "quantity": 1, "price": 19.99}
                ],
                "total": 99.99,
                "status": "shipped",
                "order_date": "2024-06-10",
                "shipping_address": "123 Main St, Anytown, USA 12345",
                "tracking_number": "TRK123456789",
                "payment_method": "Credit Card ending in 4567",
                "estimated_delivery": "2024-06-15",
                "shipping_cost": 0.00,
                "tax": 8.00,
                "discount": 0.00
            },
            {
                "order_id": 11111,
                "customer_id": 1002,
                "items": [
                    {"product_id": 3, "quantity": 1, "price": 59.99},
                    {"product_id": 4, "quantity": 1, "price": 14.99}
                ],
                "total": 74.98,
                "status": "delivered",
                "order_date": "2024-06-08",
                "shipping_address": "789 Pine St, Riverside, USA 54321",
                "tracking_number": "TRK987654321",
                "payment_method": "Credit Card ending in 8901",
                "delivery_date": "2024-06-12",
                "delivery_confirmation": "Package delivered to front door",
                "shipping_cost": 5.99,
                "tax": 6.00,
                "discount": 10.00
            },
            {
                "order_id": 54321,
                "customer_id": 1003,
                "items": [
                    {"product_id": 5, "quantity": 1, "price": 89.99}
                ],
                "total": 89.99,
                "status": "processing",
                "order_date": "2024-06-13",
                "shipping_address": "456 Oak Ave, Springfield, USA 67890",
                "payment_method": "PayPal",
                "estimated_delivery": "2024-06-18",
                "shipping_cost": 7.99,
                "tax": 7.20,
                "discount": 0.00
            }
        ]
        
        # Add test orders
        for order in test_orders:
            orders[order["order_id"]] = order
        
        # Generate additional random orders
        statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
        payment_methods = ["Credit Card ending in 1234", "Credit Card ending in 5678", "PayPal", "Apple Pay", "Google Pay"]
        
        for order_id in range(20000, 20050):
            customer_id = random.choice(list(self.customers.keys()))
            num_items = random.randint(1, 4)
            items = []
            total = 0
            
            for _ in range(num_items):
                product_id = random.choice(list(self.products.keys()))
                quantity = random.randint(1, 3)
                price = self.products[product_id]["price"]
                items.append({
                    "product_id": product_id,
                    "quantity": quantity,
                    "price": price
                })
                total += price * quantity
            
            order_date = datetime.now() - timedelta(days=random.randint(1, 90))
            status = random.choice(statuses)
            
            orders[order_id] = {
                "order_id": order_id,
                "customer_id": customer_id,
                "items": items,
                "total": round(total, 2),
                "status": status,
                "order_date": order_date.strftime("%Y-%m-%d"),
                "shipping_address": self.customers[customer_id]["address"],
                "tracking_number": f"TRK{random.randint(100000000, 999999999)}" if status in ["shipped", "delivered"] else None,
                "payment_method": random.choice(payment_methods),
                "estimated_delivery": (order_date + timedelta(days=random.randint(3, 7))).strftime("%Y-%m-%d"),
                "shipping_cost": round(random.uniform(0, 15), 2),
                "tax": round(total * 0.08, 2),
                "discount": round(random.uniform(0, total * 0.2), 2) if random.random() < 0.3 else 0.00
            }
            
            if status == "delivered":
                orders[order_id]["delivery_date"] = (order_date + timedelta(days=random.randint(3, 6))).strftime("%Y-%m-%d")
                orders[order_id]["delivery_confirmation"] = random.choice([
                    "Package delivered to front door",
                    "Package delivered to mailbox",
                    "Package delivered to neighbor",
                    "Package left at reception"
                ])
        
        return orders
    
    def _generate_support_tickets(self) -> Dict[str, Dict]:
        """Generate support ticket data"""
        tickets = {}
        
        categories = ["Order Issue", "Refund Request", "Shipping Question", "Product Defect", "Account Problem"]
        priorities = ["Low", "Medium", "High", "Urgent"]
        statuses = ["Open", "In Progress", "Resolved", "Closed"]
        
        for i in range(100):
            ticket_id = f"TKT{random.randint(100000, 999999)}"
            customer_id = random.choice(list(self.customers.keys()))
            
            tickets[ticket_id] = {
                "ticket_id": ticket_id,
                "customer_id": customer_id,
                "category": random.choice(categories),
                "priority": random.choice(priorities),
                "status": random.choice(statuses),
                "subject": f"Issue with order or product - {random.choice(['urgent', 'help needed', 'question', 'problem'])}",
                "description": "Customer reported an issue that needs attention",
                "created_date": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d %H:%M:%S"),
                "last_updated": (datetime.now() - timedelta(hours=random.randint(1, 72))).strftime("%Y-%m-%d %H:%M:%S"),
                "assigned_agent": f"Agent{random.randint(1, 10)}"
            }
        
        return tickets
    
    def _generate_shipping_data(self) -> Dict[str, Dict]:
        """Generate shipping carrier data"""
        return {
            "UPS": {
                "name": "UPS",
                "tracking_url": "https://www.ups.com/track?tracknum=",
                "delivery_time": "1-5 business days",
                "cost_standard": 8.99,
                "cost_express": 24.99
            },
            "FedEx": {
                "name": "FedEx",
                "tracking_url": "https://www.fedex.com/apps/fedextrack/?tracknumbers=",
                "delivery_time": "1-3 business days",
                "cost_standard": 9.99,
                "cost_express": 29.99
            },
            "USPS": {
                "name": "USPS",
                "tracking_url": "https://tools.usps.com/go/TrackConfirmAction?tLabels=",
                "delivery_time": "2-8 business days",
                "cost_standard": 6.99,
                "cost_express": 19.99
            }
        }
    
    def get_order(self, order_id: int) -> Optional[Dict]:
        """Get order by ID with enhanced details"""
        if order_id not in self.orders:
            return None
        
        order = self.orders[order_id].copy()
        
        # Add customer details
        customer = self.customers.get(order["customer_id"], {})
        order["customer_name"] = customer.get("name", "Unknown Customer")
        order["customer_email"] = customer.get("email", "unknown@email.com")
        
        # Add product details to items
        enhanced_items = []
        for item in order["items"]:
            product = self.products.get(item["product_id"], {})
            enhanced_item = item.copy()
            enhanced_item["name"] = product.get("name", "Unknown Product")
            enhanced_item["category"] = product.get("category", "Unknown")
            enhanced_item["brand"] = product.get("brand", "Unknown")
            enhanced_items.append(enhanced_item)
        
        order["items"] = enhanced_items
        
        # Calculate days since order
        order_date = datetime.strptime(order["order_date"], "%Y-%m-%d")
        order["days_since_order"] = (datetime.now() - order_date).days
        
        return order
    
    def get_customer(self, customer_id: int) -> Optional[Dict]:
        """Get customer by ID"""
        return self.customers.get(customer_id)
    
    def get_product(self, product_id: int) -> Optional[Dict]:
        """Get product by ID"""
        return self.products.get(product_id)
    
    def search_orders_by_customer(self, customer_id: int) -> List[Dict]:
        """Get all orders for a customer"""
        return [order for order in self.orders.values() if order["customer_id"] == customer_id]
    
    def get_order_statistics(self) -> Dict:
        """Get order statistics"""
        total_orders = len(self.orders)
        total_revenue = sum(order["total"] for order in self.orders.values())
        
        status_counts = {}
        for order in self.orders.values():
            status = order["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_orders": total_orders,
            "total_revenue": round(total_revenue, 2),
            "status_breakdown": status_counts,
            "average_order_value": round(total_revenue / total_orders if total_orders > 0 else 0, 2)
        }

# Global database instance
enhanced_db = EnhancedDatabase() 