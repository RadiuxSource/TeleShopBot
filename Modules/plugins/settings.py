import asyncio
from Modules import zenova, BOT_ID

from pyrogram import filters
from pyrogram.types import (Message, ChatMemberUpdated, 
    CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup)

from database import (QzMgr, set_auto_delete,
    get_current_question_level, add_served_chat,
    set_question_level, is_auto_delete_enabled, 
    set_lang, get_lang, set_exam, get_exam)
from utils import (is_admin, get_level_text, 
    check_chat, generate_config_message, Language)
from Types import Exam


# Group Management Functions
@zenova.on_chat_member_updated(filters.group)
async def handle_group_member_update(client, chat_member_updated: ChatMemberUpdated):
    try:
        user_id = chat_member_updated.new_chat_member.user.id
        if user_id == BOT_ID:
            chat_id = chat_member_updated.chat.id
            await asyncio.sleep(2)
            await add_served_chat(chat_id, client, chat_member_updated.from_user)
            await send_settings(client, chat_id)
    except: pass


@zenova.on_message(filters.command(['quiz', 'setting', 'settings', 'setup']) & filters.group)
async def quiz_mode(client, message: Message):
    chat_id = message.chat.id
    await send_settings(client, chat_id)
    await add_served_chat(chat_id, client)


async def send_settings(client, chat_id):
    quiz_status = '⚡ On' if await QzMgr.is_quiz_group(chat_id) else '🚫 Off'
    question_level = await get_level_text(await get_current_question_level(chat_id))
    auto_delete_status = '⚡ On' if await is_auto_delete_enabled(chat_id) else '🚫 Off'
    lang_ = await get_lang(chat_id)
    lang = Language.get_language_name(lang_)
    exam_ = await get_exam(chat_id)
    exam = Exam.get_exam_name(exam_)
    reply_markup = InlineKeyboardMarkup([
        [    
            InlineKeyboardButton(f"🎯 Quiz", callback_data='toggle_quiz')
        ],
        [    
            InlineKeyboardButton("📊 Question Level", callback_data='set_question_level'),
            InlineKeyboardButton(f"⏱️ Auto-Delete", callback_data='change_auto_delete')
        ],
        [
            InlineKeyboardButton("🧑‍🔬 Exam", callback_data='change_stream'),
            InlineKeyboardButton("🌏 Language", callback_data='change_lang'),
        ]])
    await client.send_message(
        chat_id,
        await generate_config_message(quiz_status, question_level, lang, exam, auto_delete_status),
        reply_markup=reply_markup)


async def validate_admin(client, callback_query):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    if not await is_admin(client, user_id, chat_id):
        await callback_query.answer("🚫 You don't have permission to change settings.", show_alert=True)
        return False
    return True


# Back Callback Query Handlers
@zenova.on_callback_query(filters.regex(r'back'))
async def handle_callback_query(client, callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    if not await validate_admin(client, callback_query):
        return
    await update_config_message(callback_query, chat_id)


# Quiz Management Functions
@zenova.on_callback_query(filters.regex(r'toggle_quiz'))
async def toggle_quiz_menu(client, callback_query: CallbackQuery):
    if not await validate_admin(client, callback_query):
        return
    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✔️ Enable Quizzes", callback_data='enable_quiz'),
            InlineKeyboardButton("✖️ Disable Quizzes", callback_data='disable_quiz'),
        ],
        [InlineKeyboardButton("🔙 Back", callback_data='back'),]
    ])
    await callback_query.message.edit_text("💡 **Quiz Mode Settings**", reply_markup=reply_markup)


@zenova.on_callback_query(filters.regex(r'set_question_level'))
async def set_question_level_menu(client, callback_query: CallbackQuery):
    if not await validate_admin(client, callback_query):
        return
    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Easy", callback_data='set_level_1'),
            InlineKeyboardButton("Medium", callback_data='set_level_2'),
        ],
        [
            InlineKeyboardButton("Hard", callback_data='set_level_3'),
            InlineKeyboardButton("Mixed", callback_data='set_level_4'),
        ],
        [InlineKeyboardButton("🔙 Back", callback_data='back'),]
    ])
    await callback_query.message.edit_text("💡 **Question Level Settings**", reply_markup=reply_markup)


@zenova.on_callback_query(filters.regex(r'set_level_'))
async def set_question_level_handler(client, callback_query: CallbackQuery):
    if not await validate_admin(client, callback_query):
        return
    level = int(callback_query.data.split('_')[2])
    await set_question_level(callback_query.message.chat.id, level)
    await update_config_message(callback_query, callback_query.message.chat.id)


@zenova.on_callback_query(filters.regex(r'change_auto_delete'))
async def toggle_auto_delete_menu(client, callback_query: CallbackQuery):
    if not await validate_admin(client, callback_query):
        return
    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✔️ Enable Auto-Delete", callback_data='enable_auto_delete'),
            InlineKeyboardButton("✖️ Disable Auto-Delete", callback_data='disable_auto_delete'),
        ],
        [InlineKeyboardButton("🔙 Back", callback_data='back'),]
    ])
    await callback_query.message.edit_text("💡 **Auto-Delete Settings**", reply_markup=reply_markup)


@zenova.on_callback_query(filters.regex(r'enable_auto_delete'))
async def enable_autodl(client, callback_query: CallbackQuery):
    if not await validate_admin(client, callback_query):
        return
    chat_id = callback_query.message.chat.id
    await set_auto_delete(chat_id, True)
    await update_config_message(callback_query, chat_id)
 

@zenova.on_callback_query(filters.regex(r'disable_auto_delete'))
async def disable_autodl(client, callback_query: CallbackQuery):
    if not await validate_admin(client, callback_query):
        return
    chat_id = callback_query.message.chat.id
    await set_auto_delete(chat_id, False)
    await update_config_message(callback_query, chat_id)


@zenova.on_callback_query(filters.regex(r'enable_quiz'))
async def enable_quiz(client, callback_query: CallbackQuery):
    if not await validate_admin(client, callback_query):
        return
    chat_id = callback_query.message.chat.id
    s = await check_chat(chat_id, zenova)
    if s:
        await callback_query.answer(s, show_alert=True)
        return
    await QzMgr.add_quiz_group(chat_id)
    await update_config_message(callback_query, chat_id)


@zenova.on_callback_query(filters.regex(r'disable_quiz'))
async def disable_quiz(client, callback_query: CallbackQuery):
    if not await validate_admin(client, callback_query):
        return
    chat_id = callback_query.message.chat.id
    await QzMgr.remove_quiz_group(chat_id)
    await update_config_message(callback_query, chat_id)


async def update_config_message(callback_query, chat_id):
    quiz_status = '⚡ On' if await QzMgr.is_quiz_group(chat_id) else '🚫 Off'
    question_level = await get_level_text(await get_current_question_level(chat_id))
    auto_delete_status = '⚡ On' if await is_auto_delete_enabled(chat_id) else '🚫 Off'
    lang_ = await get_lang(chat_id)
    lang = Language.get_language_name(lang_)
    exam_ = await get_exam(chat_id)
    exam = Exam.get_exam_name(exam_)
    reply_markup = InlineKeyboardMarkup([
        [    
            InlineKeyboardButton(f"🎯 Quiz", callback_data='toggle_quiz')
        ],
        [    
            InlineKeyboardButton("📊 Question Level", callback_data='set_question_level'),
            InlineKeyboardButton(f"⏱️ Auto-Delete", callback_data='change_auto_delete')
        ],
        [
            InlineKeyboardButton("🧑‍🔬 Exam", callback_data='change_stream'),
            InlineKeyboardButton("🌏 Language", callback_data='change_lang'),
        ]])
    await callback_query.message.edit_text(await generate_config_message(quiz_status, question_level, lang, exam, auto_delete_status), reply_markup=reply_markup)


# Change Language/Stream 
@zenova.on_callback_query(filters.regex(r'change_lang'))
async def change_language(client, callback_query: CallbackQuery):
    chat_id= callback_query.message.chat.id
    ikb = []
    # Dynamically create buttons for each language
    for lang_code, lang_name in Language.LANGUAGES.items():
        button = InlineKeyboardButton(lang_name, callback_data=f'set_lang_{lang_code}')
        ikb.append([button])  
    back_button = InlineKeyboardButton("🔙 Back", callback_data='back')
    ikb.append([back_button]) 
    reply_markup = InlineKeyboardMarkup(ikb)
    await callback_query.message.edit_text("💡 **Language Settings**\n\n**Note:** Language is for quiz question(specifically for 🏛️ Government Exam 🏛️ polls) only.", reply_markup=reply_markup)


@zenova.on_callback_query(filters.regex(r'change_stream'))
async def change_exam(client, callback_query: CallbackQuery):
    chat_id= callback_query.message.chat.id
    ikb = []
    # Dynamically create buttons for each exam
    for exam_raw, exam_name in Exam.exam_names.items():
        button = InlineKeyboardButton(exam_name, callback_data=f'set_exam_{exam_raw}')
        ikb.append([button])
    back_button = InlineKeyboardButton("🔙 Back", callback_data='back')
    ikb.append([back_button])  
    reply_markup = InlineKeyboardMarkup(ikb)
    await callback_query.message.edit_text("💡 **Exam Stream Settings**\n\nWe are coming soon with many exams like 10th Boards, NEET Seprate and other exams questions. 🙌", reply_markup=reply_markup)


@zenova.on_callback_query(filters.regex(r'set_lang_'))
async def set_language_handler(client, callback_query: CallbackQuery):
    if not await validate_admin(client, callback_query):
        return
    lang = callback_query.data.split('_')[2]
    await set_lang(callback_query.message.chat.id, lang)
    await update_config_message(callback_query, callback_query.message.chat.id)


@zenova.on_callback_query(filters.regex(r'set_exam_'))
async def set_exam_handler(client, callback_query: CallbackQuery):
    if not await validate_admin(client, callback_query):
        return
    exam = callback_query.data.split('_')[2]
    await set_exam(callback_query.message.chat.id, exam)
    await update_config_message(callback_query, callback_query.message.chat.id)