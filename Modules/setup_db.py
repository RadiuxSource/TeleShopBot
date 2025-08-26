from motor.motor_asyncio import AsyncIOMotorDatabase

async def setup_indexes(db: AsyncIOMotorDatabase):
    """Setup database indexes for optimized queries"""

    # Chats collection indexes
    await db.Chats_DB.create_index("chat_id")
    
    # Quiz collection indexes
    await db.Quiz_DB.create_index("creator_id")
    await db.Quiz_DB.create_index([("creator_id", 1), ("_id", 1)])
    
    # User stats collection indexes
    await db.V2_User_Stat_DB.create_index("user_id")
    
    # For global stats queries
    # await db.chats.create_index([("chat_id", 1), ("unique_participants", 1)])

