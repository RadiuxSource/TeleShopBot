#!/usr/bin/env python3
"""
TeleShopBot Modules Package
Initializes the bot and loads all plugins and handlers
"""

import asyncio
import logging
from pyrogram import Client
from pyrogram.types import BotCommand
from config import Settings
from motor.motor_asyncio import AsyncIOMotorClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Bot information
BOT_NAME = Settings.BOT_NAME
BOT_USERNAME = Settings.BOT_USERNAME
SUDO_USERS=Settings.ADMIN_IDS


# Initialize the Pyrogram client
teleshop_bot = Client(
    name="TeleShopBot",
    api_id=Settings.API_ID,
    api_hash=Settings.API_HASH,
    bot_token=Settings.BOT_TOKEN,
)


client = AsyncIOMotorClient(Settings.MONGO_URI)
db = client["::BUYSELL::"]
ChatDB = db["Chats_DB"]
UserDB = db["User_DB"]
StoreDB = db["Store_DB"]


async def initialize_bot():
    """
    Initialize bot with necessary setup
    """
    try:
        await teleshop_bot.start()
        # Get bot information
        me = await teleshop_bot.get_me()
        logger.info(f"🤖 Bot started: @{me.username}")
        logger.info(f"📋 Bot ID: {me.id}")
        logger.info(f"👤 Bot Name: {me.first_name}")
        
        # Set up bot commands
        
        logger.info("✅ TeleShopBot initialization completed successfully!")
        
        # Send startup notification to log group if configured
        if Settings.LOG_GROUP:
            try:
                await teleshop_bot.send_message(
                    Settings.LOG_GROUP,
                    f"🚀 **TeleShopBot Started Successfully!**\n\n"
                    f"🤖 **Bot:** @{me.username}\n"
                    f"📅 **Started:** Successfully\n"
                    f"🔧 **Version:** 1.0.0\n"
                    f"💾 **Database:** {'Connected' if Settings.MONGO_URI else 'Local'}"
                )
            except Exception as e:
                logger.warning(f"⚠️ Could not send startup message to log group: {e}")
                
    except Exception as e:
        logger.error(f"❌ Bot initialization failed: {e}")
        raise

# Initialize when module is imported
logger.info("🔧 Initializing TeleShopBot modules...")
logger.info(f"📋 Bot Name: {BOT_NAME}")
logger.info(f"📋 Bot Username: @{BOT_USERNAME}")

# Export important objects
__all__ = [
    "teleshop_bot",
    "BOT_NAME", 
    "BOT_USERNAME",
    "initialize_bot",
    "setup_bot_commands"
]
