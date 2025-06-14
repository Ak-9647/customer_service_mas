import os
import psycopg2
import redis
from pymongo import MongoClient
from typing import Optional
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

# Mock database connections for development
class MockPostgresConnection:
    def __init__(self):
        self.closed = False
        
    def cursor(self):
        return MockCursor()
        
    def commit(self):
        logger.info("Mock PostgreSQL: Transaction committed")
        
    def close(self):
        self.closed = True
        logger.info("Mock PostgreSQL: Connection closed")

class MockCursor:
    def __init__(self):
        self.closed = False
        
    def execute(self, query, params=None):
        logger.info(f"Mock PostgreSQL: Executing query:\n                {query}\n                 with params: {params}")
        
    def fetchone(self):
        return None
        
    def fetchall(self):
        return []
        
    def close(self):
        self.closed = True
        logger.info("Mock PostgreSQL: Cursor closed")
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

def get_postgres_connection():
    """Get PostgreSQL connection with fallback to mock"""
    postgres_url = os.getenv('POSTGRES_URL')
    if not postgres_url or postgres_url == 'postgresql://user:password@localhost:5432/adk_db':
        logger.warning("Using mock PostgreSQL connection - no real database configured")
        return MockPostgresConnection()
    
    try:
        conn = psycopg2.connect(postgres_url)
        return conn
    except Exception as e:
        logger.warning(f"Failed to connect to PostgreSQL: {e}. Using mock connection.")
        return MockPostgresConnection()

def get_redis_connection():
    """Get Redis connection with fallback to mock"""
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
    try:
        r = redis.from_url(redis_url)
        r.ping()  # Test connection
        return r
    except Exception as e:
        logger.warning(f"Failed to connect to Redis: {e}. Using mock connection.")
        return MockRedis()

def get_mongodb_connection():
    """Get MongoDB connection with fallback to mock"""
    mongodb_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/adk_db')
    try:
        client = MongoClient(mongodb_url)
        client.admin.command('ping')  # Test connection
        return client
    except Exception as e:
        logger.warning(f"Failed to connect to MongoDB: {e}. Using mock connection.")
        return MockMongoDB()

class MockRedis:
    def __init__(self):
        self.data = {}
        
    def get(self, key):
        return self.data.get(key)
        
    def set(self, key, value):
        self.data[key] = value
        logger.info(f"Mock Redis: SET {key} = {value}")
        
    def delete(self, key):
        if key in self.data:
            del self.data[key]
            logger.info(f"Mock Redis: DELETE {key}")

class MockMongoDB:
    def __init__(self):
        self.collections = {}
        
    def __getitem__(self, db_name):
        return MockMongoDatabase()

class MockMongoDatabase:
    def __init__(self):
        self.collections = {}
        
    def __getitem__(self, collection_name):
        if collection_name not in self.collections:
            self.collections[collection_name] = MockMongoCollection()
        return self.collections[collection_name]

class MockMongoCollection:
    def __init__(self):
        self.documents = []
        
    def insert_one(self, document):
        self.documents.append(document)
        logger.info(f"Mock MongoDB: Inserted document: {document}")
        
    def find_one(self, query):
        logger.info(f"Mock MongoDB: Finding document with query: {query}")
        return None
        
    def find(self, query=None):
        logger.info(f"Mock MongoDB: Finding documents with query: {query}")
        return []

# Refund logging functions
def log_refund_request(log_id: str, order_id: int, reason: str, priority: str = "standard", estimated_amount: float = 0.0):
    """Log a refund request to the database"""
    conn = get_postgres_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO refund_logs (log_id, order_id, reason, timestamp, status, priority, estimated_amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (log_id, order_id, reason, datetime.now(), 'initiated', priority, estimated_amount))
        conn.commit()
    finally:
        conn.close()

def complete_refund(log_id: str, transaction_id: str, processing_time_seconds: int = 0, refund_method: str = "Original payment method"):
    """Complete a refund and update the log"""
    conn = get_postgres_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            UPDATE refund_logs
            SET status = %s, transaction_id = %s, completion_timestamp = %s, 
                processing_time_seconds = %s, refund_method = %s
            WHERE log_id = %s
        """, ('completed', transaction_id, datetime.now(), processing_time_seconds, refund_method, log_id))
        conn.commit()
    finally:
        conn.close()
