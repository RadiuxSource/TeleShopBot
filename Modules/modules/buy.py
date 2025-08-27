from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from Modules import teleshop_bot
from database import fetch_group_listings

# Helper to format group info
def format_group(group, idx, total):
    return (
        f"📝 **Group {idx+1} of {total}:**\n\n"
        f"**Group Name:** {group.get('name', 'N/A')}\n"
        f"• Members: {group.get('members', 'N/A')}\n"
        f"• Niche: {group.get('niche', 'N/A')}\n"
        f"• Price: {group.get('price', 'N/A')}\n"
        f"• Seller: {group.get('seller', 'N/A')}\n"
        f"{'• ' + group.get('notes', '') if group.get('notes') else ''}"
    )

# Entry point: show first group
@teleshop_bot.on_message(filters.command(["buy"]) & filters.private)
async def buy_command(client: Client, message: Message):
    groups = await fetch_group_listings()
    if not groups:
        await message.reply_text(
            "❌ No groups are currently listed for sale."
        )
        return

    idx = 0
    total = len(groups)
    group = groups[idx]
    kb = []
    if total > 1:
        kb = [[
            InlineKeyboardButton("⬅️ Back", callback_data=f"buy_back_{idx}"),
            InlineKeyboardButton("➡️ Next", callback_data=f"buy_next_{idx}")
        ]]
    await message.reply_text(
        format_group(group, idx, total),
        reply_markup=InlineKeyboardMarkup(kb) if kb else None
    )

# Callback for next/back navigation
@teleshop_bot.on_callback_query(filters.regex(r"^buy_(next|back)_(\d+)"))
async def buy_pagination_callback(client: Client, callback_query):
    action, idx = callback_query.data.split('_')[1:]
    idx = int(idx)
    groups = await fetch_group_listings()
    total = len(groups)
    if not groups or total == 0:
        await callback_query.answer("No groups found.", show_alert=True)
        return

    if action == "next":
        idx = (idx + 1) % total
    elif action == "back":
        idx = (idx - 1 + total) % total

    group = groups[idx]
    kb = []
    if total > 1:
        kb = [[
            InlineKeyboardButton("⬅️ Back", callback_data=f"buy_back_{idx}"),
            InlineKeyboardButton("➡️ Next", callback_data=f"buy_next_{idx}")
        ]]
    await callback_query.message.edit_text(
        format_group(group, idx, total),
        reply_markup=InlineKeyboardMarkup(kb) if kb else None
    )
    await callback_query.answer()