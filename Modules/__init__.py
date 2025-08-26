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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Bot information
BOT_NAME = Settings.BOT_NAME
BOT_USERNAME = Settings.BOT_USERNAME

# Initialize the Pyrogram client
teleshop_bot = Client(
    name="TeleShopBot",
    api_id=Settings.API_ID,
    api_hash=Settings.API_HASH,
    bot_token=Settings.BOT_TOKEN,
    plugins=dict(root="Modules/plugins"),
    workdir=".",
    sleep_threshold=60
)

async def setup_bot_commands():
    """
    Set up bot commands that will appear in Telegram's command menu
    """
    commands = [
        BotCommand("start", "🚀 Start the bot"),
        BotCommand("help", "❓ Get help and instructions"),
        BotCommand("profile", "👤 View your profile"),
        BotCommand("buy", "🛒 Buy digital assets"),
        BotCommand("sell", "💰 Sell your assets"),
        BotCommand("settings", "⚙️ Bot settings"),
        BotCommand("premium", "✨ Premium features"),
        BotCommand("support", "🆘 Get support"),
        BotCommand("cancel", "❌ Cancel current operation")
    ]
    
    try:
        await teleshop_bot.set_bot_commands(commands)
        logger.info("✅ Bot commands set successfully")
    except Exception as e:
        logger.error(f"❌ Failed to set bot commands: {e}")

async def initialize_bot():
    """
    Initialize bot with necessary setup
    """
    try:
        # Initialize database if available
        try:
            from database import init_database
            database_success = await init_database()
            if database_success:
                logger.info("✅ Database connected successfully!")
            else:
                logger.warning("⚠️ Database connection failed. Using sample data.")
        except ImportError:
            logger.warning("⚠️ Database module not found. Bot will run with sample data.")
        
        # Get bot information
        me = await teleshop_bot.get_me()
        logger.info(f"🤖 Bot started: @{me.username}")
        logger.info(f"📋 Bot ID: {me.id}")
        logger.info(f"👤 Bot Name: {me.first_name}")
        
        # Set up bot commands
        await setup_bot_commands()
        
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
