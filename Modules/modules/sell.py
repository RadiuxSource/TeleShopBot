from pyrogram import filters, Client
from pyrogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from Modules import teleshop_bot
from database import add_group_listing

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

@teleshop_bot.on_message(filters.text & filters.private, group = 3)
async def sell_menu_handler(client: Client, message: Message):
    text = message.text.strip().lower()
    if text == "➕ list my group" or text == "list my group":
        prompt = (
            "📝 Please send the following details about your group in one message:\n"
            "- Group Name\n- Number of Members\n- Niche/Topic\n- Asking Price\n- Any notes\n\n"
            "Example:\n"
            "Group Name: Techies\nNumber of Members: 2000\nNiche/Topic: Technology\nAsking Price: $50\nNotes: Active daily"
        )
        await message.reply_text(prompt)
        response: Message = await client.listen(message.chat.id, filters=filters.text, timeout=120)
        if response:
            lines = response.text.split("\n")
            # Simple parsing, expects order
            group_data = {
                "name": lines[0].replace("Group Name:", "").strip() if len(lines) > 0 else "N/A",
                "members": lines[1].replace("Number of Members:", "").strip() if len(lines) > 1 else "N/A",
                "niche": lines[2].replace("Niche/Topic:", "").strip() if len(lines) > 2 else "N/A",
                "price": lines[3].replace("Asking Price:", "").strip() if len(lines) > 3 else "N/A",
                "notes": lines[4] if len(lines) > 4 else "",
                "seller": f"{message.from_user.mention}" if message.from_user else "N/A"
            }
            await add_group_listing(group_data)
            await message.reply_text(
                "✅ Group listed for sale!\nYou can edit or remove your listing later.",
                reply_markup=sell_menu_keyboard
            )
        else:
            await message.reply_text(
                "❌ Timeout or no response received. Please try again.",
                reply_markup=sell_menu_keyboard
            )
    elif text == "🔙 back to sell menu" or text == "back to sell menu":
        await sell_command(client, message)