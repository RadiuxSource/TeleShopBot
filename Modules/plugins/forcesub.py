from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import ChatAdminRequired, ChatWriteForbidden
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from Modules import zenova as app
from utils import get_invite_link
from config import Settings

channel_cache = {}

@app.on_message(filters.incoming & filters.private, group=-10)
async def must_join_channel(app: Client, msg: Message):
    if not Settings.MUST_JOIN:
        return
    try:
        user_has_joined_all = True
        links = []
        buttons = []
        for channel in Settings.MUST_JOIN:
            try:
                await app.get_chat_member(channel, msg.from_user.id)
            except UserNotParticipant:
                user_has_joined_all = False
                if channel not in channel_cache:
                    chat_info = await app.get_chat(channel)
                    link = await get_invite_link(channel, app)
                    channel_cache[channel] = {
                        'title': chat_info.title,
                        'link': link
                    }
                cached_info = channel_cache[channel]
                links.append(cached_info['link'])
                buttons.append([InlineKeyboardButton("๏ Join " + cached_info['title'][:10] + " ๏", url=cached_info['link'])])
        if not user_has_joined_all:
            try:
                await msg.reply_photo(
                    photo=Settings.ERROR_IMG,
                    caption=f"๏ ᴀᴄᴄᴏʀᴅɪɴɢ ᴛᴏ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ ʏᴏᴜ'ᴠᴇ ɴᴏᴛ ᴊᴏɪɴᴇᴅ ᴛʜᴇ fᴏʟʟᴏᴡɪɴɢ ᴄʜᴀɴɴᴇʟs ʏᴇᴛ, ɪғ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴜsᴇ ᴍᴇ ᴛʜᴇɴ ᴊᴏɪɴ ᴛʜᴇsᴇ ᴄʜᴀɴɴᴇʟs ᴀɴᴅ sᴛᴀʀᴛ ᴍᴇ ᴀɢᴀɪɴ!",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
                await msg.stop_propagation()
            except ChatWriteForbidden:
                pass
        else:
            return
    except ChatAdminRequired:
        print(f"๏ᴘʀᴏᴍᴏᴛᴇ ᴍᴇ ᴀs ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ ᴍᴜsᴛ_Jᴏɪɴ ᴄʜᴀᴛ ๏: {channel} !")
        return
    except Exception as e:
        print(f"❌{e}")