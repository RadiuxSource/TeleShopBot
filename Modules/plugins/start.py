from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from config import Settings
from Questions import get_solution_video, get_explaination_govt, get_explaination_tenth
from utils.translator import translate_async
from database import add_served_user, add_served_chat
from Modules import zenova, BOT_NAME, BOT_USERNAME, NO_SOLN, MSG_GROUP


# start_msg = f"""
# ʜᴇʏ 🙋‍♂️, ɪ ᴀᴍ **{BOT_NAME}🤖**!

# ɪ ᴀᴍ ᴄᴀᴘᴀʙʟᴇ ᴏꜰ ꜱᴇɴᴅɪɴɢ Qᴜᴀʟɪᴛʏ Qᴜᴇꜱᴛɪᴏɴꜱ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘꜱ ᴀᴄᴄᴏʀᴅɪɴɢ ᴛᴏ ʏᴏᴜʀ ꜱᴛʀᴇᴀᴍ, Qᴜᴇꜱᴛɪᴏɴ ʟᴇᴠᴇʟꜱ ᴀɴᴅ ᴍᴜᴄʜ ᴍᴏʀᴇ 😎.

# ᴊᴜꜱᴛ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴇɴᴊᴏʏ ᴀ ɴᴇᴡ Qᴜɪᴢ ᴘᴏʟʟ ᴀꜰᴛᴇʀ ᴇᴠᴇʀʏ 30 ᴍɪɴꜱ 🎉.

# ʏᴏᴜ ᴄᴀɴ ᴄʜᴀɴɢᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘ's ꜱᴇᴛᴛɪɴɢꜱ ᴏꜰ Qᴜɪᴢ ᴠɪᴀ /setting ᴄᴏᴍᴍᴀɴᴅ.
# """

start_msg = f"""
ʜᴇʏ 🙋‍♂️, ɪ ᴀᴍ **{BOT_NAME}🤖**!

**{BOT_NAME}** ɪꜱ ᴀ ғᴇᴀᴛᴜʀᴇ-ʀɪᴄʜ Qᴜɪᴢ ʙᴏᴛ ꜰᴏʀ Tᴇʟᴇɢʀᴀᴍ, ᴅᴇꜱɪɢɴᴇᴅ ᴀꜱ ᴀ ᴍᴏᴅᴇʀɴ ᴀʟᴛᴇʀɴᴀᴛɪᴠᴇ ᴛᴏ @quizbot.  
Cʀᴇᴀᴛᴇ, ᴘʟᴀʏ, ᴀɴᴅ ᴇɴᴊᴏʏ ɪɴᴛᴇʀᴀᴄᴛɪᴠᴇ Qᴜɪᴢᴢᴇꜱ ᴡɪᴛʜ ᴍᴜʟᴛɪᴘʟᴇ Qᴜᴇꜱᴛɪᴏɴ ᴛʏᴘᴇꜱ, ᴇxᴀᴍ ᴄᴀᴛᴇɢᴏʀɪᴇꜱ, ᴀɴᴅ ᴇɴɢᴀɢɪɴɢ ꜰᴇᴀᴛᴜʀᴇꜱ!

📚 **Mᴀɪɴ Fᴇᴀᴛᴜʀᴇꜱ:**
• Aᴜᴛᴏ-ǫᴜɪᴢ Pᴏʟʟꜱ ᴇᴠᴇʀʏ 30 ᴍɪɴꜱ ɪɴ Gʀᴏᴜᴘꜱ  
• Cʀᴇᴀᴛᴇ ʏᴏᴜʀ ᴏᴡɴ Qᴜɪᴢᴢᴇꜱ (ᴡɪᴛʜ ᴅᴀᴛᴀʙᴀꜱᴇ ᴀꜱ ᴡᴇʟʟ ᴀꜱ ᴍᴀɴᴜᴀʟ ǫᴜᴇꜱᴛɪᴏɴꜱ)  
• Cᴜꜱᴛᴏᴍɪᴢᴀʙʟᴇ Qᴜᴇꜱᴛɪᴏɴ ʟᴇᴠᴇʟꜱ, ꜱᴛʀᴇᴀᴍꜱ & ᴇxᴀᴍ ᴛʏᴘᴇꜱ  
• Dᴇᴛᴀɪʟᴇᴅ ꜱᴏʟᴜᴛɪᴏɴꜱ & ᴇxᴘʟᴀɴᴀᴛɪᴏɴꜱ ꜰᴏʀ Qᴜᴇꜱᴛɪᴏɴꜱ  

👥 **Uꜱᴇʀ Fᴇᴀᴛᴜʀᴇꜱ:**
• Pᴇʀꜰᴏʀᴍᴀɴᴄᴇ Tʀᴀᴄᴋɪɴɢ & Pᴇʀꜱᴏɴᴀʟ Pʀᴏꜰɪʟᴇ  
• Gʟᴏʙᴀʟ Lᴇᴀᴅᴇʀʙᴏᴀʀᴅꜱ  
• Qᴜɪᴢ Sʜᴀʀɪɴɢ & Mᴀɴᴀɢᴇᴍᴇɴᴛ

⚙️ **Gʀᴏᴜᴘ Fᴇᴀᴛᴜʀᴇꜱ:**
• Cᴜꜱᴛᴏᴍ Qᴜɪᴢ Sᴇᴛᴛɪɴɢꜱ  
• Gʀᴏᴜᴘ Qᴜɪᴢ Sᴛᴀᴛɪᴄꜱ  
• Mᴜʟᴛɪ-ʟᴀɴɢᴜᴀɢᴇ ꜱᴜᴘᴘᴏʀᴛ

👉 ᴜꜱᴇ /help ᴛᴏ ᴇxᴘʟᴏʀᴇ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅꜱ, ᴏʀ ᴠɪꜱɪᴛ [quizora.live](https://quizora.live) ꜰᴏʀ ꜰᴜʟʟ ᴅᴏᴄꜱ!
"""


help_text = """
ʜᴇʏ! ʜᴇʀᴇ ᴀʀᴇ sᴏᴍᴇ ᴏꜰ ᴍʏ ᴄᴏᴍᴍᴀɴᴅꜱ:

📌 ʙᴀsɪᴄ ᴄᴏᴍᴍᴀɴᴅs:
  ➤ /start - sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ
  ➤ /help - sʜᴏᴡ ᴛʜɪs ʜᴇʟᴘ ᴍᴇssᴀɢᴇ
  ➤ /feedback - sᴇɴᴅ ғᴇᴇᴅʙᴀᴄᴋ ᴛᴏ ʙᴏᴛ ᴀᴅᴍɪɴs

👤 ᴘʀᴏғɪʟᴇ & sᴛᴀᴛs:
  ➤ /profile - ᴠɪᴇᴡ & ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ᴘʀᴏғɪʟᴇ
  ➤ /mstat - ᴠɪᴇᴡ ʏᴏᴜʀ ǫᴜɪᴢ ᴘᴇʀғᴏʀᴍᴀɴᴄᴇ
  ➤ /gstat - ᴠɪᴇᴡ ɢʀᴏᴜᴘ ǫᴜɪᴢ sᴛᴀᴛs
  ➤ /top - sᴇᴇ ᴛᴏᴘ ɢʟᴏʙᴀʟ sᴄᴏʀᴇʀs

📝 ǫᴜɪᴢ ᴄʀᴇᴀᴛɪᴏɴ:
  ➤ /create_quiz - ᴄʀᴇᴀᴛᴇ ᴀ ɴᴇᴡ ǫᴜɪᴢ
  ➤ /cancel - ᴄᴀɴᴄᴇʟ ᴏɴɢᴏɪɴɢ ǫᴜɪᴢ ᴄʀᴇᴀᴛɪᴏɴ
  ➤ /my_quiz - ʟɪsᴛ ʏᴏᴜʀ ᴄʀᴇᴀᴛᴇᴅ ǫᴜɪᴢᴢᴇs
  ➤ /view_[quiz_id] - ᴠɪᴇᴡ sᴘᴇᴄɪғɪᴄ ǫᴜɪᴢ
  ➤ /group_quiz [quiz_id] - sᴛᴀʀᴛ ǫᴜɪᴢ ɪɴ ɢʀᴏᴜᴘ

⚙️ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs:
  ➤ /setting ᴏʀ /setup - ᴄᴏɴғɪɢᴜʀᴇ ǫᴜɪᴢ sᴇᴛᴛɪɴɢs ɪɴ ɢʀᴏᴜᴘ
  ➤ /stop - sᴛᴏᴘ ᴏɴɢᴏɪɴɢ ǫᴜɪᴢ

ℹ️ Fᴏʀ ᴍᴏʀᴇ ᴅᴇᴛᴀɪʟꜱ, ᴠɪꜱɪᴛ [quizora.live](https://quizora.live) ꜰᴏʀ ᴛʜᴇ ꜰᴜʟʟ ᴅᴏᴄᴜᴍᴇɴᴛᴀᴛɪᴏɴ 📚!
"""
keyboard = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ɢʀᴏᴜᴘ", url=f"http://t.me/{BOT_USERNAME}?startgroup=s&admin=delete_messages+pin_messages+invite_users")],
        [InlineKeyboardButton("📣 ᴄʜᴀɴɴᴇʟ", url=Settings.Channel),
         InlineKeyboardButton("🔔 ᴜᴘᴅᴀᴛᴇꜱ", url=Settings.Update)],
    ]
)

@zenova.on_callback_query(filters.regex("hindi"))
async def hindi_callback(client: Client, callback_query):
    message = callback_query.message
    await message.edit("हिंदी में अनुवाद किया जा रहा है...")
    text = message.text
    translated_text = await translate_async(text, "hi")
    await message.edit(translated_text) 
    
async def send_solution(client: Client, _id: str, user_id: int):
    if _id.startswith('quiz_'):
        return
    if _id.startswith('govt_'):
        soln = await get_explaination_govt(_id.replace('govt_', ''))
        if not soln: soln = "😔 Sorry, no Explaination found for this question."
        k = InlineKeyboardMarkup([[InlineKeyboardButton("हिंदी में देखे", callback_data="hindi")]])
        return await client.send_message(user_id, soln, reply_markup=k)
    if _id.startswith('htent'):
        soln = await get_explaination_tenth(_id)
        if not soln: soln = "😔 Sorry, no Explaination found for this question."
        return await client.send_message(user_id, soln)
    vdo_url = await get_solution_video(_id, NO_SOLN) 
    if vdo_url: message = f"😊 Here is the video solution for the question: {vdo_url}"
    else: message = "😔 Sorry, no video solution found for this question." 
    await client.send_message(user_id, message, disable_web_page_preview=True)

@zenova.on_message(filters.command(["start"]) & filters.private, group=-5)
async def start(client: Client, message: Message):
    await add_served_user(message.from_user.id, client)
    if len(message.text.split()) > 1:
        u = message.text.split()[1]
        return await send_solution(
            client, u, 
            message.from_user.id
        )
    # get = await client.get_users(message.from_user.id)
    # name = get.first_name + (get.last_name if get.last_name else '')
    await message.reply(start_msg.format(BOT_NAME), reply_markup= keyboard)

@zenova.on_message(filters.command(["help"]) & filters.private, group=-5)
async def help_command(client: Client, message: Message):
#     help_text = """
# ʜᴇʏ! ʜᴇʀᴇ ᴀʀᴇ sᴏᴍᴇ ᴏꜰ ᴍʏ ᴄᴏᴍᴍᴀɴᴅꜱ:

#   ➤ /start - sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ.
#   ➤ /mstat - Vɪᴇᴡ ʏᴏᴜʀ Qᴜɪᴢ ᴘᴇʀғᴏʀᴍᴀɴᴄᴇ.
#   ➤ /gstat - Vɪᴇᴡ Qᴜɪᴢ sᴛᴀᴛs ꜰᴏʀ ᴛʜᴇ ɢʀᴏᴜᴘ.
#   ➤ /top - Sᴇᴇ ᴛʜᴇ ᴛᴏᴘ ɢʟᴏʙᴀʟ sᴄᴏʀᴇʀs.
#   ➤ /setting - Aᴄᴄᴇss Qᴜɪᴢ sᴇᴛᴛɪɴɢs ᴀɴᴅ ᴄᴏɴꜰɪɡᴜʀᴀᴛɪᴏns.
#   ➤ /help - Sʜᴏᴡ ᴛʜɪs ʜᴇʟᴘ ᴍᴇssᴀɢᴇ.

# ɪғ ʏᴏᴜ ʜᴀᴠᴇ ᴀɴʏ ᴏᴛʜᴇʀ ᴛʜɪɴɢs ʏᴏᴜ ᴡᴏᴜʟᴅ ʟɪᴋᴇ ᴛᴏ ᴋɴᴏᴡ, ᴠɪsɪᴛ sᴜᴘᴘᴏʀᴛ ᴄʜᴀɴɴᴇʟ!
#     """
    await message.reply(help_text, reply_markup= keyboard)

@zenova.on_message(filters.command(["start", "help"]) & filters.group & ~filters.chat(MSG_GROUP))
async def start_group(client: Client, message: Message):
    await add_served_chat(message.chat.id, client)
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("𝖮𝖯𝖤𝖭 𝖨𝖭 𝖣𝖬 💌", url=f"https://t.me/{BOT_USERNAME}")]]
    )
    await message.reply(
        f"ʜᴇʏ! ᴜꜱᴇ /setting ᴛᴏ ᴄᴏɴꜰɪɢᴜʀᴇ Qᴜɪᴢ ꜱᴇᴛᴛɪɴɢꜱ ꜰᴏʀ ᴛʜɪꜱ ɢʀᴏᴜᴘ. ꜰᴏʀ ᴍᴏʀᴇ ꜰᴇᴀᴛᴜʀᴇꜱ, ᴄʜᴇᴄᴋ ᴍᴇ ᴏᴜᴛ ɪɴ ᴅᴍ!",
        reply_markup=keyboard
    )

@zenova.on_message(filters.command(['setting', 'settings', 'setup']) & filters.private)
async def settings_private(client: Client, message: Message):
    settings_msg = (
        "ʜᴇʏ! ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜsᴇᴅ ɪɴ ɢʀᴏᴜᴘs ᴡʜᴇʀᴇ ɪ ᴀᴍ ᴘʀᴇsᴇɴᴛ. "
        "ᴘʟᴇᴀsᴇ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ."
        # "ɪғ ɴᴏ ɢʀᴏᴜᴘs ʏᴏᴜ ʜᴀᴠᴇ ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ 'ᴊᴏɪɴ ᴏғғɪᴄɪᴀʟ Qᴜɪᴢ ᴄʜᴀᴛs' ʙᴜᴛᴛᴏɴ."
    )
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ɢʀᴏᴜᴘ", url=f"http://t.me/{BOT_USERNAME}?startgroup=s&admin=delete_messages+pin_messages+invite_users")],
            # [InlineKeyboardButton("ᴊᴏɪɴ ᴏғғɪᴄɪᴀʟ Qᴜɪᴢ ᴄʜᴀᴛs", callback_data= 'join_quiz_chat')]
        ]
    )
    await message.reply(settings_msg, reply_markup=keyboard)

@zenova.on_callback_query(filters.regex("join_quiz_chat"))
async def join_quiz_chat(client: Client, callback_query):
    # Define the links to the official promoters chat groups
    chat_links = [
        "https://t.me/OfficialQuizGroup1",  # Replace with actual group link
        "https://t.me/OfficialQuizGroup2",  # Replace with actual group link
    ]
    inline_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Join Group 1", url=chat_links[0])],
        [InlineKeyboardButton("Join Group 2", url=chat_links[1])]
    ])
    message = (
        "Nᴏ ɢʀᴏᴜᴘꜱ? Nᴏ ᴡᴏʀʀʏ!! Jᴏɪɴ ᴏᴜʀ ᴏғғɪᴄɪᴀʟ Pʀᴏᴍᴏᴛᴇʀꜱ ɢʀᴏᴜᴘꜱ ᴛᴏ ɢᴇᴛ Qᴜɪᴢᴢᴇꜱ 24/7! ᴀɴᴅ ʜᴀᴠᴇ ꜰᴜɴ!"
    )
    await callback_query.message.edit(message, reply_markup=inline_keyboard, disable_web_page_preview=False)
