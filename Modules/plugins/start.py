#!/usr/bin/env python3
"""
TeleShopBot Start Plugin
Handles the main start command and core navigation
"""

from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from config import Settings
from database import add_served_user
from Modules import teleshop_bot, BOT_NAME, BOT_USERNAME

# ============================================
# START MESSAGE AND WELCOME SCREEN
# ============================================

start_message = f"""
👋 **Welcome to the Telegram Buy & Sell Bot!**

With this bot, you can easily buy or sell **Telegram Groups**, **Channels**, **Bots**, and more digital assets.

🛍️ **What can you do here?**
• 🛒 **Buy** premium Telegram assets
• 💰 **Sell** your own digital assets
• 👤 **Manage** your profile and transactions
• ✨ **Upgrade** to Premium for exclusive benefits
• ⚙️ **Customize** your experience

**Please choose an option below:**
"""

# Main menu keyboard
main_menu_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🛒 BUY", callback_data="main_buy"),
        InlineKeyboardButton("💰 SELL", callback_data="main_sell")
    ],
    [
        InlineKeyboardButton("👤 MY PROFILE", callback_data="main_profile"),
        InlineKeyboardButton("⚙️ SETTINGS", callback_data="main_settings")
    ],
    [
        InlineKeyboardButton("✨ PREMIUM", callback_data="main_premium")
    ],
    [
        InlineKeyboardButton("🆘 Support", url=Settings.SUPPORT_CHAT),
        InlineKeyboardButton("📢 Updates", url=Settings.UPDATES_CHANNEL)
    ]
])

# Help text
help_text = """
🆘 **TeleShopBot Help & Commands**

**📋 Basic Commands:**
• `/start` - Start the bot and show main menu
• `/help` - Show this help message
• `/profile` - View your profile
• `/buy` - Quick access to buy assets
• `/sell` - Quick access to sell assets
• `/settings` - Bot settings and preferences
• `/premium` - Premium features
• `/cancel` - Cancel current operation

**🛒 Buying Process:**
1. Choose asset type (Group/Channel/Bot/Other)
2. Select creation year and month
3. Browse available assets
4. Complete purchase with escrow protection

**💰 Selling Process:**
1. Choose what to sell
2. Set creation details and price
3. Choose direct sale or marketplace
4. Optional escrow service for safety

**✨ Premium Benefits:**
• Priority in buying and selling
• Free escrow support
• Featured listings
• No extra commissions
• High-rate group notifications

**🔒 Safety Features:**
• Escrow service for secure transactions
• Verified sellers and buyers
• Transaction history tracking
• 24/7 support team

**💡 Need more help?**
Contact our support team: {Settings.SUPPORT_CHAT}
"""

# ============================================
# COMMAND HANDLERS
# ============================================

@teleshop_bot.on_message(filters.command(["start"]) & filters.private)
async def start_command(client: Client, message: Message):
    """
    Handle /start command - Main entry point
    """
    try:
        # Add user to database
        await add_served_user(message.from_user.id)
        
        # Get user info
        user_name = message.from_user.first_name
        user_id = message.from_user.id
        
        # Log user start
        print(f"👤 User started bot: {user_name} (ID: {user_id})")
        
        # Send welcome message
        await message.reply_text(
            start_message,
            reply_markup=main_menu_keyboard,
            disable_web_page_preview=True
        )
        
    except Exception as e:
        print(f"❌ Error in start command: {e}")
        await message.reply_text(
            "❌ **Error occurred!** Please try again or contact support.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🆘 Support", url=Settings.SUPPORT_CHAT)
            ]])
        )

@teleshop_bot.on_message(filters.command(["help"]) & filters.private)
async def help_command(client: Client, message: Message):
    """
    Handle /help command
    """
    try:
        back_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]
        ])
        
        await message.reply_text(
            help_text,
            reply_markup=back_keyboard,
            disable_web_page_preview=True
        )
        
    except Exception as e:
        print(f"❌ Error in help command: {e}")
        await message.reply_text("❌ Error occurred! Please try again.")

@teleshop_bot.on_message(filters.command(["buy"]) & filters.private)
async def quick_buy_command(client: Client, message: Message):
    """
    Quick access to buy menu
    """
    try:
        from Modules.plugins.buy import show_buy_menu
        await show_buy_menu(client, message, edit=False)
    except Exception as e:
        print(f"❌ Error in buy command: {e}")
        await message.reply_text("❌ Error occurred! Please try again.")

@teleshop_bot.on_message(filters.command(["sell"]) & filters.private)
async def quick_sell_command(client: Client, message: Message):
    """
    Quick access to sell menu
    """
    try:
        from Modules.plugins.sell import show_sell_menu
        await show_sell_menu(client, message, edit=False)
    except Exception as e:
        print(f"❌ Error in sell command: {e}")
        await message.reply_text("❌ Error occurred! Please try again.")

@teleshop_bot.on_message(filters.command(["profile"]) & filters.private)
async def quick_profile_command(client: Client, message: Message):
    """
    Quick access to profile
    """
    try:
        from Modules.plugins.profile import show_user_profile
        await show_user_profile(client, message, edit=False)
    except Exception as e:
        print(f"❌ Error in profile command: {e}")
        await message.reply_text("❌ Error occurred! Please try again.")

# ============================================
# CALLBACK QUERY HANDLERS
# ============================================

@teleshop_bot.on_callback_query(filters.regex("^main_"))
async def main_menu_callbacks(client: Client, callback_query: CallbackQuery):
    """
    Handle main menu button clicks
    """
    try:
        data = callback_query.data
        message = callback_query.message
        user_id = callback_query.from_user.id
        
        # Answer callback to remove loading state
        await callback_query.answer()
        
        if data == "main_buy":
            from Modules.plugins.buy import show_buy_menu
            await show_buy_menu(client, message, edit=True)
            
        elif data == "main_sell":
            from Modules.plugins.sell import show_sell_menu
            await show_sell_menu(client, message, edit=True)
            
        elif data == "main_profile":
            from Modules.plugins.profile import show_user_profile
            await show_user_profile(client, message, edit=True)
            
        elif data == "main_settings":
            from Modules.plugins.settings import show_settings_menu
            await show_settings_menu(client, message, edit=True)
            
        elif data == "main_premium":
            from Modules.plugins.premium import show_premium_info
            await show_premium_info(client, message, edit=True)
            
    except Exception as e:
        print(f"❌ Error in main menu callback: {e}")
        await callback_query.answer("❌ Error occurred! Please try again.", show_alert=True)

@teleshop_bot.on_callback_query(filters.regex("back_to_main"))
async def back_to_main_menu(client: Client, callback_query: CallbackQuery):
    """
    Handle back to main menu
    """
    try:
        await callback_query.answer()
        await callback_query.message.edit_text(
            start_message,
            reply_markup=main_menu_keyboard,
            disable_web_page_preview=True
        )
    except Exception as e:
        print(f"❌ Error going back to main menu: {e}")
        await callback_query.answer("❌ Error occurred!", show_alert=True)

# ============================================
# GROUP COMMAND HANDLERS
# ============================================

@teleshop_bot.on_message(filters.command(["start", "help"]) & filters.group)
async def group_start_command(client: Client, message: Message):
    """
    Handle start/help in groups
    """
    try:
        group_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "💬 Open in Private Chat", 
                url=f"https://t.me/{BOT_USERNAME}?start=group_{message.chat.id}"
            )]
        ])
        
        await message.reply_text(
            f"👋 **Hello!** I'm {BOT_NAME}\n\n"
            "🛍️ I help users buy and sell **Telegram Groups**, **Channels**, **Bots** and other digital assets.\n\n"
            "📱 For full functionality, please use me in **private chat**.",
            reply_markup=group_keyboard,
            disable_web_page_preview=True
        )
        
    except Exception as e:
        print(f"❌ Error in group start command: {e}")

# ============================================
# UTILITY FUNCTIONS
# ============================================

def get_main_keyboard():
    """
    Get the main menu keyboard
    """
    return main_menu_keyboard

def get_start_message():
    """
    Get the start message text
    """
    return start_message

# Export functions for other modules
__all__ = [
    "get_main_keyboard",
    "get_start_message",
    "main_menu_keyboard",
    "start_message"
]
