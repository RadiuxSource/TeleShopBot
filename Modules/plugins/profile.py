from datetime import datetime
from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from Modules import zenova
from Types import Exam
from database import get_user_stats, set_preferred_exam

def format_unix_time(timestamp):
    try:
        return datetime.fromtimestamp(timestamp).strftime('%d %b %Y, %I:%M %p')
    except:
        return "N/A"

def generate_profile_message(user_data: dict, preferred_exam: str = None) -> tuple[str, list]:
    user_id = user_data.get("user_id")
    exams = [k for k in Exam.exam_names if k in user_data]
    lines = [
        "🧑‍💻 **Your Profile**",
        f"🆔 ID: `{user_id}`",
        ""
    ]
    for exam in exams:
        data = user_data.get(exam, {})
        score = data.get("score", 0)
        attempts = data.get("total_attempts", 0)
        last_time = format_unix_time(data.get("last_attempt_time", 0))
        lines.extend([
            f"📚 **{Exam.get_exam_name(exam)}**",
            f"   🔸 Score: `{score}`",
            f"   🔸 Attempts: `{attempts}`",
            f"   🔸 Last Attempt: `{last_time}`",
            ""
        ])
    if preferred_exam:
        lines.append(f"🎯 **Preferred Exam:** `{Exam.get_exam_name(preferred_exam)}`")
        lines.append("")
    lines.append("👇 Select or update your preferred exam:")
    message = "\n".join(lines)
    return message

@zenova.on_message(filters.command("profile") & filters.private)
async def profile(client: Client, message: Message):
    user_id = message.from_user.id
    user_data = await get_user_stats(user_id, raw=True)
    if not user_data:
        return await message.reply_text("You don't have any exam data yet.")
    preferred_exam = user_data.get("preferred_exam", 'N/A')
    message_text = generate_profile_message(user_data, preferred_exam)
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Reset Preferred Exam", callback_data="reset_exam")]])
    await message.reply_text(message_text, reply_markup=reply_markup)

@zenova.on_callback_query(filters.regex(r'^reset_exam$'))
async def reset_exam_callback(client, callback_query: CallbackQuery):
    ikb = []
    # Dynamically create buttons for each exam
    for exam in Exam.exam_names:
        exam_name = Exam.get_exam_name(exam)
        button = InlineKeyboardButton(exam_name, callback_data=f'set_preferred_exam_{exam}')
        ikb.append([button])
    reply_markup = InlineKeyboardMarkup(ikb)
    await callback_query.message.edit_reply_markup(reply_markup)

@zenova.on_callback_query(filters.regex(r'^set_preferred_exam_(.+)$'))
async def set_preferred_exam_callback(client, callback_query: CallbackQuery):
    exam = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id
    await set_preferred_exam(user_id, exam)
    user_data = await get_user_stats(user_id, raw=True)
    message_text = generate_profile_message(user_data, exam)
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Reset Preferred Exam", callback_data="reset_exam")]])
    await callback_query.message.edit_text(message_text, reply_markup=reply_markup)
    await callback_query.answer(f"Preferred exam set to {Exam.get_exam_name(exam)}")