#!/usr/bin/env python3
"""
TeleShopBot Sell Plugin
Handles selling functionality for digital assets
"""

from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from config import Settings
from database import get_user_data, update_user_data
from Modules import teleshop_bot

# ============================================
# SELL FLOW MESSAGES AND KEYBOARDS
# ============================================

sell_main_message = """
💰 **Sell Your Digital Assets**

Turn your digital assets into cash! We help you sell:

**What can you sell?**
• 📱 **Telegram Groups** - With active members
• 📢 **Telegram Channels** - With subscribers
• 🤖 **Telegram Bots** - With users and features
• 📦 **Other Assets** - Any digital asset you own

**Why sell with us?**
• 🔒 Secure escrow service available
• 💰 Fair market pricing
• 📈 Featured listings for premium users
• 🚀 Quick sale process
• 🛡️ Buyer protection

Choose what you want to sell:
"""

sell_main_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("📱 Group", callback_data="sell_type_group"),
        InlineKeyboardButton("📢 Channel", callback_data="sell_type_channel")
    ],
    [
        InlineKeyboardButton("🤖 Bot", callback_data="sell_type_bot"),
        InlineKeyboardButton("📦 Other", callback_data="sell_type_other")
    ],
    [
        InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")
    ]
])

sell_year_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("2016", callback_data="sell_year_2016"),
        InlineKeyboardButton("2017", callback_data="sell_year_2017"),
        InlineKeyboardButton("2018", callback_data="sell_year_2018")
    ],
    [
        InlineKeyboardButton("2019", callback_data="sell_year_2019"),
        InlineKeyboardButton("2020", callback_data="sell_year_2020"),
        InlineKeyboardButton("2021", callback_data="sell_year_2021")
    ],
    [
        InlineKeyboardButton("2022", callback_data="sell_year_2022"),
        InlineKeyboardButton("2023", callback_data="sell_year_2023"),
        InlineKeyboardButton("2024", callback_data="sell_year_2024")
    ],
    [
        InlineKeyboardButton("🔙 Back", callback_data="main_sell")
    ]
])

sell_price_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("$5", callback_data="sell_price_5"),
        InlineKeyboardButton("$8", callback_data="sell_price_8"),
        InlineKeyboardButton("$10", callback_data="sell_price_10")
    ],
    [
        InlineKeyboardButton("$15", callback_data="sell_price_15"),
        InlineKeyboardButton("$20", callback_data="sell_price_20"),
        InlineKeyboardButton("$25", callback_data="sell_price_25")
    ],
    [
        InlineKeyboardButton("$30", callback_data="sell_price_30"),
        InlineKeyboardButton("$50", callback_data="sell_price_50"),
        InlineKeyboardButton("💬 Custom Price", callback_data="sell_price_custom")
    ],
    [
        InlineKeyboardButton("🔙 Back", callback_data="sell_select_year")
    ]
])

# ============================================
# MAIN FUNCTIONS
# ============================================

async def show_sell_menu(client: Client, message: Message, edit: bool = True):
    """
    Show the main sell menu
    """
    try:
        if edit:
            await message.edit_text(
                sell_main_message,
                reply_markup=sell_main_keyboard,
                disable_web_page_preview=True
            )
        else:
            await message.reply_text(
                sell_main_message,
                reply_markup=sell_main_keyboard,
                disable_web_page_preview=True
            )
    except Exception as e:
        print(f"❌ Error showing sell menu: {e}")

async def show_sell_year_selection(client: Client, message: Message, asset_type: str):
    """
    Show year selection for selling
    """
    try:
        year_message = f"""
📅 **Asset Creation Year**

**Asset Type:** {asset_type.title()}

When was your {asset_type} created?

*This helps buyers understand the asset's age and history*
"""
        
        await message.edit_text(
            year_message,
            reply_markup=sell_year_keyboard,
            disable_web_page_preview=True
        )
    except Exception as e:
        print(f"❌ Error showing sell year selection: {e}")

async def show_sell_price_selection(client: Client, message: Message, asset_type: str, year: str):
    """
    Show price selection for selling
    """
    try:
        price_message = f"""
💰 **Set Your Price**

**Asset Details:**
• Type: {asset_type.title()}
• Created: {year}

**Please set a reasonable price for your asset:**

*Tip: Check similar listings to price competitively*
"""
        
        await message.edit_text(
            price_message,
            reply_markup=sell_price_keyboard,
            disable_web_page_preview=True
        )
    except Exception as e:
        print(f"❌ Error showing price selection: {e}")

async def show_sell_direct_question(client: Client, message: Message, asset_type: str, year: str, price: str):
    """
    Ask if user wants to sell directly to platform
    """
    try:
        direct_sale_message = f"""
🤝 **Sale Method**

**Your Asset:**
• Type: {asset_type.title()}
• Created: {year}
• Price: ${price}

**Do you want to sell this directly to us?**

**✅ Yes (Direct Sale):**
• Instant sale - no waiting
• Quick payment processing
• We handle all buyer interactions
• Guaranteed sale

**❌ No (Marketplace):**
• List on our marketplace
• Find your own buyers
• Higher potential profit
• You handle negotiations

Choose your preferred method:
"""
        
        direct_sale_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Yes - Direct Sale", callback_data=f"sell_direct_yes_{asset_type}_{year}_{price}")],
            [InlineKeyboardButton("❌ No - Marketplace", callback_data=f"sell_direct_no_{asset_type}_{year}_{price}")],
            [InlineKeyboardButton("🔙 Back", callback_data="sell_select_price")]
        ])
        
        await message.edit_text(
            direct_sale_message,
            reply_markup=direct_sale_keyboard,
            disable_web_page_preview=True
        )
    except Exception as e:
        print(f"❌ Error showing direct sale question: {e}")

async def show_escrow_question(client: Client, message: Message, asset_type: str, year: str, price: str, direct: str):
    """
    Ask about escrow service
    """
    try:
        escrow_message = f"""
🔒 **Escrow Service**

**Your Listing:**
• Type: {asset_type.title()}
• Created: {year}
• Price: ${price}
• Method: {'Direct Sale' if direct == 'yes' else 'Marketplace'}

**Do you want to use our escrow service?**

**✅ Yes - With Escrow (${Settings.ESCROW_CHARGE} fee):**
• 100% secure transaction
• Payment held until transfer complete  
• Protection against scams
• Professional mediation if needed
• Recommended for all sales

**❌ No - Without Escrow:**
• Direct buyer-seller transaction
• No transaction fees
• ⚠️ We do not take responsibility for scams
• Higher risk for both parties

Choose your preference:
"""
        
        escrow_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                f"🔒 Yes - Use Escrow (${Settings.ESCROW_CHARGE} fee)", 
                callback_data=f"sell_escrow_yes_{asset_type}_{year}_{price}_{direct}"
            )],
            [InlineKeyboardButton(
                "❌ No - Direct Transaction", 
                callback_data=f"sell_escrow_no_{asset_type}_{year}_{price}_{direct}"
            )],
            [InlineKeyboardButton("🔙 Back", callback_data="sell_select_direct")]
        ])
        
        await message.edit_text(
            escrow_message,
            reply_markup=escrow_keyboard,
            disable_web_page_preview=True
        )
    except Exception as e:
        print(f"❌ Error showing escrow question: {e}")

async def show_sell_confirmation(client: Client, message: Message, asset_data: dict):
    """
    Show final confirmation and next steps
    """
    try:
        user_id = message.chat.id if hasattr(message, 'chat') else message.from_user.id
        
        confirmation_message = f"""
✅ **Listing Created Successfully!**

**Your Asset Details:**
• 📦 Type: {asset_data['type'].title()}
• 📅 Created: {asset_data['year']}
• 💰 Price: ${asset_data['price']}
• 🤝 Method: {'Direct Sale to Us' if asset_data['direct'] == 'yes' else 'Marketplace Listing'}
• 🔒 Escrow: {'Yes (${Settings.ESCROW_CHARGE} fee)' if asset_data['escrow'] == 'yes' else 'No'}

**📋 Next Steps:**

1. **Asset Verification**
   - Our team will review your listing
   - We may ask for proof of ownership
   - Verification typically takes 2-6 hours

2. **Listing Process**
"""
        
        if asset_data['direct'] == 'yes':
            confirmation_message += """   - We'll evaluate your asset
   - If approved, instant purchase
   - Payment within 24 hours"""
        else:
            confirmation_message += """   - Asset goes live on marketplace
   - Buyers can contact you directly
   - We'll notify you of inquiries"""
            
        confirmation_message += f"""

3. **Payment & Transfer**
   - {'Escrow handles secure payment' if asset_data['escrow'] == 'yes' else 'Direct payment between parties'}
   - Asset ownership transfer
   - Transaction completion

**📞 Support:** Need help? Contact {Settings.SUPPORT_CHAT}

**⏰ Status:** Your listing is now pending review.
"""
        
        confirmation_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("👤 View My Profile", callback_data="main_profile")],
            [InlineKeyboardButton("💰 Sell Another Asset", callback_data="main_sell")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
        ])
        
        await message.edit_text(
            confirmation_message,
            reply_markup=confirmation_keyboard,
            disable_web_page_preview=True
        )
        
        # TODO: Save the listing to database
        # await save_user_listing(user_id, asset_data)
        
        # Notify admins about new listing
        if Settings.LOG_GROUP:
            admin_message = f"""
🆕 **New Asset Listing**

**User:** {user_id}
**Type:** {asset_data['type'].title()}
**Year:** {asset_data['year']}
**Price:** ${asset_data['price']}
**Direct:** {asset_data['direct']}
**Escrow:** {asset_data['escrow']}

Review and approve this listing.
"""
            try:
                await teleshop_bot.send_message(Settings.LOG_GROUP, admin_message)
            except Exception as e:
                print(f"⚠️ Could not notify admins: {e}")
        
    except Exception as e:
        print(f"❌ Error showing sell confirmation: {e}")

async def handle_other_asset_details(client: Client, message: Message):
    """
    Handle 'Other' asset type - ask for manual details
    """
    try:
        other_message = """
📦 **Other Asset Details**

You selected "Other" asset type.

**Please provide your asset details in this format:**
```
Name – Category – Price
```

**Example:**
```
Instagram Account – Social Media – 50
Website Template – Web Design – 25
Discord Bot – Software – 35
YouTube Channel – Content – 100
```

**Guidelines:**
• Be specific about what you're selling
• Include category for better discovery
• Set a reasonable price ($5 - $1000)
• Ensure you own the asset

Reply to this message with your details:
"""
        
        back_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Asset Types", callback_data="main_sell")]
        ])
        
        await message.edit_text(
            other_message,
            reply_markup=back_keyboard,
            disable_web_page_preview=True
        )
        
    except Exception as e:
        print(f"❌ Error handling other asset details: {e}")

# ============================================
# CALLBACK QUERY HANDLERS  
# ============================================

@teleshop_bot.on_callback_query(filters.regex("^sell_"))
async def sell_callback_handler(client: Client, callback_query: CallbackQuery):
    """
    Handle all sell-related callback queries
    """
    try:
        data = callback_query.data
        message = callback_query.message
        await callback_query.answer()
        
        if data.startswith("sell_type_"):
            # Asset type selection
            asset_type = data.replace("sell_type_", "")
            if asset_type == "other":
                await handle_other_asset_details(client, message)
            else:
                await show_sell_year_selection(client, message, asset_type)
                
        elif data.startswith("sell_year_"):
            # Year selection
            year = data.replace("sell_year_", "")
            # Store in user session (for now using default)
            asset_type = "group"  # Should come from user session
            await show_sell_price_selection(client, message, asset_type, year)
            
        elif data.startswith("sell_price_"):
            # Price selection
            price_data = data.replace("sell_price_", "")
            if price_data == "custom":
                # Handle custom price input
                custom_price_message = """
💰 **Custom Price**

Please reply with your desired price in USD.

**Format:** Just the number (e.g., 75)
**Range:** $5 - $1000

What's your custom price?
"""
                back_keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Prices", callback_data="sell_select_price")]
                ])
                
                await message.edit_text(
                    custom_price_message,
                    reply_markup=back_keyboard
                )
                return
            
            price = price_data
            # Get from user session  
            asset_type = "group"  # Should come from user session
            year = "2024"  # Should come from user session
            await show_sell_direct_question(client, message, asset_type, year, price)
            
        elif data.startswith("sell_direct_"):
            # Direct sale choice
            parts = data.replace("sell_direct_", "").split("_")
            direct_choice = parts[0]  # yes or no
            asset_type = parts[1] if len(parts) > 1 else "group"
            year = parts[2] if len(parts) > 2 else "2024"
            price = parts[3] if len(parts) > 3 else "10"
            
            await show_escrow_question(client, message, asset_type, year, price, direct_choice)
            
        elif data.startswith("sell_escrow_"):
            # Escrow choice - final step
            parts = data.replace("sell_escrow_", "").split("_")
            escrow_choice = parts[0]  # yes or no
            asset_type = parts[1] if len(parts) > 1 else "group"
            year = parts[2] if len(parts) > 2 else "2024"
            price = parts[3] if len(parts) > 3 else "10"
            direct_choice = parts[4] if len(parts) > 4 else "no"
            
            asset_data = {
                "type": asset_type,
                "year": year,
                "price": price,
                "direct": direct_choice,
                "escrow": escrow_choice
            }
            
            await show_sell_confirmation(client, message, asset_data)
            
        elif data == "sell_select_year":
            await show_sell_year_selection(client, message, "group")  # Should get from session
            
        elif data == "sell_select_price":
            await show_sell_price_selection(client, message, "group", "2024")  # Should get from session
            
        elif data == "sell_select_direct":
            await show_sell_direct_question(client, message, "group", "2024", "10")  # Should get from session
            
    except Exception as e:
        print(f"❌ Error in sell callback handler: {e}")
        await callback_query.answer("❌ Error occurred!", show_alert=True)

# ============================================
# MESSAGE HANDLERS FOR TEXT INPUT
# ============================================

@teleshop_bot.on_message(filters.text & filters.private & filters.regex(r"^[A-Za-z0-9\s]+ – [A-Za-z0-9\s]+ – \d+$"))
async def handle_other_asset_input(client: Client, message: Message):
    """
    Handle manual input for 'Other' asset type
    """
    try:
        # Parse the input format: Name – Category – Price
        parts = message.text.split(" – ")
        if len(parts) != 3:
            await message.reply_text(
                "❌ **Invalid format!**\n\n"
                "Please use the format:\n"
                "```Name – Category – Price```\n\n"
                "Example: ```Discord Bot – Software – 35```"
            )
            return
        
        name, category, price = parts
        price = price.strip()
        
        # Validate price
        try:
            price_val = int(price)
            if price_val < Settings.MIN_ASSET_PRICE or price_val > Settings.MAX_ASSET_PRICE:
                await message.reply_text(
                    f"❌ **Invalid price!**\n\n"
                    f"Price must be between ${Settings.MIN_ASSET_PRICE} - ${Settings.MAX_ASSET_PRICE}"
                )
                return
        except ValueError:
            await message.reply_text("❌ **Invalid price!** Please enter a valid number.")
            return
        
        # Show confirmation
        other_confirmation = f"""
✅ **Asset Details Received**

**Your Asset:**
• 📦 Name: {name.strip()}
• 🏷️ Category: {category.strip()}  
• 💰 Price: ${price}

**Next: Choose sale method**
"""
        
        method_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🤝 Direct Sale to Us", callback_data=f"sell_direct_yes_other_2024_{price}")],
            [InlineKeyboardButton("🏪 List on Marketplace", callback_data=f"sell_direct_no_other_2024_{price}")],
            [InlineKeyboardButton("🔙 Back", callback_data="main_sell")]
        ])
        
        await message.reply_text(
            other_confirmation,
            reply_markup=method_keyboard,
            disable_web_page_preview=True
        )
        
    except Exception as e:
        print(f"❌ Error handling other asset input: {e}")
        await message.reply_text("❌ Error processing your asset details. Please try again.")

# ============================================
# EXPORT FUNCTIONS
# ============================================

__all__ = [
    "show_sell_menu",
    "show_sell_year_selection",
    "show_sell_price_selection", 
    "show_sell_direct_question",
    "show_escrow_question",
    "show_sell_confirmation",
    "handle_other_asset_details"
]
