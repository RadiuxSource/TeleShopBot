from utils import paste
from database import QzMgr
from Modules import zenova, LOG_GROUP
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import ChannelPrivate, TopicClosed, ChatSendPhotosForbidden

IGNORED_EXCEPTIONS = (ChannelPrivate, TopicClosed)
async def report_error(e, chat_id = None, user_id = None, Traceback: str = None):    
    if await mng_known_errors(e, chat_id):
        return
    if isinstance(e, IGNORED_EXCEPTIONS):
        return
    error = "**Unknown Error occured:**"
    error += f"\n\n```py\n{e}```"
    if chat_id: error += f"\n\n**Chat:** `{chat_id}`"
    if user_id: error += f"\n**User:** `{user_id}`"
    if Traceback:
        link = await paste(Traceback)
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Traceback", url=link)]])
        await zenova.send_message(LOG_GROUP, error, reply_markup=keyboard, disable_web_page_preview=True)
    else:
        await zenova.send_message(LOG_GROUP, error, disable_web_page_preview=True)


async def mng_known_errors(e, chat_id = None):
    try:
        if isinstance(e, (ChannelPrivate, TopicClosed)):
            await QzMgr.remove_quiz_group(chat_id)
            return True
        if isinstance(e, ChatSendPhotosForbidden):
            await QzMgr.remove_quiz_group(chat_id)
            await zenova.send_message(chat_id, "**I’m unable to send photos of questions in this chat. Could you please grant me permission to share images? That would really help! 😊 You can turn the quiz feature back on after adjusting the permissions. Thank you! 🙌**", parse_mode=ParseMode.MARKDOWN)
            return True
    except:
        return False
    return False