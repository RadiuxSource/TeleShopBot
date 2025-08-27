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

@teleshop_bot.on_message(filters.command(["profile"]) & filters.private)
async def profile_command(client: Client, message: Message):
    await message.reply_text(
        "👤 My Profile - Coming soon!",
        reply_markup=main_menu_keyboard
    )

@teleshop_bot.on_message(filters.command(["settings"]) & filters.private)
async def settings_command(client: Client, message: Message):
    await message.reply_text(
        "⚙️ Settings - Coming soon!",
        reply_markup=main_menu_keyboard
    )

# ============================================
# REPLY KEYBOARD HANDLERS
# ============================================
@teleshop_bot.on_message(filters.regex(r"^(🛒\s*buy\s*groups|💰\s*sell\s*groups|🛡️\s*escrow\s*service|👤\s*my\s*profile|⚙️\s*settings|🆘\s*help|🔙\s*back\s*to\s*main\s*menu)$", re.IGNORECASE) & filters.private)
async def keyboard_handler(client: Client, message: Message):
    text = message.text.strip().lower()
    if "buy groups" in text:
        await buy_command(client, message)
    elif "sell groups" in text:
        await sell_command(client, message)
    elif "escrow service" in text:
        await escrow_command(client, message)
    elif "my profile" in text:
        await profile_command(client, message)
    elif "settings" in text:
        await settings_command(client, message)
    elif "help" in text:
        await help_command(client, message)
    elif "back to main menu" in text:
        await start_command(client, message)
    else:
        await message.reply_text(
            "❓ Unknown option. Please use the menu below.",
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
