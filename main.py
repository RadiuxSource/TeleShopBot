#!/usr/bin/env python3
"""
TeleShopBot - Telegram Buy & Sell Bot for Digital Assets
Author: TeleShopBot Team
Description: A professional Telegram bot for buying and selling Telegram Groups, Channels, Bots, and other digital assets.
Version: 1.0.0
"""

import asyncio
import logging
from pyrogram import Client
from config import Settings

# Configure logging for better debugging and monitoring
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("teleshopbot.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """
    Main function to start the TeleShopBot
    """
    try:
        # Import bot instance from modules
        from Modules import teleshop_bot
        
        logger.info("🚀 Starting TeleShopBot...")
        logger.info("📋 Bot Configuration:")
        logger.info(f"   API ID: {Settings.API_ID}")
        logger.info(f"   Bot Token: {Settings.BOT_TOKEN[:20]}...")
        logger.info(f"   MongoDB URI: {'Connected' if Settings.MONGO_URI else 'Not configured'}")
        
        # Start the bot
        await teleshop_bot.start()
        logger.info("✅ TeleShopBot started successfully!")
        
        # Initialize bot with database and commands
        from Modules import initialize_bot
        await initialize_bot()
        
        logger.info("🛍️ Ready to handle buy/sell transactions...")
        
        # Keep the bot running
        await teleshop_bot.idle()
        
    except Exception as e:
        logger.error(f"❌ Failed to start TeleShopBot: {e}")
        raise
    finally:
        logger.info("🛑 TeleShopBot stopped")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"💥 Critical error: {e}")
        exit(1)