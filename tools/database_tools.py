import time
import uuid
from datetime import datetime, timedelta
import random
from persistence.memory_manager import get_postgres_connection

# Enhanced mock order database with multiple scenarios
MOCK_ORDERS = {
    12345: {
        "order_id": 12345,
        "customer_name": "John Doe",
        "customer_email": "john.doe@email.com",
        "items": [
            {"item_id": 1, "name": "Premium Wireless Headphones", "quantity": 1, "price": 79.99},
            {"item_id": 2, "name": "Phone Case", "quantity": 1, "price": 19.99}
        ],
        "total": 99.99,
        "status": "shipped",
        "order_date": "2024-06-10",
        "shipping_address": "123 Main St, Anytown, USA 12345",
        "tracking_number": "TRK123456789",
        "payment_method": "Credit Card ending in 4567"
    },
    54321: {
        "order_id": 54321,
        "customer_name": "Jane Smith",
        "customer_email": "jane.smith@email.com",
        "items": [
            {"item_id": 3, "name": "Smart Watch", "quantity": 1, "price": 199.99},
            {"item_id": 4, "name": "Watch Band", "quantity": 2, "price": 24.99}
        ],
        "total": 249.97,
        "status": "processing",
        "order_date": "2024-06-13",
        "shipping_address": "456 Oak Ave, Springfield, USA 67890",
        "tracking_number": None,
        "payment_method": "PayPal"
    },
    11111: {
        "order_id": 11111,
        "customer_name": "Bob Johnson",
        "customer_email": "bob.johnson@email.com",
        "items": [
            {"item_id": 5, "name": "Gaming Mouse", "quantity": 1, "price": 59.99},
            {"item_id": 6, "name": "Mouse Pad", "quantity": 1, "price": 14.99}
        ],
        "total": 74.98,
        "status": "delivered",
        "order_date": "2024-06-08",
        "shipping_address": "789 Pine St, Riverside, USA 54321",
        "tracking_number": "TRK987654321",
        "payment_method": "Credit Card ending in 8901",
        "delivery_date": "2024-06-12"
    },
    22222: {
        "order_id": 22222,
        "customer_name": "Alice Brown",
        "customer_email": "alice.brown@email.com",
        "items": [
            {"item_id": 7, "name": "Bluetooth Speaker", "quantity": 1, "price": 89.99}
        ],
        "total": 89.99,
        "status": "cancelled",
        "order_date": "2024-06-11",
        "shipping_address": "321 Elm St, Lakeside, USA 98765",
        "tracking_number": None,
        "payment_method": "Apple Pay",
        "cancellation_reason": "Customer requested cancellation"
    },
    33333: {
        "order_id": 33333,
        "customer_name": "Mike Wilson",
        "customer_email": "mike.wilson@email.com",
        "items": [
            {"item_id": 8, "name": "Laptop Stand", "quantity": 1, "price": 45.99},
            {"item_id": 9, "name": "USB-C Cable", "quantity": 3, "price": 12.99}
        ],
        "total": 84.96,
        "status": "refunded",
        "order_date": "2024-06-05",
        "shipping_address": "654 Maple Dr, Hilltown, USA 13579",
        "tracking_number": "TRK456789123",
        "payment_method": "Credit Card ending in 2468",
        "refund_date": "2024-06-09",
        "refund_amount": 82.97,  # After processing fee
        "refund_reason": "Product defect"
    }
}

def lookup_order_by_id(order_id: int) -> dict:
    """
    Enhanced order lookup with comprehensive order information
    Simulates database lookup with realistic delay
    """
    print(f"🔍 Looking up order {order_id}...")
    
    # Simulate database query delay
    time.sleep(1)
    
    # Check if order exists in our mock database
    if order_id in MOCK_ORDERS:
        order = MOCK_ORDERS[order_id].copy()
        
        # Add dynamic information based on status
        if order["status"] == "shipped":
            # Calculate estimated delivery
            order_date = datetime.strptime(order["order_date"], "%Y-%m-%d")
            estimated_delivery = order_date + timedelta(days=random.randint(3, 7))
            order["estimated_delivery"] = estimated_delivery.strftime("%Y-%m-%d")
            
        elif order["status"] == "processing":
            order["estimated_ship_date"] = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            
        elif order["status"] == "delivered":
            order["delivery_confirmation"] = "Package delivered to front door"
            
        # Add order age for context
        order_date = datetime.strptime(order["order_date"], "%Y-%m-%d")
        days_ago = (datetime.now() - order_date).days
        order["days_since_order"] = days_ago
        
        return order
    else:
        # Generate realistic error messages based on order ID patterns
        if order_id < 1000:
            return {"error": "Order ID too short. Order numbers are typically 4-6 digits."}
        elif order_id > 999999:
            return {"error": "Order ID too long. Please check your order number."}
        else:
            return {"error": f"Order {order_id} not found in our system. Please check your order number or contact support."}

def process_refund_step_1(order_id: int, reason: str = "Customer request") -> dict:
    """
    Enhanced refund step 1: Log refund request with business validation
    """
    print(f"💰 Processing refund request for order {order_id}...")
    
    try:
        # Generate unique log ID
        log_id = str(uuid.uuid4())
        
        # Enhanced reason processing
        if not reason or len(reason.strip()) < 3:
            reason = "Customer requested refund"
        
        # Validate reason length
        if len(reason) > 500:
            reason = reason[:500] + "..."
        
        # Get database connection
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        # Create refund log entry with additional metadata
        query = """
            INSERT INTO refund_logs (log_id, order_id, reason, timestamp, status, priority, estimated_amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        # Determine priority based on order value (if we can look it up)
        priority = "standard"
        estimated_amount = 0.0
        
        if order_id in MOCK_ORDERS:
            order_total = MOCK_ORDERS[order_id]["total"]
            estimated_amount = order_total
            if order_total > 200:
                priority = "high"
            elif order_total > 100:
                priority = "medium"
        
        cursor.execute(query, (
            log_id, 
            order_id, 
            reason, 
            datetime.now(), 
            'initiated',
            priority,
            estimated_amount
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "logged",
            "log_id": log_id,
            "message": f"Refund request logged for order {order_id}",
            "priority": priority,
            "estimated_amount": estimated_amount,
            "next_step": "Processing refund..."
        }
        
    except Exception as e:
        print(f"❌ Error in refund step 1: {e}")
        return {"error": f"Failed to log refund request: {str(e)}"}

def process_refund_step_2(log_id: str) -> dict:
    """
    Enhanced refund step 2: Complete refund processing with transaction details
    """
    print(f"✅ Completing refund for log ID {log_id}...")
    
    try:
        # Generate transaction ID
        transaction_id = str(uuid.uuid4())
        
        # Get database connection
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        # Update refund log with completion details
        query = """
            UPDATE refund_logs
            SET status = %s, transaction_id = %s, completion_timestamp = %s, 
                processing_time_seconds = %s, refund_method = %s
            WHERE log_id = %s
        """
        
        # Calculate processing time (simulate realistic processing)
        processing_time = random.randint(30, 180)  # 30 seconds to 3 minutes
        
        # Determine refund method
        refund_methods = ["Original payment method", "Store credit", "Bank transfer"]
        refund_method = random.choice(refund_methods)
        
        cursor.execute(query, (
            'completed',
            transaction_id,
            datetime.now(),
            processing_time,
            refund_method,
            log_id
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "completed",
            "transaction_id": transaction_id,
            "message": "Refund processed successfully",
            "processing_time_seconds": processing_time,
            "refund_method": refund_method,
            "estimated_arrival": "3-5 business days"
        }
        
    except Exception as e:
        print(f"❌ Error in refund step 2: {e}")
        return {"error": f"Failed to complete refund: {str(e)}"}

def get_order_history(customer_email: str) -> dict:
    """
    New function: Get order history for a customer
    """
    print(f"📋 Looking up order history for {customer_email}...")
    
    # Simulate database delay
    time.sleep(0.5)
    
    customer_orders = []
    for order_id, order_data in MOCK_ORDERS.items():
        if order_data["customer_email"].lower() == customer_email.lower():
            customer_orders.append({
                "order_id": order_id,
                "order_date": order_data["order_date"],
                "total": order_data["total"],
                "status": order_data["status"],
                "items_count": len(order_data["items"])
            })
    
    if customer_orders:
        # Sort by order date (newest first)
        customer_orders.sort(key=lambda x: x["order_date"], reverse=True)
        return {
            "customer_email": customer_email,
            "orders": customer_orders,
            "total_orders": len(customer_orders),
            "total_spent": sum(order["total"] for order in customer_orders)
        }
    else:
        return {"error": f"No orders found for customer {customer_email}"}

def check_refund_eligibility(order_id: int) -> dict:
    """
    New function: Check if an order is eligible for refund
    """
    print(f"🔍 Checking refund eligibility for order {order_id}...")
    
    if order_id not in MOCK_ORDERS:
        return {"error": f"Order {order_id} not found"}
    
    order = MOCK_ORDERS[order_id]
    status = order["status"].lower()
    order_date = datetime.strptime(order["order_date"], "%Y-%m-%d")
    days_since_order = (datetime.now() - order_date).days
    
    # Business rules for refund eligibility
    if status == "cancelled":
        return {
            "eligible": False,
            "reason": "Order was already cancelled",
            "alternative": "If you were charged, the refund should process automatically within 3-5 business days."
        }
    
    if status == "refunded":
        return {
            "eligible": False,
            "reason": "Order was already refunded",
            "refund_date": order.get("refund_date", "Unknown"),
            "refund_amount": order.get("refund_amount", 0)
        }
    
    if days_since_order > 30:
        return {
            "eligible": False,
            "reason": "Refund window has expired (30 days)",
            "alternative": "You may still be eligible for store credit. Please contact customer service."
        }
    
    if status == "processing":
        return {
            "eligible": True,
            "reason": "Order can be cancelled/refunded as it hasn't shipped yet",
            "refund_type": "Full refund",
            "processing_time": "Immediate"
        }
    
    if status in ["shipped", "delivered"]:
        return {
            "eligible": True,
            "reason": "Order is eligible for return refund",
            "refund_type": "Full refund minus return shipping",
            "processing_time": "3-5 business days after we receive the return",
            "return_required": True
        }
    
    return {
        "eligible": True,
        "reason": "Standard refund eligibility",
        "refund_type": "Full refund",
        "processing_time": "3-5 business days"
    }

def get_shipping_info(order_id: int) -> dict:
    """
    New function: Get detailed shipping information
    """
    print(f"🚚 Getting shipping info for order {order_id}...")
    
    if order_id not in MOCK_ORDERS:
        return {"error": f"Order {order_id} not found"}
    
    order = MOCK_ORDERS[order_id]
    
    shipping_info = {
        "order_id": order_id,
        "status": order["status"],
        "shipping_address": order["shipping_address"],
        "tracking_number": order.get("tracking_number")
    }
    
    # Add status-specific information
    if order["status"] == "processing":
        shipping_info.update({
            "estimated_ship_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "shipping_method": "Standard (3-5 business days)",
            "message": "Your order is being prepared for shipment."
        })
    
    elif order["status"] == "shipped":
        order_date = datetime.strptime(order["order_date"], "%Y-%m-%d")
        estimated_delivery = order_date + timedelta(days=random.randint(3, 7))
        shipping_info.update({
            "estimated_delivery": estimated_delivery.strftime("%Y-%m-%d"),
            "shipping_method": "Standard Ground",
            "message": "Your order is on its way!",
            "tracking_url": f"https://tracking.example.com/{order['tracking_number']}"
        })
    
    elif order["status"] == "delivered":
        shipping_info.update({
            "delivery_date": order.get("delivery_date", "Unknown"),
            "delivery_confirmation": order.get("delivery_confirmation", "Package delivered"),
            "message": "Your order has been delivered successfully."
        })
    
    elif order["status"] == "cancelled":
        shipping_info.update({
            "message": "This order was cancelled and will not be shipped.",
            "cancellation_reason": order.get("cancellation_reason", "Customer request")
        })
    
    return shipping_info
