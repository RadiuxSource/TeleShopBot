#!/usr/bin/env python3
"""
Group Buy/Sell Bot - Start Plugin (Reply Keyboard Version)
Handles /start, /help, and main menu navigation for group marketplace
"""

from pyrogram import filters, Client
from pyrogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from Modules import teleshop_bot
from Modules.modules.buy import buy_command
from Modules.modules.sell import sell_command
from Modules.modules.profile import profile_command
from Modules.modules.settings import settings_command
from database import add_served_user
import re

BOT_NAME = "GroupMarketBot"
BOT_USERNAME = "GroupMarketBot"

# ============================================
# START MESSAGE AND WELCOME SCREEN
# ============================================
start_message = f"""
👋 **Welcome to GroupMarketBot!**

Here you can **buy** or **sell** Telegram groups safely, with optional **escrow service** for secure transactions.

**What do you want to do?**
"""

main_menu_keyboard = ReplyKeyboardMarkup(
    [
        [KeyboardButton("🛒 Buy Groups"), KeyboardButton("💰 Sell Groups")],
        [KeyboardButton("🛡️ Escrow Service")],
        [KeyboardButton("👤 My Profile"), KeyboardButton("⚙️ Settings")],
        [KeyboardButton("🆘 Help")],
    ],
    resize_keyboard=True
)

help_text = """
🆘 **Help & Commands**

• /start — Show main menu
• /buy — Browse groups for sale
• /sell — List your group for sale
• /escrow — Learn about escrow service
• /profile — View your profile and transactions
• /settings — Change preferences

**How it works:**
- To buy, browse listings and initiate a purchase.
- To sell, create a listing with group details.
- Use escrow for secure group transfers.
- Contact an admin for disputes or support.
"""

# ============================================
# COMMAND HANDLERS
# ============================================

@teleshop_bot.on_message(filters.command(["start"]) & filters.private)
async def start_command(client: Client, message: Message):
    try:
        await add_served_user(message.from_user.id, client)
        await message.reply_text(
            start_message,
            reply_markup=main_menu_keyboard,
            disable_web_page_preview=True
        )
    except Exception as e:
        await message.reply_text("❌ Error occurred! Please try again.")

@teleshop_bot.on_message(filters.command(["help"]) & filters.private)
async def help_command(client: Client, message: Message):
    try:
        await message.reply_text(
            help_text,
            reply_markup=main_menu_keyboard,
            disable_web_page_preview=True
        )
    except Exception as e:
        await message.reply_text("❌ Error occurred! Please try again.")


@teleshop_bot.on_message(filters.command(["escrow"]) & filters.private)
async def escrow_command(client: Client, message: Message):
    await message.reply_text(
        "🛡️ Escrow Service\n\nFunds are held securely until the group is transferred. Ask for escrow during buy/sell!",
        reply_markup=main_menu_keyboard
    )



# ============================================
# REPLY KEYBOARD HANDLERS
# ============================================
@teleshop_bot.on_message(filters.text & filters.private & ~filters.command(["start", "help", "buy", "sell", "profile", "settings", "escrow"]))
async def keyboard_handler(client: Client, message: Message):
    try:
        text = message.text.strip().lower()
        print(f"Keyboard handler received: '{text}'")  # Debug log
        
        # Handle keyboard buttons
        if "buy groups" in text or "🛒" in text:
            print("Processing buy groups")
            await buy_command(client, message)
            return
        elif "sell groups" in text or "💰" in text:
            print("Processing sell groups")
            await sell_command(client, message)
            return
        elif "escrow service" in text or "🛡️" in text:
            print("Processing escrow service")
            await escrow_command(client, message)
            return
        elif "my profile" in text or "👤" in text:
            print("Processing my profile")
            await profile_command(client, message)
            return
        elif "settings" in text or "⚙️" in text:
            print("Processing settings")
            await settings_command(client, message)
            return
        elif "help" in text or "🆘" in text:
            print("Processing help")
            await help_command(client, message)
            return
        elif "back to main menu" in text or "🔙" in text:
            print("Processing back to main menu")
            await start_command(client, message)
            return
        
        # If not a recognized keyboard button, don't respond
        # This allows other handlers (like anonymous chat) to process the message
        
    except Exception as e:
        print(f"Error in keyboard_handler: {e}")
        await message.reply_text(
            "❌ Error processing your request. Please try again.",
            reply_markup=main_menu_keyboard
        )

# ============================================
# GROUP COMMAND HANDLERS
# ============================================
@teleshop_bot.on_message(filters.command(["start", "help"]) & filters.group)
async def group_start_command(client: Client, message: Message):
    await message.reply_text(
        f"👋 **Hello!** I'm {BOT_NAME}\n\n"
        "🛍️ Buy & sell Telegram groups safely! For full features, use me in **private chat**.",
        disable_web_page_preview=True
    )

# ============================================
# UTILITY FUNCTIONS
# ============================================
def get_main_keyboard():
    return main_menu_keyboard

def get_start_message():
    return start_message
