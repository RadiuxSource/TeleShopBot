from pyrogram import filters, Client, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from Modules import teleshop_bot
from database import get_user_settings, update_user_settings

# Settings menu keyboard
settings_menu_keyboard = ReplyKeyboardMarkup(
    [
        [KeyboardButton("🔍 Filter Settings"), KeyboardButton("📊 Sort Settings")],
        [KeyboardButton("🔄 Reset Settings"), KeyboardButton("⚙️ Other Settings")],
        [KeyboardButton("🔙 Back to Main Menu")],
    ],
    resize_keyboard=True
)

@teleshop_bot.on_message(filters.command(["settings"]) & filters.private)
async def settings_command(client: Client, message: Message):
    try:
        # Get user's current settings
        user_settings = await get_user_settings(message.from_user.id)
        
        settings_text = (
            "⚙️ **Your Current Settings**\n\n"
            f"🔍 **Filter Settings:**\n"
            f"• Min Rating: {user_settings.get('min_seller_rating', 'No filter')} stars\n"
            f"• Max Price: {user_settings.get('max_price', 'No limit')}\n"
            f"• Min Price: {user_settings.get('min_price', 'No limit')}\n"
            f"• Creation Year: {user_settings.get('creation_year_filter', 'All years')}\n"
            f"• Min Members: {user_settings.get('min_members', 'No limit')}\n\n"
            f"📊 **Sort Settings:**\n"
            f"• Sort by: {user_settings.get('sort_by', 'Default (newest first)')}\n"
            f"• Order: {user_settings.get('sort_order', 'Descending')}\n\n"
            f"🎯 **Other Settings:**\n"
            f"• Anonymous Mode: {user_settings.get('anonymous_mode', 'Enabled')}\n"
            f"• Notifications: {user_settings.get('notifications', 'Enabled')}\n\n"
            "Choose what you want to configure:"
        )
        
        await message.reply_text(settings_text, reply_markup=settings_menu_keyboard)
        
    except Exception as e:
        print(f"Error in settings_command: {e}")
        await message.reply_text(
            "❌ Error loading settings. Please try again.",
            reply_markup=settings_menu_keyboard
        )

# Handle settings menu navigation
@teleshop_bot.on_message(filters.text & filters.private, group=6)  # Medium-low priority
async def settings_menu_handler(client: Client, message: Message):
    text = message.text.strip().lower()
    
    if "filter settings" in text or "🔍" in text:
        await show_filter_settings(client, message)
        return
    elif "sort settings" in text or "📊" in text:
        await show_sort_settings(client, message)
        return
    elif "reset settings" in text or "🔄" in text:
        await reset_settings(client, message)
        return
    elif "other settings" in text or "⚙️" in text:
        await show_other_settings(client, message)
        return

async def show_filter_settings(client: Client, message: Message):
    """Show filter configuration options"""
    try:
        filter_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⭐ Min Seller Rating", callback_data="filter_rating"),
                InlineKeyboardButton("💰 Price Range", callback_data="filter_price")
            ],
            [
                InlineKeyboardButton("📅 Creation Year", callback_data="filter_year"),
                InlineKeyboardButton("👥 Min Members", callback_data="filter_members")
            ],
            [
                InlineKeyboardButton("🔄 Clear All Filters", callback_data="clear_filters"),
                InlineKeyboardButton("🔙 Back", callback_data="back_to_settings")
            ]
        ])
        
        await message.reply_text(
            "🔍 **Filter Settings**\n\n"
            "Configure filters to show only groups that match your criteria:\n\n"
            "• **Min Seller Rating:** Only show groups from highly rated sellers\n"
            "• **Price Range:** Set minimum and maximum price limits\n"
            "• **Creation Year:** Filter by when groups were created\n"
            "• **Min Members:** Only show groups with sufficient members\n\n"
            "Choose a filter to configure:",
            reply_markup=filter_keyboard
        )
        
    except Exception as e:
        print(f"Error in show_filter_settings: {e}")
        await message.reply_text("❌ Error loading filter settings.")

async def show_sort_settings(client: Client, message: Message):
    """Show sorting configuration options"""
    try:
        sort_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("💰 Price (Low to High)", callback_data="sort_price_asc"),
                InlineKeyboardButton("💰 Price (High to Low)", callback_data="sort_price_desc")
            ],
            [
                InlineKeyboardButton("⭐ Rating (Best First)", callback_data="sort_rating_desc"),
                InlineKeyboardButton("⭐ Rating (Worst First)", callback_data="sort_rating_asc")
            ],
            [
                InlineKeyboardButton("👥 Members (Most First)", callback_data="sort_members_desc"),
                InlineKeyboardButton("👥 Members (Least First)", callback_data="sort_members_asc")
            ],
            [
                InlineKeyboardButton("📅 Newest First", callback_data="sort_newest"),
                InlineKeyboardButton("📅 Oldest First", callback_data="sort_oldest")
            ],
            [
                InlineKeyboardButton("🔄 Default Sort", callback_data="sort_default"),
                InlineKeyboardButton("🔙 Back", callback_data="back_to_settings")
            ]
        ])
        
        await message.reply_text(
            "📊 **Sort Settings**\n\n"
            "Choose how you want groups to be sorted when browsing:\n\n"
            "• **Price:** Sort by asking price\n"
            "• **Rating:** Sort by seller rating\n"
            "• **Members:** Sort by group member count\n"
            "• **Date:** Sort by listing date\n\n"
            "Select your preferred sorting:",
            reply_markup=sort_keyboard
        )
        
    except Exception as e:
        print(f"Error in show_sort_settings: {e}")
        await message.reply_text("❌ Error loading sort settings.")

async def show_other_settings(client: Client, message: Message):
    """Show other configuration options"""
    try:
        other_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🎭 Anonymous Mode", callback_data="toggle_anonymous"),
                InlineKeyboardButton("🔔 Notifications", callback_data="toggle_notifications")
            ],
            [
                InlineKeyboardButton("🌐 Language (EN)", callback_data="change_language"),
                InlineKeyboardButton("🎨 Theme (Default)", callback_data="change_theme")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="back_to_settings")
            ]
        ])
        
        await message.reply_text(
            "⚙️ **Other Settings**\n\n"
            "Configure additional preferences:\n\n"
            "• **Anonymous Mode:** Hide your identity in transactions\n"
            "• **Notifications:** Receive updates about deals\n"
            "• **Language:** Change bot language (Coming soon)\n"
            "• **Theme:** Change interface theme (Coming soon)\n\n"
            "Choose what to configure:",
            reply_markup=other_keyboard
        )
        
    except Exception as e:
        print(f"Error in show_other_settings: {e}")
        await message.reply_text("❌ Error loading other settings.")

# Handle filter rating callback
@teleshop_bot.on_callback_query(filters.regex(r"^filter_rating$"))
async def filter_rating_callback(client: Client, callback_query):
    try:
        rating_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⭐ 1+ Stars", callback_data="set_min_rating_1"),
                InlineKeyboardButton("⭐⭐ 2+ Stars", callback_data="set_min_rating_2")
            ],
            [
                InlineKeyboardButton("⭐⭐⭐ 3+ Stars", callback_data="set_min_rating_3"),
                InlineKeyboardButton("⭐⭐⭐⭐ 4+ Stars", callback_data="set_min_rating_4")
            ],
            [
                InlineKeyboardButton("⭐⭐⭐⭐⭐ 5 Stars Only", callback_data="set_min_rating_5"),
                InlineKeyboardButton("🚫 No Filter", callback_data="set_min_rating_0")
            ],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_filters")]
        ])
        
        await callback_query.message.edit_text(
            "⭐ **Minimum Seller Rating Filter**\n\n"
            "Choose the minimum seller rating to show groups from:\n\n"
            "• **Higher ratings = more trustworthy sellers**\n"
            "• **New sellers may have no ratings yet**\n"
            "• **Use 4+ stars for maximum safety**\n\n"
            "Select minimum rating:",
            reply_markup=rating_keyboard
        )
        
    except Exception as e:
        print(f"Error in filter_rating_callback: {e}")
        await callback_query.answer("❌ Error occurred!")

# Handle price filter callback
@teleshop_bot.on_callback_query(filters.regex(r"^filter_price$"))
async def filter_price_callback(client: Client, callback_query):
    try:
        price_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("💰 $1-$10", callback_data="set_price_range_1_10"),
                InlineKeyboardButton("💰 $5-$15", callback_data="set_price_range_5_15")
            ],
            [
                InlineKeyboardButton("💰 $10-$25", callback_data="set_price_range_10_25"),
                InlineKeyboardButton("💰 $20-$50", callback_data="set_price_range_20_50")
            ],
            [
                InlineKeyboardButton("💰 Under $5", callback_data="set_price_range_0_5"),
                InlineKeyboardButton("💰 Over $50", callback_data="set_price_range_50_999")
            ],
            [
                InlineKeyboardButton("🎯 Custom Range", callback_data="set_custom_price_range"),
                InlineKeyboardButton("🚫 No Filter", callback_data="clear_price_filter")
            ],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_filters")]
        ])
        
        await callback_query.message.edit_text(
            "💰 **Price Range Filter**\n\n"
            "Set minimum and maximum price limits:\n\n"
            "• **Lower prices:** More affordable but may have fewer features\n"
            "• **Higher prices:** Premium groups with more members\n"
            "• **Custom range:** Set your own min/max values\n\n"
            "Choose a price range:",
            reply_markup=price_keyboard
        )
        
    except Exception as e:
        print(f"Error in filter_price_callback: {e}")
        await callback_query.answer("❌ Error occurred!")

# Handle year filter callback
@teleshop_bot.on_callback_query(filters.regex(r"^filter_year$"))
async def filter_year_callback(client: Client, callback_query):
    try:
        year_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📅 2024 Only", callback_data="set_year_filter_2024"),
                InlineKeyboardButton("📅 2023-2024", callback_data="set_year_filter_2023_2024")
            ],
            [
                InlineKeyboardButton("📅 2022-2024", callback_data="set_year_filter_2022_2024"),
                InlineKeyboardButton("📅 2020-2024", callback_data="set_year_filter_2020_2024")
            ],
            [
                InlineKeyboardButton("📅 Before 2020", callback_data="set_year_filter_old"),
                InlineKeyboardButton("🚫 All Years", callback_data="clear_year_filter")
            ],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_filters")]
        ])
        
        await callback_query.message.edit_text(
            "📅 **Creation Year Filter**\n\n"
            "Filter groups by when they were created:\n\n"
            "• **Newer groups:** More recent content, active communities\n"
            "• **Older groups:** Established communities, proven track record\n"
            "• **All years:** See everything available\n\n"
            "Choose year range:",
            reply_markup=year_keyboard
        )
        
    except Exception as e:
        print(f"Error in filter_year_callback: {e}")
        await callback_query.answer("❌ Error occurred!")

# Handle members filter callback
@teleshop_bot.on_callback_query(filters.regex(r"^filter_members$"))
async def filter_members_callback(client: Client, callback_query):
    try:
        members_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("👥 100+ Members", callback_data="set_min_members_100"),
                InlineKeyboardButton("👥 500+ Members", callback_data="set_min_members_500")
            ],
            [
                InlineKeyboardButton("👥 1K+ Members", callback_data="set_min_members_1000"),
                InlineKeyboardButton("👥 5K+ Members", callback_data="set_min_members_5000")
            ],
            [
                InlineKeyboardButton("👥 10K+ Members", callback_data="set_min_members_10000"),
                InlineKeyboardButton("👥 50K+ Members", callback_data="set_min_members_50000")
            ],
            [
                InlineKeyboardButton("🚫 No Filter", callback_data="clear_members_filter"),
                InlineKeyboardButton("🔙 Back", callback_data="back_to_filters")
            ]
        ])
        
        await callback_query.message.edit_text(
            "👥 **Minimum Members Filter**\n\n"
            "Set minimum member count for groups:\n\n"
            "• **More members:** Larger audience, more engagement\n"
            "• **Fewer members:** More intimate community\n"
            "• **Quality over quantity:** Consider engagement vs count\n\n"
            "Choose minimum members:",
            reply_markup=members_keyboard
        )
        
    except Exception as e:
        print(f"Error in filter_members_callback: {e}")
        await callback_query.answer("❌ Error occurred!")

# Handle setting minimum rating
@teleshop_bot.on_callback_query(filters.regex(r"^set_min_rating_(\d+)"))
async def set_min_rating_callback(client: Client, callback_query):
    try:
        rating = int(callback_query.data.split('_')[3])
        user_id = callback_query.from_user.id
        
        if rating == 0:
            await update_user_settings(user_id, {"min_seller_rating": None})
            await callback_query.answer("✅ Seller rating filter removed!")
            filter_text = "All sellers"
        else:
            await update_user_settings(user_id, {"min_seller_rating": rating})
            await callback_query.answer(f"✅ Minimum {rating}+ star sellers only!")
            filter_text = f"{rating}+ stars only"
        
        # Update the message
        await callback_query.message.edit_text(
            f"⭐ **Seller Rating Filter Updated!**\n\n"
            f"**Current setting:** {filter_text}\n\n"
            f"You will now only see groups from sellers with {rating}+ star ratings.\n\n"
            f"💡 This filter will apply when you browse groups with /buy command."
        )
        
    except Exception as e:
        print(f"Error in set_min_rating_callback: {e}")
        await callback_query.answer("❌ Error updating rating filter!")

# Handle setting price range
@teleshop_bot.on_callback_query(filters.regex(r"^set_price_range_(\d+)_(\d+)"))
async def set_price_range_callback(client: Client, callback_query):
    try:
        parts = callback_query.data.split('_')
        min_price = int(parts[3])
        max_price = int(parts[4])
        user_id = callback_query.from_user.id
        
        await update_user_settings(user_id, {
            "min_price": min_price,
            "max_price": max_price
        })
        
        await callback_query.answer(f"✅ Price range set to ${min_price}-${max_price}!")
        
        await callback_query.message.edit_text(
            f"💰 **Price Filter Updated!**\n\n"
            f"**Price range:** ${min_price} - ${max_price}\n\n"
            f"You will now only see groups priced between ${min_price} and ${max_price}.\n\n"
            f"💡 This filter will apply when you browse groups with /buy command."
        )
        
    except Exception as e:
        print(f"Error in set_price_range_callback: {e}")
        await callback_query.answer("❌ Error updating price filter!")

# Handle sorting callbacks
@teleshop_bot.on_callback_query(filters.regex(r"^sort_(price|rating|members|newest|oldest|default)(_asc|_desc)?"))
async def sort_settings_callback(client: Client, callback_query):
    try:
        user_id = callback_query.from_user.id
        data = callback_query.data
        
        if data == "sort_price_asc":
            sort_by, sort_order = "price", "ascending"
            display = "Price (Low to High)"
        elif data == "sort_price_desc":
            sort_by, sort_order = "price", "descending"
            display = "Price (High to Low)"
        elif data == "sort_rating_desc":
            sort_by, sort_order = "rating", "descending"
            display = "Rating (Best First)"
        elif data == "sort_rating_asc":
            sort_by, sort_order = "rating", "ascending"
            display = "Rating (Worst First)"
        elif data == "sort_members_desc":
            sort_by, sort_order = "members", "descending"
            display = "Members (Most First)"
        elif data == "sort_members_asc":
            sort_by, sort_order = "members", "ascending"
            display = "Members (Least First)"
        elif data == "sort_newest":
            sort_by, sort_order = "date", "descending"
            display = "Newest First"
        elif data == "sort_oldest":
            sort_by, sort_order = "date", "ascending"
            display = "Oldest First"
        elif data == "sort_default":
            sort_by, sort_order = "default", "descending"
            display = "Default (Newest First)"
        
        await update_user_settings(user_id, {
            "sort_by": sort_by,
            "sort_order": sort_order
        })
        
        await callback_query.answer(f"✅ Sorting set to: {display}")
        
        await callback_query.message.edit_text(
            f"📊 **Sort Settings Updated!**\n\n"
            f"**Current sorting:** {display}\n\n"
            f"Groups will now be sorted by {display.lower()} when you browse.\n\n"
            f"💡 This sorting will apply when you browse groups with /buy command."
        )
        
    except Exception as e:
        print(f"Error in sort_settings_callback: {e}")
        await callback_query.answer("❌ Error updating sort settings!")

async def reset_settings(client: Client, message: Message):
    """Reset all user settings to default"""
    try:
        reset_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Yes, Reset All", callback_data="confirm_reset_settings"),
                InlineKeyboardButton("❌ No, Keep Settings", callback_data="cancel_reset_settings")
            ]
        ])
        
        await message.reply_text(
            "🔄 **Reset All Settings**\n\n"
            "This will reset all your settings to default values:\n\n"
            "• Remove all filters\n"
            "• Reset sorting to default\n"
            "• Enable anonymous mode\n"
            "• Enable notifications\n\n"
            "⚠️ **This cannot be undone!**\n\n"
            "Are you sure you want to reset all settings?",
            reply_markup=reset_keyboard
        )
        
    except Exception as e:
        print(f"Error in reset_settings: {e}")
        await message.reply_text("❌ Error preparing settings reset.")

# Handle settings reset confirmation
@teleshop_bot.on_callback_query(filters.regex(r"^confirm_reset_settings$"))
async def confirm_reset_settings_callback(client: Client, callback_query):
    try:
        user_id = callback_query.from_user.id
        
        # Reset to default settings
        default_settings = {
            "min_seller_rating": None,
            "max_price": None,
            "min_price": None,
            "creation_year_filter": None,
            "min_members": None,
            "sort_by": "default",
            "sort_order": "descending",
            "anonymous_mode": True,
            "notifications": True
        }
        
        await update_user_settings(user_id, default_settings)
        
        await callback_query.answer("✅ All settings reset to default!")
        
        await callback_query.message.edit_text(
            "🔄 **Settings Reset Complete!**\n\n"
            "All your settings have been reset to default values:\n\n"
            "✅ All filters removed\n"
            "✅ Default sorting restored\n"
            "✅ Anonymous mode enabled\n"
            "✅ Notifications enabled\n\n"
            "You can now configure new settings as needed."
        )
        
    except Exception as e:
        print(f"Error in confirm_reset_settings_callback: {e}")
        await callback_query.answer("❌ Error resetting settings!")

# Handle back navigation
@teleshop_bot.on_callback_query(filters.regex(r"^back_to_(settings|filters)$"))
async def back_navigation_callback(client: Client, callback_query):
    try:
        if callback_query.data == "back_to_settings":
            await settings_command(client, callback_query.message)
        elif callback_query.data == "back_to_filters":
            await show_filter_settings(client, callback_query.message)
            
    except Exception as e:
        print(f"Error in back_navigation_callback: {e}")
        await callback_query.answer("❌ Error occurred!")

# Handle other callback data that wasn't implemented yet
@teleshop_bot.on_callback_query(filters.regex(r"^(clear_filters|toggle_anonymous|toggle_notifications|change_language|change_theme|cancel_reset_settings)$"))
async def misc_settings_callback(client: Client, callback_query):
    try:
        data = callback_query.data
        
        if data == "clear_filters":
            await update_user_settings(callback_query.from_user.id, {
                "min_seller_rating": None,
                "max_price": None,
                "min_price": None,
                "creation_year_filter": None,
                "min_members": None
            })
            await callback_query.answer("✅ All filters cleared!")
            await callback_query.message.edit_text("🔄 **All filters cleared!** You will now see all available groups.")
            
        elif data == "cancel_reset_settings":
            await callback_query.answer("Settings reset cancelled")
            await callback_query.message.edit_text("❌ Settings reset cancelled. Your current settings are preserved.")
            
        else:
            await callback_query.answer("🚧 Feature coming soon!")
            
    except Exception as e:
        print(f"Error in misc_settings_callback: {e}")
        await callback_query.answer("❌ Error occurred!")