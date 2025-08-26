from pyrogram import filters
from pyrogram import Client
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, PeerIdInvalid
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
import asyncio
import datetime, time

from Modules import zenova, SUDO_USERS
from database import get_served_chats, get_served_users

broadcasting_in_progress = False
failed_users = []
preview_mode = False

async def get_failed_users():
    global failed_users
    return failed_users

@zenova.on_message(filters.command(["bcast", "gcast"]) & filters.user(SUDO_USERS))
async def broadcast_handler(client, message: Message):
    global preview_mode
    global broadcasting_in_progress
    if broadcasting_in_progress: 
        stop_button = InlineKeyboardButton("Stop Broadcasting", callback_data="stop_broadcast")
        stop_markup = InlineKeyboardMarkup([[stop_button]])
        await message.reply_text("Another broadcast is already in process...", reply_markup= stop_markup)
        return
    cmd = message.command[0]
    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Preview Mode On", callback_data=f'preview_on_{cmd}'),
            InlineKeyboardButton("Preview Mode Off", callback_data=f'preview_off_{cmd}'),
        ]
    ])
    await message.reply_text(f'Preview mode: {preview_mode}\n\nPlease choose the forward tag preview mode:', reply_markup=reply_markup)


@zenova.on_callback_query(filters.regex(r'^preview_(on|off)_(bcast|gcast)$'))
async def preview_handler(client: Client, query: CallbackQuery):
    if not query.from_user.id in SUDO_USERS: 
        await query.answer("Not for you dude🥹", show_alert= True)
        return
    global preview_mode
    cmd = query.data.split("_")[2]
    if query.data.startswith('preview_on'):
        preview_mode = True
    else:
        preview_mode = False
    await query.message.edit_text(text="Enter the broadcast message:")
    try:
        newsletter_msg: Message = await client.wait_for_message(query.from_user.id, timeout= 120)
    except (asyncio.exceptions.TimeoutError, TimeoutError):
        await query.message.edit_text("No message received, Timeout!!")
        return
    if newsletter_msg:
        if preview_mode:
            await newsletter_msg.forward(chat_id=int(query.from_user.id))
        else:
            await newsletter_msg.copy(chat_id=int(query.from_user.id))
        await zenova.send_message(query.from_user.id, text="Do you want to broadcast this message to all your users? (y/n)")
        try:
            confirmation = await client.wait_for_message(query.from_user.id, timeout= 120)
        except (asyncio.exceptions.TimeoutError, TimeoutError):
            await query.message.reply("No confirmation received, Timeout!!")
            return
        confirmation_text = confirmation.text.lower()
        if confirmation_text == 'n':
            await zenova.send_message(query.from_user.id, text="Broadcast cancelled by admin.")
            return 
        elif confirmation_text != 'y':
            await zenova.send_message(query.from_user.id, text="Invalid response. Please enter y or n.")
            return 
        
        global broadcasting_in_progress
        broadcasting_in_progress = True
        if cmd == "bcast":
            chats = await get_served_users()
        else:
            chats = await get_served_chats()
        stop_broadcast_button = InlineKeyboardButton("Stop Broadcasting", callback_data="stop_broadcast")
        stop_broadcast_markup = InlineKeyboardMarkup([[stop_broadcast_button]])
        sts_msg = await zenova.send_message(query.from_user.id, text="Starting process of Broadcast...", reply_markup=stop_broadcast_markup)
        done = 0
        failed = 0
        success = 0
        start_time = time.time()
        total_users = len(chats)
        for chat in chats:
            if broadcasting_in_progress:
                try:
                    chat_id = chat['user_id'] 
                except:   
                    chat_id = chat['chat_id']
                sts = await send_newsletter(chat_id, newsletter_msg)
                if sts == 200:
                    success += 1
                else:
                    failed += 1
                done += 1
                if not done % 20:
                    await sts_msg.edit(
                        text=f"📣 Sending newsletter... 📱\n\nTotal chats: {total_users} 👥\nCompleted: {done} / {total_users} 📊\nSuccess: {success} ✅\nFailed: {failed} ❌"
                    )
            else:
                break

        if broadcasting_in_progress:
            completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
            await zenova.send_message(query.from_user.id,
                text=f"🎉 Newsletter sent successfully! 📨\nCompleted in {completed_in} ⏰\nTotal chats: {total_users} 👥\nCompleted: {done} / {total_users} 📊\nSuccess: {success} ✅\nFailed: {failed} ❌"
            )
        else:
            await zenova.send_message(query.from_user.id, text="Broadcasting stopped by admin.")    
    broadcasting_in_progress = False

@zenova.on_callback_query(filters.regex(r'^stop_broadcast$'))
async def stop_broadcasting_handler(_, query):
    if not query.from_user.id in SUDO_USERS: 
        await query.answer("Not for you dude🥹", show_alert= True)
        return
    global broadcasting_in_progress
    broadcasting_in_progress = False
    await query.message.edit_text(text="Broadcasting stopped.")

async def send_newsletter(chat_id, message):
    global preview_mode
    try:
        if preview_mode:
            await message.forward(chat_id=int(chat_id))
        else:
            await message.copy(chat_id=int(chat_id))
        return 200
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return send_newsletter(chat_id, message)
    except InputUserDeactivated:
        print(f"{chat_id} : Deactivated")
        failed_users.append(chat_id)
        return 400
    except UserIsBlocked:
        print(f"{chat_id} : Blocked")
        failed_users.append(chat_id)
        return 400
    except PeerIdInvalid:
        print(f"{chat_id} : Invalid ID")
        failed_users.append(chat_id)
        return 400
    except Exception as e:
        print(f"{chat_id} : {e}")
        failed_users.append(chat_id)
        return 500