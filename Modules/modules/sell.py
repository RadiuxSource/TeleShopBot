from pyrogram import filters, Client, enums
from pyrogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import chat_member_status
from Modules import teleshop_bot
from database import add_group_listing
import re

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

@teleshop_bot.on_message(filters.regex(r"^(➕\s*list\s*my\s*group)$", re.IGNORECASE) & filters.private)
async def sell_menu_handler(client: Client, message: Message):
    text = message.text.strip().lower()
    if "list my group" in text:
        prompt = (
            "📝 Please send the following details about your group in one message:\n"
            "- Group Name\n- Number of Members\n- Niche/Topic\n- Asking Price\n- Any notes\n\n"
            "Example:\n"
            "Group Name: Techies\nNumber of Members: 2000\nNiche/Topic: Technology\nAsking Price: $50\nNotes: Active daily"
        )
        await message.reply_text(prompt)
        
        # Wait for user to provide group details
        while True:
            response: Message = await client.listen(chat_id=message.chat.id, filters=filters.text, timeout=120)
            if not response:
                await message.reply_text(
                    "❌ Timeout or no response received. Please try again.",
                    reply_markup=sell_menu_keyboard
                )
                return
                
            # Parse the input and validate
            try:
                group_data = parse_group_data(response.text)
                if validate_group_data(group_data):
                    break
                else:
                    await message.reply_text(
                        "❌ Invalid format or missing required information. Please follow the example format and try again."
                    )
            except Exception as e:
                await message.reply_text(
                    f"❌ Error parsing input: {str(e)}\nPlease follow the example format exactly."
                )
        
        # Ask user to add bot to their group
        await message.reply_text(
            "👍 Details received! Now, please add this bot to your Telegram group and make it an admin with at least "
            "these permissions:\n\n"
            "- Read Messages\n"
            "- Manage Chat\n\n"
            "After adding the bot to your group, please send the group ID or group username (@example) here."
        )
        
        # Wait for user to provide group ID
        group_id_response: Message = await client.listen(chat_id=message.chat.id, filters=filters.text, timeout=300)
        if not group_id_response:
            await message.reply_text(
                "❌ Timeout or no response received. Please try again.",
                reply_markup=sell_menu_keyboard
            )
            return
        
        group_identifier = group_id_response.text.strip()
        
        # Verify group and ownership
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
            await client.send_message(group_chat.id, "👋 This bot has verified this group and it can be listed for sell now")
            # Update group data with verified information
            group_data.update({
                "group_id": group_chat.id,
                "username": group_chat.username if hasattr(group_chat, 'username') else None,
                "actual_members": group_chat.members_count if hasattr(group_chat, 'members_count') else 0,
                "seller_id": message.from_user.id,
                "seller": f"{message.from_user.mention}" if message.from_user else "N/A"
            })
            
            # Double-check with the user
            confirmation_text = (
                f"📊 **Group Information**\n\n"
                f"**Group Name:** {group_data['name']}\n"
                f"**Group ID:** {group_data['group_id']}\n"
                f"**Username:** {('@' + group_data['username']) if group_data['username'] else 'None'}\n"
                f"**Members:** {group_data['actual_members']} (you reported: {group_data['members']})\n"
                f"**Niche/Topic:** {group_data['niche']}\n"
                f"**Asking Price:** {group_data['price']}\n"
                f"**Notes:** {group_data['notes']}\n\n"
                f"Is this information correct? Confirm to list your group for sale."
            )
            
            confirm_keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_listing_{group_chat.id}"),
                    InlineKeyboardButton("❌ Cancel", callback_data="cancel_listing")
                ]
            ])
            
            confirmation_message = await message.reply_text(confirmation_text, reply_markup=confirm_keyboard)
            
            # Wait for the callback query response
            callback_query = await client.listen(
                chat_id=message.chat.id,
                filters=filters.user(message.from_user.id) & 
                        filters.regex(r"^confirm_listing_|^cancel_listing"),
                timeout=120,
                listener_type=enums.ListenerTypes.CALLBACK_QUERY
            )
            
            if callback_query:
                if callback_query.data.startswith("confirm_listing_"):
                    # Extract group ID from callback data
                    group_id = int(callback_query.data.split("_")[-1])
                    
                    # Add to database
                    await add_group_listing(group_data)
                    
                    # Update the confirmation message
                    await callback_query.message.edit_text(
                        f"✅ Group successfully listed for sale! (ID: {group_id})\n"
                        "Buyers will be able to see your listing now."
                    )
                    
                    # Acknowledge the callback
                    await callback_query.answer("Group listing confirmed!")
                    
                    await message.reply_text(
                        "Your group is now listed in our marketplace. You'll be notified when someone shows interest.",
                        reply_markup=sell_menu_keyboard
                    )
                else:  # Cancel listing
                    # Update the confirmation message
                    await callback_query.message.edit_text(
                        "❌ Group listing cancelled. You can try again later."
                    )
                    
                    # Acknowledge the callback
                    await callback_query.answer("Listing cancelled")
                    
                    await message.reply_text(
                        "Group listing was cancelled. You can try again anytime.",
                        reply_markup=sell_menu_keyboard
                    )
            else:
                # Timeout occurred
                await confirmation_message.edit_text(
                    "⌛ Confirmation timed out. Your group was not listed. Please try again."
                )
                await message.reply_text(
                    "Operation timed out. Please try again.",
                    reply_markup=sell_menu_keyboard
                )
            
        except Exception as e:
            await message.reply_text(
                f"❌ Error verifying group: {str(e)}\nPlease make sure the group ID or username is correct and the bot is added as an admin.",
                reply_markup=sell_menu_keyboard
            )

def parse_group_data(text):
    """Parse the group data from the user's input text"""
    lines = text.split('\n')
    data = {}
    
    for line in lines:
        if ":" not in line:
            continue
            
        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip()
        
        if "group name" in key:
            data["name"] = value
        elif "number of members" in key or "members" in key:
            data["members"] = value
        elif "niche" in key or "topic" in key:
            data["niche"] = value
        elif "price" in key or "asking price" in key:
            data["price"] = value
        elif "note" in key:
            data["notes"] = value
    
    return data

def validate_group_data(data):
    """Validate that all required fields are present and in the correct format"""
    required_fields = ["name", "members", "niche", "price"]
    for field in required_fields:
        if field not in data or not data[field]:
            return False
    
    # Try to convert members to a number
    try:
        # Remove any non-numeric characters like commas or 'k'
        members_str = re.sub(r'[^0-9]', '', data["members"])
        int(members_str)
    except ValueError:
        return False
    
    # Make sure price contains a currency symbol or number
    if not re.search(r'[$€£¥]|\d', data["price"]):
        return False
    
    return True