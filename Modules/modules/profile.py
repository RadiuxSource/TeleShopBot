from pyrogram import filters, Client, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from Modules import teleshop_bot, LOG_GROUP
from database import fetch_group_listings, get_user_statistics, fetch_user_groups, update_user_activity, get_user_premium_status

@teleshop_bot.on_message(filters.command(["profile"]) & filters.private)
async def profile_command(client: Client, message: Message):
    user_id = message.from_user.id
    user = message.from_user
    
    # Update user activity
    try:
        await update_user_activity(user_id, "profile_view")
    except Exception as e:
        print(f"Error updating user activity: {e}")
    
    try:
        # Get user statistics and premium status
        stats = await get_user_statistics(user_id)
        user_groups = await fetch_user_groups(user_id)
        premium_status = await get_user_premium_status(user_id)
        
        # Get user rating
        from database import get_user_rating
        rating_info = await get_user_rating(user_id)
        
        # Ensure user_groups is a list
        if user_groups is None:
            user_groups = []
        
        # Premium status indicator
        premium_indicator = "✅ Premium" if premium_status.get('is_premium', False) else "❌ Free"
        premium_expiry = premium_status.get('expires_at', 'N/A')
        
        # Format star rating display
        if rating_info['total_ratings'] > 0:
            rating_stars = "⭐" * int(rating_info['average_rating'])
            rating_display = f"{rating_stars} ({rating_info['average_rating']:.1f}/5.0) - {rating_info['total_ratings']} reviews"
        else:
            rating_display = "No ratings yet"
        
        # Format user information
        profile_text = (
            f"👤 **Your Profile**\n\n"
            f"**Name:** {user.first_name} {user.last_name or ''}\n"
            f"**Username:** @{user.username if user.username else 'Not set'}\n"
            f"**User ID:** `{user_id}`\n"
            f"**Subscription:** {premium_indicator}\n"
        )
        
        if premium_status.get('is_premium', False):
            profile_text += f"**Premium Expires:** {premium_expiry}\n"
        
        profile_text += (
            f"**Member since:** {stats.get('member_since', 'Unknown')}\n"
            f"**Rating:** {rating_display}\n\n"
            f"📊 **Statistics:**\n"
            f"• Groups Currently Listed: {stats.get('groups_listed', 0)}\n"
            f"• Groups Successfully Sold: {stats.get('groups_sold', 0)}\n"
            f"• Groups Successfully Bought: {stats.get('groups_bought', 0)}\n"
            f"• Total Deals Completed: {stats.get('total_deals', 0)}\n\n"
        )
        
        if user_groups:
            profile_text += f"🏪 **Your Active Listings:**\n"
            for i, group in enumerate(user_groups[:3], 1):  # Show first 3 groups
                profile_text += f"{i}. {group.get('name', 'N/A')} - {group.get('price', 'N/A')}\n"
            
            if len(user_groups) > 3:
                profile_text += f"... and {len(user_groups) - 3} more\n"
        else:
            profile_text += "🏪 **No active listings**\n"
        
        # Create profile keyboard
        profile_keyboard = []
        
        if user_groups:
            profile_keyboard.append([
                InlineKeyboardButton("📋 View All My Listings", callback_data=f"view_my_listings_{user_id}")
            ])
        
        # Premium subscription button
        if not premium_status.get('is_premium', False):
            profile_keyboard.append([
                InlineKeyboardButton("⭐ Get Premium - ₹99/month", callback_data=f"get_premium_{user_id}")
            ])
        else:
            profile_keyboard.append([
                InlineKeyboardButton("⭐ Manage Premium", callback_data=f"manage_premium_{user_id}")
            ])
        
        profile_keyboard.extend([
            [
                InlineKeyboardButton("📈 Detailed Stats", callback_data=f"detailed_stats_{user_id}"),
                InlineKeyboardButton("🔄 Refresh Profile", callback_data=f"refresh_profile_{user_id}")
            ],
            [
                InlineKeyboardButton("⚙️ Profile Settings", callback_data=f"profile_settings_{user_id}")
            ]
        ])
        
        await message.reply_text(
            profile_text,
            reply_markup=InlineKeyboardMarkup(profile_keyboard)
        )
        
    except Exception as e:
        print(f"Error in profile_command: {e}")
        await message.reply_text(
            "❌ **Error loading profile**\n\n"
            "There was an error loading your profile data. Please try again later or contact support if the issue persists."
        )

# Handle profile callbacks
@teleshop_bot.on_callback_query(filters.regex(r"^(view_my_listings|detailed_stats|refresh_profile|profile_settings|get_premium|manage_premium)_(\d+)$"))
async def profile_callback_handler(client: Client, callback_query):
    try:
        # Parse callback data properly
        parts = callback_query.data.split('_')
        if len(parts) < 3:
            await callback_query.answer("❌ Invalid callback data!", show_alert=True)
            return
            
        # Handle different action patterns
        if callback_query.data.startswith("view_my_listings_"):
            action = "view_my_listings"
            user_id = int(parts[-1])
        elif callback_query.data.startswith("detailed_stats_"):
            action = "detailed_stats"
            user_id = int(parts[-1])
        elif callback_query.data.startswith("refresh_profile_"):
            action = "refresh_profile"
            user_id = int(parts[-1])
        elif callback_query.data.startswith("profile_settings_"):
            action = "profile_settings"
            user_id = int(parts[-1])
        elif callback_query.data.startswith("get_premium_"):
            action = "get_premium"
            user_id = int(parts[-1])
        elif callback_query.data.startswith("manage_premium_"):
            action = "manage_premium"
            user_id = int(parts[-1])
        else:
            await callback_query.answer("❌ Unknown action!", show_alert=True)
            return
        
        # Verify user authorization
        if callback_query.from_user.id != user_id:
            await callback_query.answer("❌ You can only view your own profile!", show_alert=True)
            return
        
        if action == "view_my_listings":
            await view_user_listings(client, callback_query, user_id)
        elif action == "detailed_stats":
            await show_detailed_stats(client, callback_query, user_id)
        elif action == "refresh_profile":
            await refresh_user_profile(client, callback_query, user_id)
        elif action == "profile_settings":
            await show_profile_settings(client, callback_query, user_id)
        elif action == "get_premium":
            await show_premium_subscription(client, callback_query, user_id)
        elif action == "manage_premium":
            await manage_premium_subscription(client, callback_query, user_id)
            
    except Exception as e:
        print(f"Error in profile_callback_handler: {e}")
        await callback_query.answer("❌ An error occurred!", show_alert=True)

async def view_user_listings(client: Client, callback_query, user_id):
    try:
        user_groups = await fetch_user_groups(user_id)
        
        # Ensure user_groups is a list
        if user_groups is None:
            user_groups = []
        
        if not user_groups or len(user_groups) == 0:
            await callback_query.answer("You have no active listings!", show_alert=True)
            return
        
        from datetime import datetime
        refresh_time = datetime.now().strftime("%H:%M:%S")
        
        listings_text = f"📋 **Your Active Listings ({len(user_groups)}):**\n\n"
        
        for i, group in enumerate(user_groups, 1):
            listings_text += (
                f"**{i}. {group.get('name', 'N/A')}**\n"
                f"• Group ID: `{group.get('group_id', 'N/A')}`\n"
                f"• Price: {group.get('price', 'N/A')}\n"
                f"• Members: {group.get('members', 'N/A')}\n"
                f"• Listed: {group.get('created_at', 'N/A')}\n\n"
            )
        
        listings_text += f"🔄 *Refreshed: {refresh_time}*"
        
        back_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Profile", callback_data=f"refresh_profile_{user_id}")]
        ])
        
        try:
            await callback_query.message.edit_text(
                listings_text,
                reply_markup=back_keyboard
            )
            await callback_query.answer()
        except Exception as edit_error:
            print(f"Edit failed in view_user_listings: {edit_error}")
            await callback_query.message.reply_text(
                listings_text,
                reply_markup=back_keyboard
            )
            await callback_query.answer()
        
    except Exception as e:
        print(f"Error in view_user_listings: {e}")
        await callback_query.answer("❌ Error loading listings!", show_alert=True)

async def show_detailed_stats(client: Client, callback_query, user_id):
    try:
        stats = await get_user_statistics(user_id)
        
        # Get user rating and transaction history
        from database import get_user_rating, get_user_sales_history, get_user_purchase_history
        rating_info = await get_user_rating(user_id)
        sales_history = await get_user_sales_history(user_id)
        purchase_history = await get_user_purchase_history(user_id)
        
        from datetime import datetime
        refresh_time = datetime.now().strftime("%H:%M:%S")
        
        detailed_text = (
            f"📈 **Detailed Statistics**\n\n"
            f"**Selling Activity:**\n"
            f"• Groups Listed: {stats.get('groups_listed', 0)}\n"
            f"• Groups Sold: {stats.get('groups_sold', 0)}\n"
            f"• Total Earnings: {stats.get('total_earnings', '$0')}\n"
            f"• Success Rate: {stats.get('sell_success_rate', '0%')}\n\n"
            f"**Buying Activity:**\n"
            f"• Groups Bought: {stats.get('groups_bought', 0)}\n"
            f"• Total Spent: {stats.get('total_spent', '$0')}\n"
            f"• Deals Initiated: {stats.get('deals_initiated', 0)}\n"
            f"• Deal Success Rate: {stats.get('buy_success_rate', '0%')}\n\n"
            f"**Rating & Reputation:**\n"
            f"• Average Rating: {rating_info['average_rating']:.1f}/5 ⭐\n"
            f"• Total Ratings Received: {rating_info['total_ratings']}\n"
            f"• Reputation: {rating_info['rating_display']}\n\n"
            f"**Transaction History:**\n"
            f"• Sales Completed: {len(sales_history)}\n"
            f"• Purchases Made: {len(purchase_history)}\n"
            f"• Total Transactions: {stats.get('total_deals', 0)}\n\n"
            f"**Overall Performance:**\n"
            f"• Member Since: {stats.get('member_since', 'Unknown')}\n"
            f"• Last Activity: {stats.get('last_activity', 'Unknown')}\n\n"
            f"🔄 *Refreshed: {refresh_time}*"
        )
        
        back_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📋 Sales History", callback_data=f"sales_history_{user_id}"),
                InlineKeyboardButton("🛒 Purchase History", callback_data=f"purchase_history_{user_id}")
            ],
            [InlineKeyboardButton("🔙 Back to Profile", callback_data=f"refresh_profile_{user_id}")]
        ])
        
        try:
            await callback_query.message.edit_text(
                detailed_text,
                reply_markup=back_keyboard
            )
            await callback_query.answer()
        except Exception as edit_error:
            print(f"Edit failed in show_detailed_stats: {edit_error}")
            await callback_query.message.reply_text(
                detailed_text,
                reply_markup=back_keyboard
            )
            await callback_query.answer()
        
    except Exception as e:
        print(f"Error in show_detailed_stats: {e}")
        await callback_query.answer("❌ Error loading statistics!", show_alert=True)

async def refresh_user_profile(client: Client, callback_query, user_id):
    try:
        user = callback_query.from_user
        
        # Get updated statistics and premium status
        stats = await get_user_statistics(user_id)
        user_groups = await fetch_user_groups(user_id)
        premium_status = await get_user_premium_status(user_id)
        
        # Get user rating
        from database import get_user_rating
        rating_info = await get_user_rating(user_id)
        
        # Ensure user_groups is a list
        if user_groups is None:
            user_groups = []
        
        # Premium status indicator
        premium_indicator = "✅ Premium" if premium_status.get('is_premium', False) else "❌ Free"
        premium_expiry = premium_status.get('expires_at', 'N/A')
        
        # Format star rating display
        if rating_info['total_ratings'] > 0:
            rating_stars = "⭐" * int(rating_info['average_rating'])
            rating_display = f"{rating_stars} ({rating_info['average_rating']:.1f}/5.0) - {rating_info['total_ratings']} reviews"
        else:
            rating_display = "No ratings yet"
        
        # Format updated user information (same as main profile command)
        profile_text = (
            f"👤 **Your Profile**\n\n"
            f"**Name:** {user.first_name} {user.last_name or ''}\n"
            f"**Username:** @{user.username if user.username else 'Not set'}\n"
            f"**User ID:** `{user_id}`\n"
            f"**Subscription:** {premium_indicator}\n"
        )
        
        if premium_status.get('is_premium', False):
            profile_text += f"**Premium Expires:** {premium_expiry}\n"
        
        profile_text += (
            f"**Member since:** {stats.get('member_since', 'Unknown')}\n"
            f"**Rating:** {rating_display}\n\n"
            f"📊 **Statistics:**\n"
            f"• Groups Currently Listed: {stats.get('groups_listed', 0)}\n"
            f"• Groups Successfully Sold: {stats.get('groups_sold', 0)}\n"
            f"• Groups Successfully Bought: {stats.get('groups_bought', 0)}\n"
            f"• Total Deals Completed: {stats.get('total_deals', 0)}\n\n"
        )
        
        if user_groups:
            profile_text += f"🏪 **Your Active Listings:**\n"
            for i, group in enumerate(user_groups[:3], 1):
                profile_text += f"{i}. {group.get('name', 'N/A')} - {group.get('price', 'N/A')}\n"
            
            if len(user_groups) > 3:
                profile_text += f"... and {len(user_groups) - 3} more\n"
        else:
            profile_text += "🏪 **No active listings**\n"
        
        # Add refresh timestamp to ensure content is different
        from datetime import datetime
        refresh_time = datetime.now().strftime("%H:%M:%S")
        profile_text += f"\n🔄 *Last refreshed: {refresh_time}*"
        
        # Create profile keyboard
        profile_keyboard = []
        
        if user_groups:
            profile_keyboard.append([
                InlineKeyboardButton("📋 View All My Listings", callback_data=f"view_my_listings_{user_id}")
            ])
        
        # Premium subscription button
        if not premium_status.get('is_premium', False):
            profile_keyboard.append([
                InlineKeyboardButton("⭐ Get Premium - ₹99/month", callback_data=f"get_premium_{user_id}")
            ])
        else:
            profile_keyboard.append([
                InlineKeyboardButton("⭐ Manage Premium", callback_data=f"manage_premium_{user_id}")
            ])
        
        profile_keyboard.extend([
            [
                InlineKeyboardButton("📈 Detailed Stats", callback_data=f"detailed_stats_{user_id}"),
                InlineKeyboardButton("🔄 Refresh Profile", callback_data=f"refresh_profile_{user_id}")
            ],
            [
                InlineKeyboardButton("⚙️ Profile Settings", callback_data=f"profile_settings_{user_id}")
            ]
        ])
        
        # Check if content is different from current message
        current_text = callback_query.message.text or ""
        
        try:
            if current_text != profile_text:
                await callback_query.message.edit_text(
                    profile_text,
                    reply_markup=InlineKeyboardMarkup(profile_keyboard)
                )
                await callback_query.answer("Profile refreshed!")
            else:
                # Content is the same, just answer the callback without editing
                await callback_query.answer("Profile is already up to date!")
        except Exception as edit_error:
            # If editing fails, send a new message instead
            print(f"Edit failed: {edit_error}, sending new message")
            await callback_query.message.reply_text(
                profile_text,
                reply_markup=InlineKeyboardMarkup(profile_keyboard)
            )
            await callback_query.answer("Profile refreshed!")
        
    except Exception as e:
        print(f"Error in refresh_user_profile: {e}")
        await callback_query.answer("❌ Error refreshing profile!", show_alert=True)

async def show_profile_settings(client: Client, callback_query, user_id):
    settings_text = (
        f"⚙️ **Profile Settings**\n\n"
        f"Customize your profile and notification preferences:\n\n"
        f"• Notification Settings\n"
        f"• Privacy Settings\n"
        f"• Account Management\n\n"
        f"🚧 **Settings panel coming soon!**"
    )
    
    settings_keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔔 Notifications", callback_data=f"notification_settings_{user_id}"),
            InlineKeyboardButton("🔐 Privacy", callback_data=f"privacy_settings_{user_id}")
        ],
        [
            InlineKeyboardButton("🔙 Back to Profile", callback_data=f"refresh_profile_{user_id}")
        ]
    ])
    
    await callback_query.message.edit_text(
        settings_text,
        reply_markup=settings_keyboard
    )
    await callback_query.answer()

# Handle notification and privacy settings (placeholder for future implementation)
@teleshop_bot.on_callback_query(filters.regex(r"^(notification_settings|privacy_settings)_(\d+)$"))
async def settings_callback_handler(client: Client, callback_query):
    try:
        parts = callback_query.data.split('_')
        if len(parts) < 3:
            await callback_query.answer("❌ Invalid callback data!", show_alert=True)
            return
            
        action = parts[0]
        user_id = int(parts[-1])
        
        if callback_query.from_user.id != user_id:
            await callback_query.answer("❌ Unauthorized!", show_alert=True)
            return
        
        await callback_query.answer("🚧 This feature is coming soon!", show_alert=True)
        
    except Exception as e:
        print(f"Error in settings_callback_handler: {e}")
        await callback_query.answer("❌ An error occurred!", show_alert=True)

async def show_premium_subscription(client: Client, callback_query, user_id):
    """Show premium subscription options and benefits"""
    premium_text = (
        f"⭐ **Premium Subscription**\n\n"
        f"**Benefits of Premium:**\n"
        f"• 🚀 Priority listing (your groups appear first)\n"
        f"• 📈 Advanced analytics and insights\n"
        f"• 🎯 Unlimited group listings\n"
        f"• 💬 Direct contact with interested buyers\n"
        f"• 🔔 Instant notifications for deals\n"
        f"• 📊 Detailed market statistics\n"
        f"• 🎨 Custom profile badge\n"
        f"• 🆘 Priority customer support\n\n"
        f"**Price:** ₹99/month\n"
        f"**Payment Method:** Telegram Stars\n\n"
        f"Ready to upgrade your experience?"
    )
    
    premium_keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💳 Pay ₹99 - Get Premium", callback_data=f"pay_premium_{user_id}")
        ],
        [
            InlineKeyboardButton("📋 View Benefits", callback_data=f"premium_benefits_{user_id}"),
            InlineKeyboardButton("❓ FAQ", callback_data=f"premium_faq_{user_id}")
        ],
        [
            InlineKeyboardButton("🔙 Back to Profile", callback_data=f"refresh_profile_{user_id}")
        ]
    ])
    
    await callback_query.message.edit_text(
        premium_text,
        reply_markup=premium_keyboard
    )
    await callback_query.answer()

async def manage_premium_subscription(client: Client, callback_query, user_id):
    """Manage existing premium subscription"""
    premium_status = await get_user_premium_status(user_id)
    
    manage_text = (
        f"⭐ **Premium Subscription Management**\n\n"
        f"**Status:** Active ✅\n"
        f"**Expires:** {premium_status.get('expires_at', 'N/A')}\n"
        f"**Auto-renewal:** {premium_status.get('auto_renew', 'Disabled')}\n\n"
        f"**Your Premium Benefits:**\n"
        f"• Priority listing active\n"
        f"• Advanced analytics enabled\n"
        f"• Unlimited listings\n"
        f"• Premium support access\n"
    )
    
    manage_keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 Renew Premium", callback_data=f"renew_premium_{user_id}")
        ],
        [
            InlineKeyboardButton("📊 Usage Stats", callback_data=f"premium_stats_{user_id}"),
            InlineKeyboardButton("🎫 Benefits", callback_data=f"premium_benefits_{user_id}")
        ],
        [
            InlineKeyboardButton("🔙 Back to Profile", callback_data=f"refresh_profile_{user_id}")
        ]
    ])
    
    await callback_query.message.edit_text(
        manage_text,
        reply_markup=manage_keyboard
    )
    await callback_query.answer()

# Handle premium-related callbacks
@teleshop_bot.on_callback_query(filters.regex(r"^(pay_premium|renew_premium|premium_benefits|premium_faq|premium_stats)_(\d+)$"))
async def premium_callback_handler(client: Client, callback_query):
    try:
        parts = callback_query.data.split('_')
        action = '_'.join(parts[:-1])  # Everything except the last part (user_id)
        user_id = int(parts[-1])
        
        if callback_query.from_user.id != user_id:
            await callback_query.answer("❌ Unauthorized!", show_alert=True)
            return
        
        if action == "pay_premium" or action == "renew_premium":
            await process_premium_payment(client, callback_query, user_id)
        elif action == "premium_benefits":
            await show_premium_benefits(client, callback_query, user_id)
        elif action == "premium_faq":
            await show_premium_faq(client, callback_query, user_id)
        elif action == "premium_stats":
            await show_premium_stats(client, callback_query, user_id)
            
    except Exception as e:
        print(f"Error in premium_callback_handler: {e}")
        await callback_query.answer("❌ An error occurred!", show_alert=True)

async def process_premium_payment(client: Client, callback_query, user_id):
    """Process premium subscription payment using Telegram Stars"""
    try:
        from pyrogram.types import LabeledPrice
        
        # Create invoice for premium subscription using Telegram Stars with minimal parameters
        await client.send_invoice(
            chat_id=callback_query.message.chat.id,
            title="TeleShop Premium Subscription",
            description="Get premium features for 30 days including priority listings, advanced analytics, and more!",
            payload=f"premium_sub_{user_id}_{int(callback_query.message.date.timestamp())}",
            currency="XTR",  # Telegram Stars currency
            prices=[LabeledPrice(label="Premium Subscription", amount=49)]  # 49 stars
        )
        
        await callback_query.answer("Payment invoice sent! Complete the payment to activate premium.")
        
    except Exception as e:
        print(f"Error processing premium payment: {e}")
        await callback_query.answer("❌ Payment processing error. Please try again.", show_alert=True)

async def show_premium_benefits(client: Client, callback_query, user_id):
    """Show detailed premium benefits"""
    benefits_text = (
        f"⭐ **Premium Benefits Details**\n\n"
        f"**🚀 Priority Listings:**\n"
        f"• Your groups appear at the top of search results\n"
        f"• Higher visibility to potential buyers\n\n"
        f"**📈 Advanced Analytics:**\n"
        f"• Detailed view statistics\n"
        f"• Market trend analysis\n"
        f"• Best pricing recommendations\n\n"
        f"**🎯 Unlimited Features:**\n"
        f"• No limit on group listings\n"
        f"• Unlimited deal requests\n\n"
        f"**💬 Enhanced Communication:**\n"
        f"• Direct buyer contact information\n"
        f"• Priority in deal notifications\n\n"
        f"**🛠️ Exclusive Tools:**\n"
        f"• Bulk listing management\n"
        f"• Custom pricing strategies\n"
        f"• Market insights dashboard\n"
    )
    
    back_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data=f"get_premium_{user_id}")]
    ])
    
    await callback_query.message.edit_text(benefits_text, reply_markup=back_keyboard)
    await callback_query.answer()

async def show_premium_faq(client: Client, callback_query, user_id):
    """Show premium FAQ"""
    faq_text = (
        f"❓ **Premium FAQ**\n\n"
        f"**Q: How long does premium last?**\n"
        f"A: Premium subscription lasts for 30 days from activation.\n\n"
        f"**Q: Can I cancel anytime?**\n"
        f"A: Yes, but no refunds for unused time.\n\n"
        f"**Q: What payment methods are accepted?**\n"
        f"A: Currently only Telegram Stars (₹99 = 99 Stars).\n\n"
        f"**Q: Do I get premium features immediately?**\n"
        f"A: Yes, features activate instantly after payment.\n\n"
        f"**Q: What happens when premium expires?**\n"
        f"A: Account returns to free tier, but data is preserved.\n\n"
        f"**Q: Can I upgrade multiple accounts?**\n"
        f"A: Each account needs separate premium subscription.\n"
    )
    
    back_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data=f"get_premium_{user_id}")]
    ])
    
    await callback_query.message.edit_text(faq_text, reply_markup=back_keyboard)
    await callback_query.answer()

async def show_premium_stats(client: Client, callback_query, user_id):
    """Show premium usage statistics"""
    stats = await get_premium_usage_stats(user_id)
    
    stats_text = (
        f"📊 **Premium Usage Statistics**\n\n"
        f"**This Month:**\n"
        f"• Priority views received: {stats.get('priority_views', 0)}\n"
        f"• Extra deals from premium: {stats.get('extra_deals', 0)}\n"
        f"• Analytics reports generated: {stats.get('reports_generated', 0)}\n"
        f"• Premium features used: {stats.get('features_used', 0)}\n\n"
        f"**Premium Value:**\n"
        f"• Estimated extra revenue: {stats.get('extra_revenue', '₹0')}\n"
        f"• Time saved: {stats.get('time_saved', '0 hours')}\n"
        f"• ROI: {stats.get('roi', '0%')}\n"
    )
    
    back_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data=f"manage_premium_{user_id}")]
    ])
    
    await callback_query.message.edit_text(stats_text, reply_markup=back_keyboard)
    await callback_query.answer()

# Handle successful premium payment
@teleshop_bot.on_message(filters.successful_payment)
async def handle_premium_payment(client: Client, message: Message):
    """Handle successful premium subscription payment"""
    user_id = message.from_user.id
    payment = message.successful_payment
    
    if payment.invoice_payload.startswith("premium_sub_"):
        try:
            # Import required functions
            from database import activate_premium_subscription, get_premium_expiry_date
            
            # Activate premium subscription
            await activate_premium_subscription(user_id)
            
            # Send confirmation
            await message.reply_text(
                f"🎉 **Premium Activated!**\n\n"
                f"Thank you for your payment of {payment.total_amount} stars!\n\n"
                f"✅ Premium features are now active\n"
                f"📅 Valid until: {get_premium_expiry_date()}\n"
                f"⭐ Enjoy priority listings and exclusive features!\n\n"
                f"Use /profile to see your premium status."
            )
            
            # Log to admin group
            if LOG_GROUP:
                await client.send_message(
                    LOG_GROUP,
                    f"💰 **Premium Subscription Activated**\n\n"
                    f"**User:** {message.from_user.mention}\n"
                    f"**User ID:** `{user_id}`\n"
                    f"**Amount:** {payment.total_amount} stars\n"
                    f"**Transaction ID:** `{payment.telegram_payment_charge_id}`"
                )
                
        except Exception as e:
            print(f"Error activating premium: {e}")
            await message.reply_text(
                "❌ Error activating premium. Please contact support with your payment details."
            )

async def get_premium_usage_stats(user_id):
    """Get premium usage statistics for a user"""
    try:
        # Import from database
        from database import get_premium_usage_stats as db_get_premium_usage_stats
        return await db_get_premium_usage_stats(user_id)
    except:
        # Fallback stats if function doesn't exist
        return {
            'priority_views': 0,
            'extra_deals': 0,
            'reports_generated': 0,
            'features_used': 0,
            'extra_revenue': '₹0',
            'time_saved': '0 hours',
            'roi': '0%'
        }

# Handle sales and purchase history callbacks
@teleshop_bot.on_callback_query(filters.regex(r"^(sales_history|purchase_history)_(\d+)$"))
async def history_callback_handler(client: Client, callback_query):
    try:
        action, user_id = callback_query.data.split('_')[0], int(callback_query.data.split('_')[-1])
        
        if callback_query.from_user.id != user_id:
            await callback_query.answer("❌ Unauthorized!", show_alert=True)
            return
        
        if action == "sales":
            from database import get_user_sales_history
            sales = await get_user_sales_history(user_id)
            
            if not sales:
                await callback_query.answer("No sales history found!", show_alert=True)
                return
            
            import string
            import random
            
            def generate_consistent_buyer_id(buyer_id, sold_at):
                """Generate consistent anonymous buyer ID"""
                random.seed(f"buyer_{buyer_id}_{sold_at}")
                chars = string.ascii_uppercase + string.digits
                return ''.join(random.choices(chars, k=10))
            
            history_text = f"📋 **Sales History ({len(sales)} sold):**\n\n"
            for i, sale in enumerate(sales[-10:], 1):  # Show last 10 sales
                buyer_id = sale.get('buyer_id', 0)
                sold_at = sale.get('sold_at', '')
                anonymous_buyer = generate_consistent_buyer_id(buyer_id, sold_at)
                
                history_text += (
                    f"**{i}. {sale.get('name', 'N/A')}**\n"
                    f"• Price: {sale.get('price', 'N/A')}\n"
                    f"• Sold: {sold_at}\n"
                    f"• Members: {sale.get('members', 'N/A')}\n"
                    f"• Buyer: `{anonymous_buyer}`\n\n"
                )
            
            if len(sales) > 10:
                history_text += f"... and {len(sales) - 10} more sales"
                
        else:  # purchase history
            from database import get_user_purchase_history
            purchases = await get_user_purchase_history(user_id)
            
            if not purchases:
                await callback_query.answer("No purchase history found!", show_alert=True)
                return
            
            import string
            import random
            
            def generate_consistent_seller_id(seller_id, sold_at):
                """Generate consistent anonymous seller ID"""
                random.seed(f"seller_{seller_id}_{sold_at}")
                chars = string.ascii_uppercase + string.digits
                return ''.join(random.choices(chars, k=10))
            
            history_text = f"🛒 **Purchase History ({len(purchases)} bought):**\n\n"
            for i, purchase in enumerate(purchases[-10:], 1):  # Show last 10 purchases
                seller_id = purchase.get('seller_id', 0)
                sold_at = purchase.get('sold_at', '')
                anonymous_seller = generate_consistent_seller_id(seller_id, sold_at)
                
                history_text += (
                    f"**{i}. {purchase.get('name', 'N/A')}**\n"
                    f"• Price: {purchase.get('price', 'N/A')}\n"
                    f"• Bought: {sold_at}\n"
                    f"• Members: {purchase.get('members', 'N/A')}\n"
                    f"• Seller: `{anonymous_seller}`\n\n"
                )
            
            if len(purchases) > 10:
                history_text += f"... and {len(purchases) - 10} more purchases"
        
        back_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Stats", callback_data=f"detailed_stats_{user_id}")]
        ])
        
        try:
            await callback_query.message.edit_text(history_text, reply_markup=back_keyboard)
            await callback_query.answer()
        except Exception as edit_error:
            print(f"Edit failed in history_callback_handler: {edit_error}")
            await callback_query.message.reply_text(history_text, reply_markup=back_keyboard)
            await callback_query.answer()
        
    except Exception as e:
        print(f"Error in history_callback_handler: {e}")
        await callback_query.answer("❌ An error occurred!", show_alert=True)


