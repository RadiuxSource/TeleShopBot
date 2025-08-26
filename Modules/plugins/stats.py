import traceback
from typing import Dict
from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from Modules import zenova, BOT_USERNAME, CORRECT_ANS, WRONG_ANS
from Types import Exam
from database.userStats import  (get_user_stats, get_global_rank, get_preferred_exam, 
        set_preferred_exam, get_highest_scorer_in_chat, get_global_top_scorers, get_top_global_users)
from database.chats import get_chat_stats, get_global_stats, get_exam

async def get_user_exam(stats: dict, user_id: int = None):
    exam_type = await get_preferred_exam(user_id)
    if exam_type:
        return exam_type
    jee_attempts = stats[Exam.JEE]["total_attempts"]
    govt_attempts = stats[Exam.GOVT_EXAM]["total_attempts"]
    if jee_attempts >= govt_attempts:
        exam_type = Exam.JEE
    else:
        exam_type = Exam.GOVT_EXAM
    await set_preferred_exam(user_id, exam_type)
    return exam_type

async def get_user_quiz_stats(user_id: int):
    user_stats = await get_user_stats(user_id)
    exam_type = await get_user_exam(user_stats, user_id)
    exam_data = user_stats[exam_type]
    global_rank = await get_global_rank(user_id, exam_type=exam_type)
    user = await zenova.get_users(user_id)
    name = user.first_name + (" " + user.last_name if user.last_name else "")
    stats_message = f"""
📊 **𝖴𝖲𝖤𝖱 𝖰𝖴𝖨𝖹 𝖯𝖮𝖫𝖫 𝖯𝖤𝖱𝖥𝖮𝖱𝖬𝖠𝖭𝖢𝖤**
━━━━━━━━━━━━━━━━
**Name:** {name}
**Exam Type:** {Exam.get_exam_name(exam_type)}
**Total Quiz Polls Attempted:** {exam_data.get('total_attempts', 0)}
**Total Points:** {exam_data.get('score', 0)}

**Global Rank:** #{global_rank}
**Scoring System:** +{CORRECT_ANS} points for each correct answer, {WRONG_ANS} points for each wrong answer.

**Preferred Exam:** Use /profile to change your Preferred Exam.
━━━━━━━━━━━━━━━━
"""
    return stats_message

@zenova.on_message(filters.command(['mstats', 'mstat']), group=1)
async def my_stats_command(client, message:Message):
    try: 
        if message.chat.type != enums.ChatType.PRIVATE:
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('Open Bot ↗️', url=f"https://t.me/{BOT_USERNAME}")]])
            return await message.reply_text('This command can be used only private mode.', reply_markup=keyboard)
        user_id = message.from_user.id
        wait_message = await message.reply('🫸Fetching...')
        stats_message = await get_user_quiz_stats(user_id)
        await wait_message.edit_text(stats_message)
    except Exception as e:
        traceback.print_exc()
        await message.reply(f'Error: {e}')

async def get_quiz_stats(chat_id: int):
    global_stats = await get_global_stats()
    chat_stats = await get_chat_stats(chat_id)
    exam_type = await get_exam(chat_id) 
    exam_type_ = Exam.get_exam_name(exam_type)
    global_top_scorers = await get_global_top_scorers(limit=3, exam_type=exam_type)
    highest_scorer_id, highest_score = await get_highest_scorer_in_chat(chat_id, exam_type, limit=1)
    chat = await zenova.get_chat(chat_id)
    group_name = chat.title
    stats_message = f"""
📊 **𝖦𝗅𝗈𝖻𝖺𝗅 & 𝖦𝗋𝗈𝗎𝗉 𝖰𝗎𝗂𝗓 𝖯𝗈𝗅𝗅 𝖲𝗍𝖺𝗍𝗂𝗌𝗍𝗂𝖼𝗌**
━━━━━━━━━━━━━━━━
**Global Statistics:**
• Total Quiz Polls Sent: {global_stats['total_polls']}
• Total Participants: {global_stats['total_participants']}
• Top Global Participants:
"""
    for i, scorer in enumerate(global_top_scorers, 1):
        user = await zenova.get_users(scorer['user_id'])
        stats_message += f"\n   {i}. {user.mention}: {scorer.get(exam_type, {}).get('score', 0)} points"    
    highest_scorer = await zenova.get_users(highest_scorer_id) if highest_scorer_id else None
    stats_message += f"""
━━━━━━━━━━━━━━━━
**Group Statistics for {group_name}:**
• Exam type: {exam_type_}
• Total Quiz Polls Sent: {chat_stats.get('total_polls', 0)}
• Total Participants: {chat_stats.get('total_participants', 0)}
• Highest Scorer in Group: {highest_scorer.mention if highest_scorer else "N/A"} with {highest_score} points
• Total Unique Participants in Group: {len(chat_stats.get('unique_participants', []))}
━━━━━━━━━━━━━━━━
"""
    return stats_message


@zenova.on_message(filters.command(['gstats', 'gstat']), group=1)
async def group_stats_command(client, message):
    try:
        if message.chat.type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('Add me to group ➕', url=f"https://t.me/{BOT_USERNAME}?startgroup=true")]])
            return await message.reply_text('This command can be used only in groups.', reply_markup=keyboard)
        chat_id = message.chat.id
        wait_message = await message.reply('🫸Fetching...')
        stats_message = await get_quiz_stats(chat_id)
        await wait_message.edit_text(stats_message)
    except Exception as e:
        traceback.print_exc()
        await message.reply(f'Error: {e}')

#if nothing is cached, fetching will  be sent
top_cached: Dict[str, str] = {exam: '🫸Fetching...' for exam in Exam.exam_names}
@zenova.on_message(filters.command("top"), group=1)
async def top_scorers_command(client, message: Message):
    try:
        wait_message = await message.reply('🫸Fetching...')
        if message.chat.type in [enums.ChatType.SUPERGROUP, enums.ChatType.GROUP]:
            exam_type = await get_exam(message.chat.id)
        else:
            u_stats = await get_user_stats(message.from_user.id)
            exam_type = await get_user_exam(u_stats, user_id=message.from_user.id)
        await wait_message.edit_text(f'Refreshing...\n\n{top_cached[exam_type]}')
        top_scorers = await get_top_global_users(limit=10, exam_type=exam_type)
        txt = Exam.get_exam_name(exam_type)
        response = f"🏆 **Top Scorers in {txt}**\n\n"
        for i, scorer in enumerate(top_scorers, 1):
            if not scorer[0]:
                continue
            user = await zenova.get_users(int(scorer[0]))
            response += f"{i}. {user.mention}: {scorer[1]} points\n"
        top_cached[exam_type] = response
        await wait_message.edit_text(response)
    except Exception as e:
        traceback.print_exc()
        await message.reply(f'Error: {e}')
