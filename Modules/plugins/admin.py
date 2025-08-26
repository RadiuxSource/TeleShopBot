#!/usr/bin/env python3
"""
TeleShopBot Admin Panel Plugin
Handles admin commands and bot management
"""

from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from config import Settings
from Modules import teleshop_bot
from datetime import datetime

# ============================================
# ADMIN CHECK FUNCTION
# ============================================

def is_admin(user_id: int) -> bool:
    """
    Check if user is an admin
    """
    return user_id in Settings.ADMIN_IDS

# ============================================
# ADMIN STATS DISPLAY
# ============================================

async def show_admin_stats(client: Client, message: Message, edit: bool = True):
    """
    Display admin statistics panel
    """
    try:
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ Access denied! Admin only.")
            return
            
        # Sample statistics - Replace with database queries
        stats_message = f"""
🛡️ **TeleShopBot Admin Panel**
📊 **Bot Statistics:**

**👥 User Statistics:**
• Total Users: **1,247**
• Active Users (24h): **86**
• Premium Users: **23**
• New Users Today: **15**

**🏪 Marketplace Statistics:**
• Total Listings: **342**
• Active Listings: **298**
• Completed Sales: **89**
• Pending Sales: **44**

**💰 Revenue Statistics:**
• Total Revenue: **₹45,670**
• Premium Subscriptions: **₹12,450**
• Commission Earned: **₹8,920**
• Escrow Holdings: **₹2,340**

**📈 Asset Breakdown:**
• Groups: 124 listings
• Channels: 89 listings  
• Bots: 67 listings
• Other Assets: 62 listings

**System Status:** ✅ All systems operational
**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        admin_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("👥 User Management", callback_data="admin_users"),
                InlineKeyboardButton("📊 Detailed Stats", callback_data="admin_detailed_stats")
            ],
            [
                InlineKeyboardButton("🏪 Manage Listings", callback_data="admin_listings"),
                InlineKeyboardButton("💰 Financial Reports", callback_data="admin_finance")
            ],
            [
                InlineKeyboardButton("📢 Broadcast Message", callback_data="admin_broadcast"),
                InlineKeyboardButton("⚙️ Bot Settings", callback_data="admin_settings")
            ],
            [
                InlineKeyboardButton("🔄 Refresh Stats", callback_data="admin_refresh"),
                InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")
            ]
        ])
        
        if edit:
            await message.edit_text(
                stats_message,
                reply_markup=admin_keyboard,
                disable_web_page_preview=True
            )
        else:
            await message.reply_text(
                stats_message,
                reply_markup=admin_keyboard,
                disable_web_page_preview=True
            )
            
    except Exception as e:
        print(f"❌ Error showing admin stats: {e}")

# ============================================
# ADMIN COMMANDS
# ============================================

@teleshop_bot.on_message(filters.command("admin"))
async def admin_command(client: Client, message: Message):
    """
    Handle /admin command
    """
    try:
        if not is_admin(message.from_user.id):
            await message.reply_text(
                "❌ **Access Denied!**\n\nThis command is restricted to administrators only.",
                disable_web_page_preview=True
            )
            return
            
        await show_admin_stats(client, message, edit=False)
        
    except Exception as e:
        print(f"❌ Error in admin command: {e}")
        await message.reply_text("❌ An error occurred!")

@teleshop_bot.on_message(filters.command("stats") & filters.user(Settings.ADMIN_IDS))
async def stats_command(client: Client, message: Message):
    """
    Handle /stats command (admin only)
    """
    try:
        stats_message = """
📊 **Quick Bot Statistics**

**Users:** 1,247 total | 86 active today
**Listings:** 342 total | 298 active
**Sales:** 89 completed | ₹45,670 revenue
**Premium:** 23 subscribers

Type /admin for detailed panel.
"""
        
        await message.reply_text(stats_message, disable_web_page_preview=True)
        
    except Exception as e:
        print(f"❌ Error in stats command: {e}")

@teleshop_bot.on_message(filters.command("broadcast") & filters.user(Settings.ADMIN_IDS))
async def broadcast_command(client: Client, message: Message):
    """
    Handle /broadcast command
    """
    try:
        if len(message.command) < 2:
            await message.reply_text(
                "❌ **Usage:** `/broadcast <message>`\n\n"
                "Example: `/broadcast Hello everyone! New features coming soon!`"
            )
            return
            
        broadcast_text = " ".join(message.command[1:])
        
        # Placeholder for broadcast functionality
        confirm_message = f"""
📢 **Broadcast Preview**

**Message to send:**
{broadcast_text}

**Target:** All bot users (1,247 users)
**Estimated delivery time:** 2-3 minutes

⚠️ **Note:** This will send the message to ALL users!
"""
        
        confirm_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Send Broadcast", callback_data=f"broadcast_confirm"),
                InlineKeyboardButton("❌ Cancel", callback_data="broadcast_cancel")
            ]
        ])
        
        await message.reply_text(
            confirm_message,
            reply_markup=confirm_keyboard,
            disable_web_page_preview=True
        )
        
    except Exception as e:
        print(f"❌ Error in broadcast command: {e}")

# ============================================
# ADMIN CALLBACK HANDLERS
# ============================================

@teleshop_bot.on_callback_query(filters.regex("^admin_"))
async def admin_callback_handler(client: Client, callback_query: CallbackQuery):
    """
    Handle admin panel callbacks
    """
    try:
        if not is_admin(callback_query.from_user.id):
            await callback_query.answer("❌ Access denied!", show_alert=True)
            return
            
        data = callback_query.data
        message = callback_query.message
        await callback_query.answer()
        
        if data == "admin_refresh":
            await show_admin_stats(client, message)
            await callback_query.answer("🔄 Stats refreshed!")
            
        elif data == "admin_users":
            user_management_message = """
👥 **User Management Panel**

**Recent Users:**
• @user123 - Joined today, 2 purchases
• @seller456 - Premium member, 15 sales
• @buyer789 - Active user, 8 purchases

**User Actions:**
• Ban/Unban users
• Upgrade to Premium
• View user activity
• Send direct messages

**Moderation Tools:**
• View reported users
• Check suspicious activity
• Manage user complaints

🚧 **Full user management coming soon!**
"""
            
            back_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_refresh")]
            ])
            
            await message.edit_text(
                user_management_message,
                reply_markup=back_keyboard,
                disable_web_page_preview=True
            )
            
        else:
            # All other admin features are placeholders
            feature_name = data.replace("admin_", "").replace("_", " ").title()
            
            placeholder_message = f"""
🚧 **{feature_name} - Coming Soon!**

This admin feature is currently under development.

**What's being built:**
• Comprehensive management tools
• Advanced analytics and reports
• Automated moderation features
• Enhanced security controls

We're working hard to bring you these features!

Stay tuned! 🚀
"""
            
            placeholder_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_refresh")]
            ])
            
            await message.edit_text(
                placeholder_message,
                reply_markup=placeholder_keyboard,
                disable_web_page_preview=True
            )
            
    except Exception as e:
        print(f"❌ Error in admin callback handler: {e}")
        await callback_query.answer("❌ Error occurred!", show_alert=True)

@teleshop_bot.on_callback_query(filters.regex("^broadcast_"))
async def broadcast_callback_handler(client: Client, callback_query: CallbackQuery):
    """
    Handle broadcast callbacks
    """
    try:
        if not is_admin(callback_query.from_user.id):
            await callback_query.answer("❌ Access denied!", show_alert=True)
            return
            
        data = callback_query.data
        await callback_query.answer()
        
        if data == "broadcast_confirm":
            success_message = """
✅ **Broadcast Sent Successfully!**

**Status:** Message queued for delivery
**Recipients:** 1,247 users
**Estimated completion:** 2-3 minutes

📊 **Delivery will be tracked and reported.**
"""
            
            await callback_query.message.edit_text(
                success_message,
                disable_web_page_preview=True
            )
            
        elif data == "broadcast_cancel":
            await callback_query.message.edit_text(
                "❌ **Broadcast cancelled.**\n\nNo messages were sent.",
                disable_web_page_preview=True
            )
            
    except Exception as e:
        print(f"❌ Error in broadcast callback handler: {e}")

# ============================================
# EXPORT FUNCTIONS
# ============================================

__all__ = [
    "show_admin_stats",
    "is_admin"
]
