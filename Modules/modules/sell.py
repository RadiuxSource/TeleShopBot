from pyrogram import filters, Client, enums
from pyrogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import chat_member_status
from Modules import teleshop_bot, LOG_GROUP
from database import add_group_listing, check_group_exists
import re
import asyncio
from datetime import datetime
from pytz import timezone

# Keyboard for selling groups
sell_menu_keyboard = ReplyKeyboardMarkup(
    [
        [KeyboardButton("➕ List My Group")],
        [KeyboardButton("🔙 Back to Main Menu")],
    ],
    resize_keyboard=True
)

@teleshop_bot.on_message(filters.command(["sell"]) & filters.private)
async def sell_command(client: Client, message: Message):
    await message.reply_text(
        "💰 **Sell Groups**\n\nChoose an option below:",
        reply_markup=sell_menu_keyboard
    )

@teleshop_bot.on_message(filters.text & filters.private, group=5)  # Medium priority
async def sell_menu_handler(client: Client, message: Message):
    text = message.text.strip().lower()
    
    # Only handle "list my group" specifically
    if "list my group" in text or "➕" in text:
        print(f"Sell handler processing: '{text}'")  # Debug log
        
        # Remove keyboard during listing process
        await message.reply_text(
            "📝 **Starting Group Listing Process...**\n\n"
            "You can cancel at any time by typing 'cancel' or using the cancel button.",
            reply_markup=None  # Remove keyboard
        )
        
        # Show warning message first
        warning_text = (
            "⚠️ **IMPORTANT WARNING** ⚠️\n\n"
            "Before listing your group, please read carefully:\n\n"
            "🚫 **You may get BLACKLISTED if you:**\n"
            "• Provide fake or incorrect group information\n"
            "• Try to sell fake/non-existent groups\n"
            "• Set extremely unrealistic prices\n"
            "• Spam multiple fake listings\n"
            "• Mislead buyers with false claims\n\n"
            "❗ **Blacklisted users cannot use this bot again**\n\n"
            "✅ Only list genuine groups you own with accurate information.\n\n"
            "Do you understand and agree to proceed responsibly?"
        )
        
        warning_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ I Understand & Agree", callback_data="agree_warning"),
                InlineKeyboardButton("❌ Cancel Listing", callback_data="cancel_warning")
            ]
        ])
        
        warning_message = await message.reply_text(warning_text, reply_markup=warning_keyboard)
        
        # Wait for warning acknowledgment
        warning_callback = await client.listen(
            chat_id=message.chat.id,
            filters=filters.user(message.from_user.id) & filters.regex(r"^agree_warning|^cancel_warning"),
            timeout=120,
            listener_type=enums.ListenerTypes.CALLBACK_QUERY
        )
        
        if not warning_callback:
            await warning_message.edit_text(
                "⌛ Warning acknowledgment timed out. Returning to sell menu.",
                reply_markup=sell_menu_keyboard
            )
            return
        
        if warning_callback.data == "cancel_warning":
            await warning_callback.answer("Listing cancelled")
            await warning_callback.message.edit_text(
                "❌ Group listing cancelled. You can start again anytime."
            )
            await message.reply_text(
                "💰 **Sell Groups**\n\nChoose an option below:",
                reply_markup=sell_menu_keyboard
            )
            return
        
        await warning_callback.answer("Warning acknowledged!")
        
        # Initialize group data
        group_data = {}
        
        # Step 1: Ask for group ID first to fetch name and members automatically
        # Create an add to group button with cancel option
        bot_username = (await client.get_me()).username
        add_to_group_url = f"https://t.me/{bot_username}?startgroup=true&admin=change_info+invite_users+manage_call+other"
        
        add_to_group_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Bot to Group", url=add_to_group_url)],
            [InlineKeyboardButton("❌ Cancel Listing", callback_data="cancel_listing_process")]
        ])
        
        await warning_callback.message.edit_text(
            "📝 **Step 1/4: Group Information**\n\n"
            "Please add this bot to your Telegram group as an admin, then send the group ID or username (@example):\n\n"
            "💡 You can also type 'cancel' to return to the sell menu.",
            reply_markup=add_to_group_keyboard
        )
        
        # Wait for user to provide group ID
        group_id_response: Message = await client.listen(chat_id=message.chat.id, filters=filters.text, timeout=300)
        if not group_id_response:
            await message.reply_text(
                "❌ Timeout or no response received. Returning to sell menu.",
                reply_markup=sell_menu_keyboard
            )
            return
        
        # Check for cancel commands
        if (group_id_response.text.strip().lower() in ['cancel', 'stop', 'exit'] or 
            "back to main menu" in group_id_response.text.strip().lower() or 
            "🔙" in group_id_response.text):
            await message.reply_text(
                "❌ Group listing cancelled. Returning to sell menu.",
                reply_markup=sell_menu_keyboard
            )
            return
        
        group_identifier = group_id_response.text.strip()
        
        # Verify and fetch group information
        try:
            # Handle both numeric IDs and usernames
            if group_identifier.startswith('@'):
                group_chat = await client.get_chat(group_identifier)
            else:
                try:
                    group_chat = await client.get_chat(int(group_identifier))
                except ValueError:
                    group_chat = await client.get_chat(group_identifier)
            
            # Verify bot is in the group
            try:
                bot_member = await client.get_chat_member(group_chat.id, (await client.get_me()).id)
                if bot_member.status not in [chat_member_status.ChatMemberStatus.ADMINISTRATOR, chat_member_status.ChatMemberStatus.OWNER]:
                    await message.reply_text(
                        "❌ I need to be an admin in the group to verify ownership and manage listings. "
                        "Please make me an admin and try again.",
                        reply_markup=sell_menu_keyboard
                    )
                    return
            except Exception as e:
                await message.reply_text(
                    f"❌ Couldn't verify my admin status in the group: {str(e)}",
                    reply_markup=sell_menu_keyboard
                )
                return
            
            # Verify user is the owner
            user_member = await client.get_chat_member(group_chat.id, message.from_user.id)
            if user_member.status != chat_member_status.ChatMemberStatus.OWNER:
                await message.reply_text(
                    "❌ Only the group owner can sell a group. You don't appear to be the owner of this group.",
                    reply_markup=sell_menu_keyboard
                )
                return
            
            # Auto-fetch group information
            group_data["name"] = group_chat.title
            group_data["members"] = str(group_chat.members_count) if hasattr(group_chat, 'members_count') else "Unknown"
            group_data["group_id"] = group_chat.id
            group_data["username"] = group_chat.username if hasattr(group_chat, 'username') else None
            
            await client.send_message(group_chat.id, "👋 This bot has verified this group and it can be listed for sell now")
            
            # Database duplicate check only
            existing_group = await check_group_exists(group_chat.id)
            if existing_group:
                await message.reply_text(
                    f"❌ This group is already listed for sale!\n\n"
                    f"**Listed by:** {existing_group.get('seller', 'Unknown')}\n"
                    f"**Price:** {existing_group.get('price', 'Not specified')}\n"
                    f"**Listed on:** {existing_group.get('created_at', 'Unknown date')}(IST)\n\n"
                    "Each group can only be listed once. If you believe this is an error, please contact support.",
                    reply_markup=sell_menu_keyboard
                )
                return
            
        except Exception as e:
            await message.reply_text(
                f"❌ Error verifying group: {str(e)}\nPlease make sure the group ID or username is correct and the bot is added as an admin.",
                reply_markup=sell_menu_keyboard
            )
            return
        
        # Step 2: Ask for group creation year with cancel option
        year_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("2016", callback_data="year_2016"), InlineKeyboardButton("2017", callback_data="year_2017"), InlineKeyboardButton("2018", callback_data="year_2018")],
            [InlineKeyboardButton("2019", callback_data="year_2019"), InlineKeyboardButton("2020", callback_data="year_2020"), InlineKeyboardButton("2021", callback_data="year_2021")],
            [InlineKeyboardButton("2022", callback_data="year_2022"), InlineKeyboardButton("2023", callback_data="year_2023"), InlineKeyboardButton("2024", callback_data="year_2024")],
            [InlineKeyboardButton("❌ Cancel Listing", callback_data="cancel_listing_process")]
        ])
        
        await message.reply_text(
            f"✅ **Group Found:** {group_data['name']}\n"
            f"📊 **Members:** {group_data['members']}\n\n"
            "📅 **Step 2/4: Group Creation Year**\n\n"
            "When was this group created? Select the year:",
            reply_markup=year_keyboard
        )
        
        # Wait for year selection
        year_callback = await client.listen(
            chat_id=message.chat.id,
            filters=filters.user(message.from_user.id) & filters.regex(r"^year_|^cancel_listing_process"),
            timeout=120,
            listener_type=enums.ListenerTypes.CALLBACK_QUERY
        )
        
        if not year_callback:
            await message.reply_text("❌ Timeout. Returning to sell menu.", reply_markup=sell_menu_keyboard)
            return
        
        if year_callback.data == "cancel_listing_process":
            await year_callback.answer("Listing cancelled")
            await year_callback.message.edit_text("❌ Group listing cancelled.")
            await message.reply_text(
                "💰 **Sell Groups**\n\nChoose an option below:",
                reply_markup=sell_menu_keyboard
            )
            return
        
        selected_year = year_callback.data.split("_")[1]
        group_data["year"] = selected_year
        await year_callback.answer(f"Year {selected_year} selected!")
        
        # Step 3: Ask for month with cancel option
        month_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("January", callback_data="month_01"), InlineKeyboardButton("February", callback_data="month_02"), InlineKeyboardButton("March", callback_data="month_03")],
            [InlineKeyboardButton("April", callback_data="month_04"), InlineKeyboardButton("May", callback_data="month_05"), InlineKeyboardButton("June", callback_data="month_06")],
            [InlineKeyboardButton("July", callback_data="month_07"), InlineKeyboardButton("August", callback_data="month_08"), InlineKeyboardButton("September", callback_data="month_09")],
            [InlineKeyboardButton("October", callback_data="month_10"), InlineKeyboardButton("November", callback_data="month_11"), InlineKeyboardButton("December", callback_data="month_12")],
            [InlineKeyboardButton("❌ Cancel Listing", callback_data="cancel_listing_process")]
        ])
        
        await year_callback.message.edit_text(
            f"✅ **Year:** {selected_year}\n\n"
            "📆 **Step 3/4: Creation Month**\n\n"
            "Which month was the group created in?",
            reply_markup=month_keyboard
        )
        
        # Wait for month selection
        month_callback = await client.listen(
            chat_id=message.chat.id,
            filters=filters.user(message.from_user.id) & filters.regex(r"^month_|^cancel_listing_process"),
            timeout=120,
            listener_type=enums.ListenerTypes.CALLBACK_QUERY
        )
        
        if not month_callback:
            await message.reply_text("❌ Timeout. Returning to sell menu.", reply_markup=sell_menu_keyboard)
            return
        
        if month_callback.data == "cancel_listing_process":
            await month_callback.answer("Listing cancelled")
            await month_callback.message.edit_text("❌ Group listing cancelled.")
            await message.reply_text(
                "💰 **Sell Groups**\n\nChoose an option below:",
                reply_markup=sell_menu_keyboard
            )
            return
        
        month_names = {
            "01": "January", "02": "February", "03": "March", "04": "April",
            "05": "May", "06": "June", "07": "July", "08": "August",
            "09": "September", "10": "October", "11": "November", "12": "December"
        }
        selected_month_num = month_callback.data.split("_")[1]
        selected_month_name = month_names[selected_month_num]
        group_data["month"] = selected_month_name
        await month_callback.answer(f"{selected_month_name} selected!")
        
        # Step 4: Ask for price
        price_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("$4", callback_data="price_4"), InlineKeyboardButton("$5", callback_data="price_5"), InlineKeyboardButton("$6", callback_data="price_6")],
            [InlineKeyboardButton("$7", callback_data="price_7"), InlineKeyboardButton("$8", callback_data="price_8"), InlineKeyboardButton("$9", callback_data="price_9")],
            [InlineKeyboardButton("$10", callback_data="price_10"), InlineKeyboardButton("$11", callback_data="price_11"), InlineKeyboardButton("$12", callback_data="price_12")],
            [InlineKeyboardButton("💰 Custom Price", callback_data="price_custom")]
        ])
        
        await month_callback.message.edit_text(
            f"✅ **Year:** {selected_year}\n"
            f"✅ **Month:** {selected_month_name}\n\n"
            "💰 **Step 4/4: Set Price**\n\n"
            "Choose your asking price:",
            reply_markup=price_keyboard
        )
        
        # Wait for price selection
        price_callback = await client.listen(
            chat_id=message.chat.id,
            filters=filters.user(message.from_user.id) & filters.regex(r"^price_"),
            timeout=120,
            listener_type=enums.ListenerTypes.CALLBACK_QUERY
        )
        
        if not price_callback:
            await message.reply_text("❌ Timeout. Please try again.", reply_markup=sell_menu_keyboard)
            return
        
        # Handle custom price input
        if price_callback.data == "price_custom":
            await price_callback.answer("Enter your custom price!")
            await price_callback.message.edit_text(
                f"✅ **Year:** {selected_year}\n"
                f"✅ **Month:** {selected_month_name}\n\n"
                "💰 **Custom Price**\n\n"
                "Please enter your asking price in dollars (e.g., 15 or $15):"
            )
            
            # Wait for custom price input
            custom_price_response = await client.listen(
                chat_id=message.chat.id, 
                filters=filters.text & filters.user(message.from_user.id), 
                timeout=120
            )
            
            if not custom_price_response:
                await message.reply_text("❌ Timeout. Please try again.", reply_markup=sell_menu_keyboard)
                return
            
            # Check for navigation commands
            if "back to main menu" in custom_price_response.text.strip().lower() or "🔙" in custom_price_response.text:
                await message.reply_text(
                    "Operation cancelled. Returning to sell menu.",
                    reply_markup=sell_menu_keyboard
                )
                return
            
            # Validate and parse custom price
            custom_price_text = custom_price_response.text.strip()
            try:
                # Extract numeric value from input
                price_match = re.search(r'\d+', custom_price_text)
                if not price_match:
                    await message.reply_text(
                        "❌ Invalid price format. Please enter a valid number (e.g., 15 or $15).",
                        reply_markup=sell_menu_keyboard
                    )
                    return
                
                price_value = int(price_match.group())
                
                # Validate price range (optional - you can adjust or remove this)
                if price_value < 1 or price_value > 1000:
                    await message.reply_text(
                        "❌ Price must be between $1 and $1000. Please try again.",
                        reply_markup=sell_menu_keyboard
                    )
                    return
                
                selected_price = str(price_value)
                group_data["price"] = f"${selected_price}"
                
                await message.reply_text(
                    f"✅ Custom price ${selected_price} set successfully!"
                )
                
            except ValueError:
                await message.reply_text(
                    "❌ Invalid price format. Please enter a valid number.",
                    reply_markup=sell_menu_keyboard
                )
                return
        else:
            # Handle predefined price selection
            selected_price = price_callback.data.split("_")[1]
            group_data["price"] = f"${selected_price}"
            await price_callback.answer(f"${selected_price} selected!")
            await price_callback.message.delete()
        
        # Update group data with additional information
        group_data.update({
            "actual_members": group_chat.members_count if hasattr(group_chat, 'members_count') else 0,
            "seller_id": message.from_user.id,
            "seller": f"Anonymous Seller",  # Use anonymous name instead of real name
            "niche": f"Created in {selected_month_name} {selected_year}",  # Using date as niche for now
            "notes": f"Group created: {selected_month_name} {selected_year}"
        })
        
        # Final confirmation
        confirmation_text = (
            f"📊 **Final Confirmation**\n\n"
            f"**Group Name:** {group_data['name']}\n"
            f"**Group ID:** {group_data['group_id']}\n"
            f"**Username:** {('@' + group_data['username']) if group_data['username'] else 'None'}\n"
            f"**Members:** {group_data['actual_members']}\n"
            f"**Created:** {group_data['month']} {group_data['year']}\n"
            f"**Asking Price:** {group_data['price']}\n\n"
            f"Confirm to list your group for sale?"
        )
        
        confirm_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_listing_{group_chat.id}"),
                InlineKeyboardButton("❌ Cancel", callback_data="cancel_listing")
            ]
        ])
        
        confirmation_message = await price_callback.message.reply_text(confirmation_text, reply_markup=confirm_keyboard)
        
        # Wait for final confirmation
        callback_query = await client.listen(
            chat_id=message.chat.id,
            filters=filters.user(message.from_user.id) & 
                    filters.regex(r"^confirm_listing_|^cancel_listing"),
            timeout=120,
            listener_type=enums.ListenerTypes.CALLBACK_QUERY
        )
        
        if callback_query:
            if callback_query.data.startswith("confirm_listing_"):
                india_tz = timezone('Asia/Kolkata')
                group_data['created_at'] = datetime.now(india_tz).strftime('%d-%b-%Y %I:%M %p')
                
                # Add to database
                success = await add_group_listing(group_data)
                if success:
                    # Announce new listing in log group
                    listing_announce = (
                        f"📢 **New Group Listing!**\n\n"
                        f"**Group Name:** {group_data['name']}\n"
                        f"**Group ID:** {group_data['group_id']}\n"
                        f"**Username:** {('@' + group_data['username']) if group_data['username'] else 'None'}\n"
                        f"**Members:** {group_data['actual_members']}\n"
                        f"**Created:** {group_data['month']} {group_data['year']}\n"
                        f"**Price:** {group_data['price']}\n"
                        f"**Seller:** {group_data['seller']}\n"
                        f"**Listed at:** {group_data['created_at']} IST"
                    )
                    await client.send_message(LOG_GROUP, listing_announce)
                if success:
                    # Update user activity
                    from database import update_user_activity
                    await update_user_activity(message.from_user.id, "group_listed")
                    
                    # Get current total listings for confirmation
                    from database import fetch_group_listings
                    all_listings = await fetch_group_listings()
                    
                    await callback_query.message.edit_text(
                        f"✅ **Group Successfully Listed!**\n\n"
                        f"**Group:** {group_data['name']}\n"
                        f"**Price:** {group_data['price']}\n"
                        f"**Listing ID:** {group_data['group_id']}\n"
                        f"**Listed at:** {group_data['created_at']} IST\n\n"
                        "Your group is now listed for sale. Interested buyers will contact you directly.\n"
                        f"📊 **Total active listings:** {len(all_listings)}\n\n"
                    )
                else:
                    await callback_query.message.edit_text(
                        "❌ **Error:** Failed to save your group listing. Please try again."
                    )
                    await callback_query.answer("Listing failed!")

            else:
                await callback_query.message.edit_text(
                    "❌ Group listing cancelled. You can try again later."
                )
                
                await callback_query.answer("Listing cancelled")
                
                await message.reply_text(
                    "Group listing was cancelled. You can try again anytime.",
                    reply_markup=sell_menu_keyboard
                )
        else:
            await confirmation_message.edit_text(
                "⌛ Confirmation timed out. Your group was not listed. Please try again."
            )

# Handle cancel listing process callback
@teleshop_bot.on_callback_query(filters.regex(r"^cancel_listing_process$"))
async def cancel_listing_process_callback(client: Client, callback_query):
    try:
        await callback_query.answer("Listing process cancelled")
        await callback_query.message.edit_text("❌ Group listing process cancelled.")
        
        # Send sell menu
        await client.send_message(
            callback_query.message.chat.id,
            "💰 **Sell Groups**\n\nChoose an option below:",
            reply_markup=sell_menu_keyboard
        )
        
    except Exception as e:
        print(f"Error in cancel_listing_process_callback: {e}")
        await callback_query.answer("❌ Error occurred!")

# Handle cancel listing callback (for final confirmation)
@teleshop_bot.on_callback_query(filters.regex(r"^cancel_listing$"))
async def cancel_listing_callback(client: Client, callback_query):
    try:
        await callback_query.answer("Listing cancelled")
        await callback_query.message.edit_text("❌ Group listing cancelled.")
        
        # Send sell menu
        await client.send_message(
            callback_query.message.chat.id,
            "💰 **Sell Groups**\n\nChoose an option below:",
            reply_markup=sell_menu_keyboard
        )
        
    except Exception as e:
        print(f"Error in cancel_listing_callback: {e}")
        await callback_query.answer("❌ Error occurred!")
        await callback_query.answer("❌ Error occurred!")
