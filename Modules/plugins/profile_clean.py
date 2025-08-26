#!/usr/bin/env python3
"""
TeleShopBot Profile Plugin
Handles user profile and account management
"""

from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from config import Settings
from Modules import teleshop_bot
import datetime

# ============================================
# PROFILE DISPLAY FUNCTIONS
# ============================================

async def show_user_profile(client: Client, message: Message, edit: bool = True):
    """
    Display user's profile with stats and listings
    """
    try:
        user_id = message.from_user.id if hasattr(message, 'from_user') else message.chat.id
        user = await client.get_users(user_id)
        
        # Sample user data - in production this would come from database
        user_data = {
            "premium": False,
            "listings": 3,
            "purchases": 7,
            "revenue": 125.50,
            "spent": 89.00,
            "joined": "2024-01-15",
            "rating": 4.8,
            "language": "English"
        }
        
        # Calculate member since
        try:
            joined_date = datetime.datetime.strptime(user_data.get("joined", "2024-01-01"), "%Y-%m-%d")
            days_since = (datetime.datetime.now() - joined_date).days
        except:
            days_since = 0
        
        profile_message = f"""
👤 **Your Profile**

**🆔 Account Info:**
• Name: {user.first_name} {user.last_name or ''}
• Username: @{user.username or 'Not set'}  
• User ID: `{user_id}`
• Member since: {days_since} days ago
• Status: {'✨ Premium' if user_data.get('premium') else '🆓 Free'}

**📊 Statistics:**
• 📦 Assets Listed: {user_data.get('listings', 0)}
• 🛒 Purchases Made: {user_data.get('purchases', 0)}
• 💰 Revenue Earned: ${user_data.get('revenue', 0):.2f}
• 💳 Total Spent: ${user_data.get('spent', 0):.2f}
• ⭐ Rating: {user_data.get('rating', 0)}/5.0

**⚙️ Settings:**
• 🌐 Language: {user_data.get('language', 'English')}
• 🔔 Notifications: Enabled
"""
        
        profile_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📦 My Listings", callback_data="profile_listings"),
                InlineKeyboardButton("🛒 My Purchases", callback_data="profile_purchases")
            ],
            [
                InlineKeyboardButton("📈 Transaction History", callback_data="profile_transactions"),
                InlineKeyboardButton("⚙️ Account Settings", callback_data="profile_settings")
            ],
            [
                InlineKeyboardButton("✨ Upgrade to Premium" if not user_data.get('premium') else "✨ Premium Status", 
                                   callback_data="main_premium")
            ],
            [
                InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")
            ]
        ])
        
        if edit:
            await message.edit_text(
                profile_message,
                reply_markup=profile_keyboard,
                disable_web_page_preview=True
            )
        else:
            await message.reply_text(
                profile_message,
                reply_markup=profile_keyboard,
                disable_web_page_preview=True
            )
            
    except Exception as e:
        print(f"❌ Error showing user profile: {e}")
        error_message = "❌ Error loading profile. Please try again."
        try:
            if edit:
                await message.edit_text(error_message)
            else:
                await message.reply_text(error_message)
        except:
            pass

async def show_user_listings(client: Client, message: Message):
    """
    Show user's asset listings
    """
    try:
        user_id = message.from_user.id if hasattr(message, 'from_user') else message.chat.id
        
        # Sample listings data
        listings = [
            {"name": "Tech Community Group", "type": "Group", "price": 25, "status": "Active", "date": "2024-01-20"},
            {"name": "Trading Signals Channel", "type": "Channel", "price": 35, "status": "Sold", "date": "2024-01-18"},
            {"name": "Reminder Bot", "type": "Bot", "price": 15, "status": "Under Review", "date": "2024-01-15"}
        ]
        
        if not listings:
            no_listings_message = """
📦 **Your Listings**

You haven't listed any assets yet.

**Ready to start selling?**
• Create your first listing
• Earn money from your digital assets
• Join thousands of successful sellers

Start selling now!
"""
            listings_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("💰 Start Selling", callback_data="main_sell")],
                [InlineKeyboardButton("🔙 Back to Profile", callback_data="main_profile")]
            ])
            
            await message.edit_text(
                no_listings_message,
                reply_markup=listings_keyboard,
                disable_web_page_preview=True
            )
            return
        
        listings_message = "📦 **Your Asset Listings**\n\n"
        
        for i, listing in enumerate(listings, 1):
            status_emoji = {"Active": "🟢", "Sold": "✅", "Under Review": "🟡", "Rejected": "❌"}
            emoji = status_emoji.get(listing["status"], "⚪")
            
            listings_message += f"""**{i}. {listing['name']}**
• Type: {listing['type']}
• Price: ${listing['price']}
• Status: {emoji} {listing['status']}
• Listed: {listing['date']}

"""
        
        listings_message += "\n💡 **Tips:**\n• Active listings are visible to buyers\n• Edit pricing to increase sales\n• Premium users get featured placement"
        
        listings_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 Listing Analytics", callback_data="profile_analytics")],
            [InlineKeyboardButton("💰 Create New Listing", callback_data="main_sell")],
            [InlineKeyboardButton("🔙 Back to Profile", callback_data="main_profile")]
        ])
        
        await message.edit_text(
            listings_message,
            reply_markup=listings_keyboard,
            disable_web_page_preview=True
        )
        
    except Exception as e:
        print(f"❌ Error showing user listings: {e}")
        await message.edit_text("❌ Error loading listings.")

# ============================================
# CALLBACK QUERY HANDLERS
# ============================================

@teleshop_bot.on_callback_query(filters.regex("^profile_"))
async def profile_callback_handler(client: Client, callback_query: CallbackQuery):
    """
    Handle profile-related callback queries
    """
    try:
        data = callback_query.data
        message = callback_query.message
        await callback_query.answer()
        
        if data == "profile_listings":
            await show_user_listings(client, message)
            
        elif data == "profile_purchases":
            placeholder_message = """
🚧 **Purchase History - Coming Soon!**

This feature is currently under development.

**What's coming:**
• Complete purchase history
• Download purchased assets
• Rate and review sellers
• Reorder functionality

Stay tuned! 🚀
"""
            back_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Profile", callback_data="main_profile")]
            ])
            
            await message.edit_text(
                placeholder_message,
                reply_markup=back_keyboard,
                disable_web_page_preview=True
            )
            
        elif data == "profile_transactions":
            placeholder_message = """
🚧 **Transaction History - Coming Soon!**

This feature is currently under development.

**What's coming:**
• Detailed transaction history
• Revenue analytics
• Export functionality
• Tax reporting tools

Stay tuned! 🚀
"""
            back_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Profile", callback_data="main_profile")]
            ])
            
            await message.edit_text(
                placeholder_message,
                reply_markup=back_keyboard,
                disable_web_page_preview=True
            )
            
        elif data == "profile_settings":
            placeholder_message = """
🚧 **Account Settings - Coming Soon!**

This feature is currently under development.

**What's coming:**
• Profile customization
• Notification preferences
• Privacy settings
• Payment methods

Stay tuned! 🚀
"""
            back_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Profile", callback_data="main_profile")]
            ])
            
            await message.edit_text(
                placeholder_message,
                reply_markup=back_keyboard,
                disable_web_page_preview=True
            )
            
        elif data == "profile_analytics":
            placeholder_message = """
🚧 **Analytics Dashboard - Coming Soon!**

This feature is currently under development.

**What's coming:**
• Listing performance metrics
• View count analytics
• Revenue tracking
• Market insights

Stay tuned! 🚀
"""
            back_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Listings", callback_data="profile_listings")]
            ])
            
            await message.edit_text(
                placeholder_message,
                reply_markup=back_keyboard,
                disable_web_page_preview=True
            )
            
    except Exception as e:
        print(f"❌ Error in profile callback handler: {e}")
        await callback_query.answer("❌ Error occurred!", show_alert=True)

# ============================================
# EXPORT FUNCTIONS
# ============================================

__all__ = [
    "show_user_profile",
    "show_user_listings"
]
