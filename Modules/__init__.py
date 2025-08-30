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
LOG_GROUP=Settings.LOG_GROUP

# Initialize the Pyrogram client
teleshop_bot = Client(
    name="TeleShopBot",
    api_id=Settings.API_ID,
    api_hash=Settings.API_HASH,
    bot_token=Settings.BOT_TOKEN,
)

user_bot = Client(
    name="UserBot",
    api_id=Settings.API_ID,
    api_hash=Settings.API_HASH,
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
        for bot in [teleshop_bot, user_bot]:
            await bot.start()
            # Get bot information
            me = await bot.get_me()
            logger.info(f"🤖 started: @{me.username}")
            logger.info(f"📋 ID: {me.id}")
            logger.info(f"👤 Name: {me.first_name}")

            # Set up bot commands
            
            logger.info(f"✅ {me.full_name} initialization completed successfully!")
            
            # Send startup notification to log group if configured
            if Settings.LOG_GROUP:
                try:
                    await bot.send_message(
                        Settings.LOG_GROUP,
                        f"🚀 **{me.full_name} Started Successfully!**\n\n"
                        f"🤖 **Bot:** @{me.username}\n"
                        f"📅 **Started:** Successfully\n"
                        f"🔧 **Version:** 1.0.0\n"
                        f"💾 **Database:** {'Connected' if Settings.MONGO_URI else 'Local'}"
                    )
                except Exception as e:
                    logger.warning(f"⚠️ Could not send startup message to log group: {e}")

    except Exception as e:
        logger.error(f"❌ initialization failed: {e}")
        raise

# Initialize when module is imported
logger.info("🔧 Initializing modules...")

# Export important objects
__all__ = [
    "teleshop_bot",
    "BOT_NAME", 
    "BOT_USERNAME",
    "initialize_bot",
    "setup_bot_commands"
]
