from pyrogram import Client, enums
from Modules import UserDB, LOG_GROUP

async def is_served_user(user_id: int) -> bool:
    user = await UserDB.find_one({"user_id": user_id})
    if not user:
        return False
    return True

async def get_served_users() -> list:
    users_list = []
    async for user in UserDB.find({"user_id": {"$gt": 0}}):
        users_list.append(user)
    return users_list

async def add_served_user(user_id: int, client: Client):
    is_served = await is_served_user(user_id)
    if is_served:
        return
    await UserDB.insert_one({"user_id": user_id})
    count = len(await get_served_users())
    try:
        user = await client.get_users(user_id)
        INFO = f'''
#NewUser

**Total users** = [{int(count) }]
**User id** = `{user_id}`
**Link** = {user.mention(enums.ParseMode.MARKDOWN)}
'''
        await client.send_message(LOG_GROUP, INFO)
    except:
        pass
    return 