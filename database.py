#!/usr/bin/env python3
"""
TeleShopBot Database Connection Module
Handles MongoDB database operations for the marketplace bot
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import asyncio

# ============================================
# DATABASE CONFIGURATION
# ============================================

class DatabaseManager:
    def __init__(self):
        """
        Initialize database connection
        """
        self.client = None
        self.database = None
        self.connected = False
        
        # Database configuration
        self.mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017/')
        self.database_name = os.getenv('DB_NAME', 'teleshopbot')
        
    async def connect(self):
        """
        Connect to MongoDB database
        """
        try:
            print("🔗 Connecting to database...")
            
            self.client = AsyncIOMotorClient(self.mongo_url)
            self.database = self.client[self.database_name]
            
            # Test connection
            await self.client.admin.command('ismaster')
            self.connected = True
            
            print("✅ Database connected successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    async def disconnect(self):
        """
        Disconnect from database
        """
        if self.client:
            self.client.close()
            self.connected = False
            print("🔌 Database disconnected")

# ============================================
# USER OPERATIONS
# ============================================

class Users:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.collection = "users"
    
    async def add_user(self, user_id: int, first_name: str, username: str = None):
        """
        Add new user to database
        """
        try:
            user_data = {
                "user_id": user_id,
                "first_name": first_name,
                "username": username,
                "joined_date": datetime.utcnow(),
                "is_premium": False,
                "premium_expiry": None,
                "language": "english",
                "notifications_enabled": True,
                "total_purchases": 0,
                "total_sales": 0,
                "total_spent": 0.0,
                "total_earned": 0.0,
                "is_banned": False,
                "ban_reason": None
            }
            
            result = await self.db.database[self.collection].update_one(
                {"user_id": user_id},
                {"$setOnInsert": user_data},
                upsert=True
            )
            
            return result.upserted_id is not None
            
        except Exception as e:
            print(f"❌ Error adding user: {e}")
            return False
    
    async def get_user(self, user_id: int):
        """
        Get user data from database
        """
        try:
            user = await self.db.database[self.collection].find_one({"user_id": user_id})
            return user
            
        except Exception as e:
            print(f"❌ Error getting user: {e}")
            return None
    
    async def update_user(self, user_id: int, update_data: dict):
        """
        Update user data
        """
        try:
            result = await self.db.database[self.collection].update_one(
                {"user_id": user_id},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"❌ Error updating user: {e}")
            return False
    
    async def get_user_count(self):
        """
        Get total user count
        """
        try:
            count = await self.db.database[self.collection].count_documents({})
            return count
            
        except Exception as e:
            print(f"❌ Error getting user count: {e}")
            return 0

# ============================================
# ASSET LISTINGS OPERATIONS
# ============================================

class Assets:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.collection = "assets"
    
    async def add_listing(self, listing_data: dict):
        """
        Add new asset listing
        """
        try:
            listing_data["created_date"] = datetime.utcnow()
            listing_data["status"] = "active"
            listing_data["views"] = 0
            listing_data["is_featured"] = False
            
            result = await self.db.database[self.collection].insert_one(listing_data)
            return result.inserted_id
            
        except Exception as e:
            print(f"❌ Error adding listing: {e}")
            return None
    
    async def get_listings(self, asset_type: str = None, status: str = "active", limit: int = 10):
        """
        Get asset listings with filters
        """
        try:
            query = {"status": status}
            if asset_type:
                query["asset_type"] = asset_type
            
            cursor = self.db.database[self.collection].find(query).limit(limit)
            listings = await cursor.to_list(length=limit)
            
            return listings
            
        except Exception as e:
            print(f"❌ Error getting listings: {e}")
            return []
    
    async def get_user_listings(self, user_id: int, status: str = None):
        """
        Get user's asset listings
        """
        try:
            query = {"seller_id": user_id}
            if status:
                query["status"] = status
                
            cursor = self.db.database[self.collection].find(query)
            listings = await cursor.to_list(length=None)
            
            return listings
            
        except Exception as e:
            print(f"❌ Error getting user listings: {e}")
            return []

# ============================================
# TRANSACTION OPERATIONS
# ============================================

class Transactions:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.collection = "transactions"
    
    async def create_transaction(self, transaction_data: dict):
        """
        Create new transaction record
        """
        try:
            transaction_data["created_date"] = datetime.utcnow()
            transaction_data["status"] = "pending"
            
            result = await self.db.database[self.collection].insert_one(transaction_data)
            return result.inserted_id
            
        except Exception as e:
            print(f"❌ Error creating transaction: {e}")
            return None
    
    async def update_transaction_status(self, transaction_id: str, status: str):
        """
        Update transaction status
        """
        try:
            from bson import ObjectId
            
            result = await self.db.database[self.collection].update_one(
                {"_id": ObjectId(transaction_id)},
                {"$set": {"status": status, "updated_date": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"❌ Error updating transaction: {e}")
            return False

# ============================================
# CHAT OPERATIONS (For chat ID management)
# ============================================

class Chats:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.collection = "chats"
    
    async def add_chat(self, chat_id: int, chat_type: str):
        """
        Add chat to database
        """
        try:
            chat_data = {
                "chat_id": chat_id,
                "chat_type": chat_type,
                "added_date": datetime.utcnow(),
                "is_active": True
            }
            
            result = await self.db.database[self.collection].update_one(
                {"chat_id": chat_id},
                {"$setOnInsert": chat_data},
                upsert=True
            )
            
            return result.upserted_id is not None
            
        except Exception as e:
            print(f"❌ Error adding chat: {e}")
            return False
    
    async def remove_chat(self, chat_id: int):
        """
        Remove chat from database
        """
        try:
            result = await self.db.database[self.collection].update_one(
                {"chat_id": chat_id},
                {"$set": {"is_active": False}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"❌ Error removing chat: {e}")
            return False

# ============================================
# DATABASE INITIALIZATION
# ============================================

# Global database manager instance
db_manager = DatabaseManager()
users_db = Users(db_manager)
assets_db = Assets(db_manager)
transactions_db = Transactions(db_manager)
chats_db = Chats(db_manager)

async def init_database():
    """
    Initialize database connection
    """
    try:
        success = await db_manager.connect()
        if success:
            print("🗄️ Database initialized successfully!")
        else:
            print("❌ Database initialization failed!")
        return success
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        return False

# ============================================
# EXPORT CLASSES
# ============================================

__all__ = [
    'DatabaseManager',
    'Users', 
    'Assets',
    'Transactions',
    'Chats',
    'db_manager',
    'users_db',
    'assets_db', 
    'transactions_db',
    'chats_db',
    'init_database'
]
