from Modules import zenova
from config import Settings
from pyrogram import Client, filters
from pyrogram.types import Message


@zenova.on_message(filters.group & filters.chat(Settings.SPAM_GROUP))
async def delete_spammers_message(client: Client, message: Message):
    filter_users = Settings.spammers
    if message.from_user.id in filter_users:
        await message.delete()