from Modules import zenova, MSG_GROUP, SUDO_USERS
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import re


IGNORE = [1062297223, 1705065791, 7225125341]
@zenova.on_message(filters.private & filters.incoming & ~filters.user(SUDO_USERS + IGNORE), group=2)
async def forward_private_message(client: Client, message: Message) -> None:
    """Forward private message to MSG_GROUP and reply with user id when not forwarded."""
    k: Message = await message.forward(MSG_GROUP, disable_notification=True)
    d = InlineKeyboardMarkup(
    [[InlineKeyboardButton("User account ↗", user_id=message.from_user.id)]]
    )
    m = f'''
#Livegram

 - User id: `{message.from_user.id}`
 - Message id: `{message.id}`
'''
    await k.reply(m, disable_notification=True, reply_markup=d)


@zenova.on_message(filters.group & filters.reply & filters.chat(MSG_GROUP) & filters.user(SUDO_USERS))
async def reply_to_forwarded_message(client: Client, message: Message) -> None:
    replied = message.reply_to_message
    m_text = replied.text or ""
    p = r"User id:\s*(\d+).*?Message id:\s*(\d+)"
    k = re.search(p, m_text, re.DOTALL)
    if k:
        user_id, msg_id = k.groups()
        try:
            m: Message = await message.copy(int(user_id), reply_to_message_id=int(msg_id))
        except Exception as e:
            return await message.reply(f"**⚠️ An error occurred:**\n```py\n{e}```")
        await m.reply("**📩 Attention! This is a message from my admins. Please take note! 🙌**", quote=True)
        return await message.reply("**✅ Message forwarded successfully!**")
    # Check if admin directly replied message which is forwarded from another chat/user
    if replied.forward_from or replied.forward_origin or getattr(replied, "forward_from_chat", None):
        return await message.reply("⚠️ Please reply to the message that contains `#Livegram` and user details.")
    return
