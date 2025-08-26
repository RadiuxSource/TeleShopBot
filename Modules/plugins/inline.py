from pyrogram import Client
from pyrogram import filters, enums
from pyrogram.types import (InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardMarkup as IKM, InlineKeyboardButton as IKB, InlineQuery)

import re
from Modules import zenova, BOT_USERNAME
from Types import Exam
from Modules.plugins.stats import get_user_quiz_stats
from database.userStats import  (get_user_stats, get_global_rank,
        get_highest_scorer_in_chat, get_global_top_scorers, get_top_global_users)
from database.chats import get_chat_stats, get_global_stats, get_exam

# @zenova.on_inline_query()
async def inline_stats(client: Client, query: InlineQuery):
    if query.query.casefold() == 'mstat':
        user_id = query.from_user.id
        try:
            stats_message = await get_user_quiz_stats(user_id)
            keyboard = IKM([[IKB("Open Bot↖️", url=f"https://t.me/{BOT_USERNAME}")]])
            result = InlineQueryResultArticle(
                title="Your Quiz Stats",
                description="Tap to View your quiz performance",
                input_message_content=InputTextMessageContent(stats_message, disable_web_page_preview=True),
                reply_markup=keyboard
            )
            await query.answer([result], cache_time=0)
        except Exception as e:
            error_result = InlineQueryResultArticle(
                title='Error fetching stats',
                description='Their was an error retrieving your quiz stats.',
                input_message_content=InputTextMessageContent(f"Error: {e}")
            )
            await query.answer([error_result], cache_time=0)