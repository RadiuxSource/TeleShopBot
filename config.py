#!/usr/bin/env python3
"""
TeleShopBot Configuration File
Contains all bot settings, API keys, and environment variables
"""

from os import environ as env
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """
    Configuration class for TeleShopBot
    All sensitive information should be stored in environment variables
    """
    
    # ========== TELEGRAM API CREDENTIALS ==========
    API_ID = int(env.get("API_ID", 12380656))
    API_HASH = str(env.get("API_HASH", "d927c13beaaf5110f25c505b7c071273"))
    BOT_TOKEN = str(env.get("BOT_TOKEN", "7820131118:AAHzh7guWLM0o6iq4HC0VcRQfcAjNkP0hbk"))
    
    # ========== DATABASE CONFIGURATION ==========
    MONGO_URI = str(env.get("MONGO_URI", "mongodb+srv://queenxytra:queenxytra@cluster0.ivuxz80.mongodb.net/?retryWrites=true&w=majority"))
    DATABASE_NAME = str(env.get("DATABASE_NAME", "teleshopbot"))
    
    # ========== BOT INFORMATION ==========
    BOT_NAME = "TeleShopBot"
    BOT_USERNAME = str(env.get("BOT_USERNAME", "TeleShopBot"))
    BOT_DESCRIPTION = "Buy & Sell Telegram Groups, Channels, Bots and Digital Assets"
    
    # ========== LOGGING AND MONITORING ==========
    LOG_GROUP = int(env.get("LOG_GROUP", -1002269859662))
    LOG_CHANNEL = int(env.get("LOG_CHANNEL", -1002269859662))
    
    # ========== SOCIAL LINKS ==========
    SUPPORT_CHAT = str(env.get("SUPPORT_CHAT", "https://t.me/TeleShopBotSupport"))
    UPDATES_CHANNEL = str(env.get("UPDATES_CHANNEL", "https://t.me/TeleShopBotUpdates"))
    
    # ========== ADMIN CONFIGURATION ==========
    try:
        SUDO_USERS = [int(admin_id) for admin_id in env.get("SUDO_USERS", "").split(",") if admin_id.strip()]
        # Add default admins
        SUDO_USERS.extend([6393380026, 5131723020, 6567513746])
    except ValueError:
        raise ValueError("❌ Error: SUDO_USERS environment variable contains invalid user IDs")
    
    # ========== PREMIUM CONFIGURATION ==========
    PREMIUM_PRICE_INR = int(env.get("PREMIUM_PRICE_INR", 199))  # ₹199/month
    PREMIUM_PRICE_USD = int(env.get("PREMIUM_PRICE_USD", 3))    # $3/month
    
    # ========== ESCROW CONFIGURATION ==========
    ESCROW_CHARGE = float(env.get("ESCROW_CHARGE", 0.5))  # $0.5 escrow charge
    MIN_ESCROW_AMOUNT = float(env.get("MIN_ESCROW_AMOUNT", 5.0))  # Minimum $5 for escrow
    
    # ========== ASSET PRICING ==========
    MIN_ASSET_PRICE = int(env.get("MIN_ASSET_PRICE", 5))   # Minimum $5
    MAX_ASSET_PRICE = int(env.get("MAX_ASSET_PRICE", 1000)) # Maximum $1000
    
    # ========== SUPPORTED LANGUAGES ==========
    SUPPORTED_LANGUAGES = {
        "en": "English",
        "hi": "हिंदी"
    }
    
    # ========== ASSET CATEGORIES ==========
    ASSET_CATEGORIES = [
        "Group",
        "Channel", 
        "Bot",
        "Other"
    ]
    
    # ========== CREATION YEARS ==========
    CREATION_YEARS = list(range(2016, 2025))  # 2016 to 2024
    
    # ========== MONTHS ==========
    MONTHS = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]
    
    # ========== PRICE OPTIONS ==========
    PRICE_OPTIONS = [5, 8, 10, 15, 20, 25, 30, 50, 75, 100]
    
    # ========== WEBHOOK SETTINGS (for deployment) ==========
    WEBHOOK_URL = str(env.get("WEBHOOK_URL", ""))
    PORT = int(env.get("PORT", 8080))
    
    # ========== FEATURE FLAGS ==========
    MAINTENANCE_MODE = env.get("MAINTENANCE_MODE", "False").lower() == "true"
    ENABLE_PREMIUM = env.get("ENABLE_PREMIUM", "True").lower() == "true"
    ENABLE_ESCROW = env.get("ENABLE_ESCROW", "True").lower() == "true"
    
    # ========== ERROR HANDLING ==========
    MAX_RETRIES = int(env.get("MAX_RETRIES", 3))
    TIMEOUT_SECONDS = int(env.get("TIMEOUT_SECONDS", 30))
    
    # ========== SUCCESS MESSAGES ==========
    SUCCESS_EMOJI = "✅"
    ERROR_EMOJI = "❌"
    WARNING_EMOJI = "⚠️"
    INFO_EMOJI = "ℹ️"
    MONEY_EMOJI = "💰"
    PREMIUM_EMOJI = "✨"
    
    @classmethod
    def get_config_summary(cls) -> str:
        """
        Returns a summary of current configuration (without sensitive data)
        """
        return f"""
🤖 **TeleShopBot Configuration Summary**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Bot Info:**
• Name: {cls.BOT_NAME}
• Username: @{cls.BOT_USERNAME}
• Description: {cls.BOT_DESCRIPTION}

**Features:**
• Premium: {'Enabled' if cls.ENABLE_PREMIUM else 'Disabled'}
• Escrow: {'Enabled' if cls.ENABLE_ESCROW else 'Disabled'}
• Maintenance: {'Active' if cls.MAINTENANCE_MODE else 'Inactive'}

**Pricing:**
• Premium: ₹{cls.PREMIUM_PRICE_INR}/month (${cls.PREMIUM_PRICE_USD})
• Escrow Charge: ${cls.ESCROW_CHARGE}
• Asset Price Range: ${cls.MIN_ASSET_PRICE} - ${cls.MAX_ASSET_PRICE}

**Database:**
• MongoDB: {'Connected' if cls.MONGO_URI else 'Not configured'}
• Database: {cls.DATABASE_NAME}

**Admins:** {len(cls.SUDO_USERS)} configured
**Languages:** {len(cls.SUPPORTED_LANGUAGES)} supported
        """
