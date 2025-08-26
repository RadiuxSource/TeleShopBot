import time
from typing import Union
from pyrogram import Client, types

from Modules import ChatDB

async def get_served_chats() -> list:    
    chats = ChatDB.find({"chat_id": {"$lt": 0}})
    if not chats:
        return []
    chats_list = []
    for chat in await chats.to_list(length=1000000000):
        chats_list.append(chat)
    return chats_list


async def is_served_chat(chat_id: int) -> bool:
    chat = await ChatDB.find_one({"chat_id": chat_id})
    if not chat:
        return False
    return True


async def add_served_chat(chat_id: int, client: Client, add_by: Union[types.User, None] = None):
    is_served = await is_served_chat(chat_id)
    if is_served:
        return
    await ChatDB.insert_one({"chat_id": chat_id})
    

async def remove_served_chat(chat_id: int):
    is_served = await is_served_chat(chat_id)
    if not is_served:
        return
    return await ChatDB.delete_one({"chat_id": chat_id})
