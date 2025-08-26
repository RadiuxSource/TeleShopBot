#!/usr/bin/env python3
"""
TeleShopBot Buy Plugin
Handles buying functionality for digital assets
"""

from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from config import Settings
from database import get_user_data, update_user_data
from Modules import teleshop_bot

# ============================================
# BUY FLOW MESSAGES AND KEYBOARDS
# ============================================

buy_main_message = """
🛒 **Buy Digital Assets**

Choose the type of asset you want to purchase:

**Available Categories:**
• 📱 **Group** - Telegram Groups with members
• 📢 **Channel** - Telegram Channels with subscribers  
• 🤖 **Bot** - Telegram Bots with features
• 📦 **Any Other** - Other digital assets

Select a category below to continue:
"""

buy_main_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("📱 Group", callback_data="buy_type_group"),
        InlineKeyboardButton("📢 Channel", callback_data="buy_type_channel")
    ],
    [
        InlineKeyboardButton("🤖 Bot", callback_data="buy_type_bot"),
        InlineKeyboardButton("📦 Any Other", callback_data="buy_type_other")
    ],
    [
        InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")
    ]
])

year_selection_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("2016", callback_data="buy_year_2016"),
        InlineKeyboardButton("2017", callback_data="buy_year_2017"),
        InlineKeyboardButton("2018", callback_data="buy_year_2018")
    ],
    [
        InlineKeyboardButton("2019", callback_data="buy_year_2019"),
        InlineKeyboardButton("2020", callback_data="buy_year_2020"),
        InlineKeyboardButton("2021", callback_data="buy_year_2021")
    ],
    [
        InlineKeyboardButton("2022", callback_data="buy_year_2022"),
        InlineKeyboardButton("2023", callback_data="buy_year_2023"),
        InlineKeyboardButton("2024", callback_data="buy_year_2024")
    ],
    [
        InlineKeyboardButton("🔙 Back", callback_data="main_buy")
    ]
])

month_selection_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("Jan", callback_data="buy_month_Jan"),
        InlineKeyboardButton("Feb", callback_data="buy_month_Feb"),
        InlineKeyboardButton("Mar", callback_data="buy_month_Mar")
    ],
    [
        InlineKeyboardButton("Apr", callback_data="buy_month_Apr"),
        InlineKeyboardButton("May", callback_data="buy_month_May"),
        InlineKeyboardButton("Jun", callback_data="buy_month_Jun")
    ],
    [
        InlineKeyboardButton("Jul", callback_data="buy_month_Jul"),
        InlineKeyboardButton("Aug", callback_data="buy_month_Aug"),
        InlineKeyboardButton("Sep", callback_data="buy_month_Sep")
    ],
    [
        InlineKeyboardButton("Oct", callback_data="buy_month_Oct"),
        InlineKeyboardButton("Nov", callback_data="buy_month_Nov"),
        InlineKeyboardButton("Dec", callback_data="buy_month_Dec")
    ],
    [
        InlineKeyboardButton("🔙 Back", callback_data="buy_select_year")
    ]
])

# ============================================
# SAMPLE DATA FOR DEMONSTRATION
# ============================================

sample_assets = {
    "group": {
        "2024": {
            "Jan": [
                {"name": "Tech Developers Group", "price": 15, "members": 1500, "description": "Active tech community"},
                {"name": "Crypto Trading Hub", "price": 25, "members": 2800, "description": "Premium crypto signals"},
                {"name": "Business Network", "price": 20, "members": 1200, "description": "Professional networking"}
            ],
            "Feb": [
                {"name": "Marketing Experts", "price": 18, "members": 900, "description": "Digital marketing professionals"},
                {"name": "Startup Community", "price": 12, "members": 750, "description": "Entrepreneur networking group"}
            ]
        },
        "2023": {
            "Dec": [
                {"name": "Vintage Tech Group", "price": 30, "members": 3500, "description": "Established tech community"},
                {"name": "Investment Circle", "price": 45, "members": 2200, "description": "High-quality investment discussions"}
            ]
        }
    },
    "channel": {
        "2024": {
            "Jan": [
                {"name": "Tech News Daily", "price": 35, "subscribers": 5000, "description": "Daily tech updates"},
                {"name": "Motivation Hub", "price": 20, "subscribers": 3200, "description": "Daily motivation content"}
            ]
        }
    },
    "bot": {
        "2024": {
            "Jan": [
                {"name": "Trading Bot Pro", "price": 50, "users": 800, "description": "Automated trading bot"},
                {"name": "Reminder Bot", "price": 15, "users": 1200, "description": "Smart reminder system"}
            ]
        }
    }
}

# ============================================
# MAIN FUNCTIONS
# ============================================

async def show_buy_menu(client: Client, message: Message, edit: bool = True):
    """
    Show the main buy menu
    """
    try:
        if edit:
            await message.edit_text(
                buy_main_message,
                reply_markup=buy_main_keyboard,
                disable_web_page_preview=True
            )
        else:
            await message.reply_text(
                buy_main_message,
                reply_markup=buy_main_keyboard,
                disable_web_page_preview=True
            )
    except Exception as e:
        print(f"❌ Error showing buy menu: {e}")

async def show_year_selection(client: Client, message: Message, asset_type: str):
    """
    Show year selection for the chosen asset type
    """
    try:
        year_message = f"""
📅 **Select Creation Year**

You chose: **{asset_type.title()}**

Please select the year of creation:
"""
        
        await message.edit_text(
            year_message,
            reply_markup=year_selection_keyboard,
            disable_web_page_preview=True
        )
    except Exception as e:
        print(f"❌ Error showing year selection: {e}")

async def show_month_selection(client: Client, message: Message, asset_type: str, year: str):
    """
    Show month selection for the chosen asset type and year
    """
    try:
        month_message = f"""
📅 **Select Creation Month**

**Asset Type:** {asset_type.title()}
**Year:** {year}

Please select the month:
"""
        
        await message.edit_text(
            month_message,
            reply_markup=month_selection_keyboard,
            disable_web_page_preview=True
        )
    except Exception as e:
        print(f"❌ Error showing month selection: {e}")

async def show_available_assets(client: Client, message: Message, asset_type: str, year: str, month: str):
    """
    Show available assets based on selection
    """
    try:
        # Get assets from sample data
        assets = sample_assets.get(asset_type, {}).get(year, {}).get(month, [])
        
        if not assets:
            no_assets_message = f"""
😔 **No Assets Available**

**Search Criteria:**
• Type: {asset_type.title()}
• Year: {year}
• Month: {month}

Sorry, no assets matching your criteria are currently available.

**What you can do:**
• Try different year/month combination
• Contact our team to list your requirements
• Check our premium listings
"""
            back_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Try Again", callback_data="main_buy")],
                [InlineKeyboardButton("✨ Premium Listings", callback_data="main_premium")],
                [InlineKeyboardButton("🆘 Contact Us", url=Settings.SUPPORT_CHAT)]
            ])
            
            await message.edit_text(
                no_assets_message,
                reply_markup=back_keyboard,
                disable_web_page_preview=True
            )
            return
        
        # Build assets list message
        assets_message = f"""
✅ **Available {asset_type.title()}s**

**Search Results for {year} - {month}:**

"""
        
        # Create inline buttons for each asset
        asset_buttons = []
        for i, asset in enumerate(assets, 1):
            assets_message += f"{i}. **{asset['name']}** - ${asset['price']}\n"
            
            if asset_type == "group":
                assets_message += f"   👥 Members: {asset['members']:,}\n"
            elif asset_type == "channel":
                assets_message += f"   📊 Subscribers: {asset['subscribers']:,}\n"
            elif asset_type == "bot":
                assets_message += f"   👤 Users: {asset['users']:,}\n"
                
            assets_message += f"   📝 {asset['description']}\n\n"
            
            # Add buy button for each asset
            asset_buttons.append([
                InlineKeyboardButton(
                    f"🛒 Buy {asset['name']} (${asset['price']})", 
                    callback_data=f"buy_asset_{i-1}_{asset_type}_{year}_{month}"
                )
            ])
        
        # Add navigation buttons
        asset_buttons.extend([
            [InlineKeyboardButton("🔄 Search Again", callback_data="main_buy")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]
        ])
        
        assets_keyboard = InlineKeyboardMarkup(asset_buttons)
        
        await message.edit_text(
            assets_message,
            reply_markup=assets_keyboard,
            disable_web_page_preview=True
        )
        
    except Exception as e:
        print(f"❌ Error showing available assets: {e}")

async def handle_asset_purchase(client: Client, callback_query: CallbackQuery, asset_data: list):
    """
    Handle the asset purchase process
    """
    try:
        asset_index, asset_type, year, month = asset_data
        asset_index = int(asset_index)
        
        # Get the specific asset
        assets = sample_assets.get(asset_type, {}).get(year, {}).get(month, [])
        if asset_index >= len(assets):
            await callback_query.answer("❌ Asset not found!", show_alert=True)
            return
        
        asset = assets[asset_index]
        user_id = callback_query.from_user.id
        
        purchase_message = f"""
🛒 **Purchase Confirmation**

**Asset Details:**
• Name: {asset['name']}
• Type: {asset_type.title()}
• Price: ${asset['price']}
• Year: {year}
• Month: {month}

"""
        
        if asset_type == "group":
            purchase_message += f"• Members: {asset['members']:,}\n"
        elif asset_type == "channel":
            purchase_message += f"• Subscribers: {asset['subscribers']:,}\n"
        elif asset_type == "bot":
            purchase_message += f"• Users: {asset['users']:,}\n"
            
        purchase_message += f"""
• Description: {asset['description']}

**💰 Payment Options:**
• Direct Payment: ${asset['price']}
• With Escrow: ${asset['price'] + Settings.ESCROW_CHARGE} (includes ${Settings.ESCROW_CHARGE} escrow fee)

**🔒 Escrow Benefits:**
• 100% secure transaction
• Money held until asset transfer complete
• Full refund if seller doesn't deliver

Choose your payment method:
"""
        
        purchase_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                f"💳 Pay ${asset['price']} (Direct)", 
                callback_data=f"pay_direct_{asset_index}_{asset_type}_{year}_{month}"
            )],
            [InlineKeyboardButton(
                f"🔒 Pay ${asset['price'] + Settings.ESCROW_CHARGE} (Escrow)", 
                callback_data=f"pay_escrow_{asset_index}_{asset_type}_{year}_{month}"
            )],
            [InlineKeyboardButton("🔙 Back", callback_data="main_buy")]
        ])
        
        await callback_query.message.edit_text(
            purchase_message,
            reply_markup=purchase_keyboard,
            disable_web_page_preview=True
        )
        
    except Exception as e:
        print(f"❌ Error handling asset purchase: {e}")
        await callback_query.answer("❌ Error occurred!", show_alert=True)

# ============================================
# CALLBACK QUERY HANDLERS
# ============================================

@teleshop_bot.on_callback_query(filters.regex("^buy_"))
async def buy_callback_handler(client: Client, callback_query: CallbackQuery):
    """
    Handle all buy-related callback queries
    """
    try:
        data = callback_query.data
        message = callback_query.message
        await callback_query.answer()
        
        if data.startswith("buy_type_"):
            # Asset type selection
            asset_type = data.replace("buy_type_", "")
            await show_year_selection(client, message, asset_type)
            
        elif data.startswith("buy_year_"):
            # Year selection - need to get asset type from user session
            year = data.replace("buy_year_", "")
            # For now, using a default asset type. In production, store user state
            asset_type = "group"  # This should come from user session
            await show_month_selection(client, message, asset_type, year)
            
        elif data.startswith("buy_month_"):
            # Month selection
            month = data.replace("buy_month_", "")
            # For now, using defaults. In production, get from user session
            asset_type = "group"  # This should come from user session
            year = "2024"  # This should come from user session
            await show_available_assets(client, message, asset_type, year, month)
            
        elif data.startswith("buy_asset_"):
            # Asset selection for purchase
            parts = data.replace("buy_asset_", "").split("_")
            await handle_asset_purchase(client, callback_query, parts)
            
        elif data == "buy_select_year":
            # Go back to year selection
            await show_year_selection(client, message, "group")  # Should get from session
            
    except Exception as e:
        print(f"❌ Error in buy callback handler: {e}")
        await callback_query.answer("❌ Error occurred!", show_alert=True)

@teleshop_bot.on_callback_query(filters.regex("^pay_"))
async def payment_callback_handler(client: Client, callback_query: CallbackQuery):
    """
    Handle payment-related callbacks
    """
    try:
        data = callback_query.data
        await callback_query.answer()
        
        if data.startswith("pay_direct_") or data.startswith("pay_escrow_"):
            payment_type = "direct" if data.startswith("pay_direct_") else "escrow"
            
            payment_message = f"""
💳 **Payment Processing**

**Payment Type:** {payment_type.title()}

🚧 **Payment Integration Coming Soon!**

We're currently integrating payment processors like:
• Stripe
• PayPal  
• Razorpay
• Cryptocurrency payments

For now, please contact our support team to complete your purchase manually.

**Next Steps:**
1. Contact support with your order details
2. Make payment via agreed method
3. Receive your asset within 24 hours

Thank you for your patience! 🙏
"""
            
            payment_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("💬 Contact Support", url=Settings.SUPPORT_CHAT)],
                [InlineKeyboardButton("🔙 Back to Buy", callback_data="main_buy")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
            ])
            
            await callback_query.message.edit_text(
                payment_message,
                reply_markup=payment_keyboard,
                disable_web_page_preview=True
            )
            
    except Exception as e:
        print(f"❌ Error in payment callback handler: {e}")
        await callback_query.answer("❌ Payment error occurred!", show_alert=True)

# ============================================
# EXPORT FUNCTIONS
# ============================================

__all__ = [
    "show_buy_menu",
    "show_year_selection", 
    "show_month_selection",
    "show_available_assets",
    "handle_asset_purchase"
]
