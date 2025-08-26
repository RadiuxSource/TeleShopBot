import time
from typing import Union
from pyrogram import Client, types

from Modules import ChatDB, LOG_GROUP, support_ikm
from utils import get_invite_link, check_chat
from Types import Exam
from database.quiz import QuizGroupManager

Qzr = QuizGroupManager()
auto_delete_cache = {}
exam_cache = {}
lang_cache = {}

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
    s = await check_chat(chat_id, client)
    if s:
        await client.send_message(chat_id, s, reply_markup=support_ikm)
        return
    await Qzr.add_quiz_group(chat_id)
    await set_auto_delete(chat_id, True)
    count = len(await get_served_chats())
    try:
        chat = await client.get_chat(chat_id)
        LINK = await get_invite_link(chat_id, client)
        INFO = f'''
#NewChat

**Total chats** = [{int(count)}]
**Chat Name** = {chat.title} 
**Chat ID** = `{chat.id}`
**Link** = {LINK}
'''
        try:
            if add_by:
                INFO += f"""
**Added By ID** = `{add_by.id}`
**Added By** = {add_by.mention}"""
        except: pass
        await client.send_message(LOG_GROUP, INFO)
    except Exception as e:
        print(e)
        pass
    return 

async def remove_served_chat(chat_id: int):
    is_served = await is_served_chat(chat_id)
    if not is_served:
        return
    return await ChatDB.delete_one({"chat_id": chat_id})


#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#
#-----------------------------[Setup.py]-------------------------------------#
#____________________________________________________________________________#

async def get_current_question_level(chat_id: int) -> str:
    chat = await ChatDB.find_one({"chat_id": chat_id})
    if not chat:
        return 4
    return chat.get('question_level', 4)

async def set_question_level(chat_id: int, level: int):
    await ChatDB.update_one(
        {"chat_id": chat_id},
        {"$set": {"question_level": level}},
        upsert=True
    )


async def is_auto_delete_enabled(chat_id: int) -> bool:
    if chat_id in auto_delete_cache:
        return auto_delete_cache[chat_id]
    chat = await ChatDB.find_one({"chat_id": chat_id})
    auto_delete_enabled = chat.get('auto_delete_enabled', False) if chat else False
    auto_delete_cache[chat_id] = auto_delete_enabled
    return auto_delete_enabled

async def set_auto_delete(chat_id: int, status: bool):
    await ChatDB.update_one(
        {"chat_id": chat_id},
        {"$set": {"auto_delete_enabled": status}},
        upsert=True
    )
    auto_delete_cache[chat_id] = status


async def get_lang(chat_id: int) -> str:
    if chat_id in lang_cache:
        return lang_cache[chat_id]
    chat = await ChatDB.find_one({"chat_id": chat_id})
    lang = chat.get('lang', "en") if chat else "en"
    lang_cache[chat_id] = lang
    return lang

async def set_lang(chat_id: int, lang: str):
    await ChatDB.update_one(
        {"chat_id": chat_id},
        {"$set": {"lang": lang}},
        upsert=True
    )
    lang_cache[chat_id] = lang


async def set_exam(chat_id: int, exam: str):
    await ChatDB.update_one(
        {"chat_id": chat_id},
        {"$set": {"exam": exam}},
        upsert=True
    )
    exam_cache.pop(chat_id, None)

async def get_exam(chat_id: int) -> str:
    if chat_id in exam_cache:
        return exam_cache[chat_id]
    chat = await ChatDB.find_one({"chat_id": chat_id})
    exam = chat.get('exam', Exam.JEE) if chat else Exam.JEE
    if exam == 'jee-neet':
        exam = Exam.JEE
        await ChatDB.update_one(
            {"chat_id": chat_id},
            {"$set": {"exam": Exam.JEE}})
    exam_cache[chat_id] = exam
    return exam

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#===============================[ Quiz.py ]==================================#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

async def add_quiz(chat_id: int, quiz_id: str, msg_id_of_quiz: list, correct_opt: int, exam_type: str):
    """ Add a quiz in the database for a specific chat. """
    new_quiz = {
        "chat_id": chat_id,
        "quiz_id": quiz_id,
        "msg_id": msg_id_of_quiz,
        "correct_opt": correct_opt,
        "time": time.time(),
        "exam_type": exam_type
    }
    result = await ChatDB.update_one(
        {"chat_id": chat_id},  
        {"$push": {"quizzes": new_quiz}},  
        upsert=True
    )
    return result.modified_count, result.upserted_id


async def get_quiz(chat_id: int = None, quiz_id: str = None) -> Union[list, dict, None]:
    """ 
    Retrieve quiz data based on chat_id or quiz_id.
    
    If only chat_id is provided, return all quizzes for that chat.
    If only quiz_id is provided, search for that quiz across all chats.
    """
    await delete_quiz(chat_id)  # Clean the quiz list first
    if chat_id:
        quiz_data = await ChatDB.find_one({"chat_id": chat_id})
        return quiz_data.get('quizzes', []) if quiz_data else []
    elif quiz_id:
        all_chats = await ChatDB.find({}).to_list(length=None)
        for chat in all_chats:
            for quiz in chat.get('quizzes', []):
                if quiz['quiz_id'] == quiz_id:
                    return quiz
    return None  


async def delete_quiz(chat_id: int, quiz_id: str = None):
    """
    Delete a specific quiz or all quizzes older than 24 hours from the database for a specific chat.
    """
    if quiz_id:
        result = await ChatDB.update_one(
            {"chat_id": chat_id},
            {"$pull": {"quizzes": {"quiz_id": quiz_id}}}  
        )
        return result.modified_count
    else:
        twenty_four_hours_ago = time.time() - 24 * 60 * 60
        result = await ChatDB.update_one(
            {"chat_id": chat_id},
            {"$pull": {"quizzes": {"time": {"$lt": twenty_four_hours_ago}}}}  
        )
        return result.modified_count



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#===============================[ stats.py ]=================================#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

async def update_chat_stats(chat_id: int, user_id: int = None, inc_tp: bool = False, inc_tp2: bool = False, 
                            govt: bool = False, tenth: bool = False, neet: bool = False,
                            add_up: bool = False, set_lpt: bool = False):
    """
    Update chat statistics in the database.

    Param:
    - chat_id (int): Telegram chat ID
    - user_id (int): Telegram user ID
    - inc_tp (bool): Increment total_polls by 1
    - inc_tp2 (bool): Increment total_participants by 1
    - govt (bool): Is group configured with GOVT exam type
    - tenth (bool): Is group configured with Tenth exam type
    - neet (bool): Is group configured with NEET exam type
    - add_up (bool): Add user_id to unique_participants set
    - set_lpt (bool): Set last_poll_time to current time

    Returns:
    - None
    """
    update = {}
    if inc_tp: update["$inc"] = {"total_polls": 1}
    if inc_tp2: update["$inc"] = update.get("$inc", {}) | {"total_participants": 1}
    if add_up: update["$addToSet"] = {"unique_participants": user_id}
    if set_lpt: update["$set"] = {"last_poll_time": time.time()}
    await ChatDB.update_one({"chat_id": chat_id}, update, upsert=True)
    # Update global stats
    update = {}
    if inc_tp: update["$inc"] = {"total_polls": 1}
    if inc_tp2: update["$inc"] = update.get("$inc", {}) | {"total_participants": 1}
    if add_up: update["$addToSet"] = {"unique_participants": user_id}
    if govt: update["$inc"] = {"govt_total_polls": 1}
    if tenth: update["$inc"] = {"tenth_total_polls": 1}
    if neet: update["$inc"] = {"neet_total_polls": 1}
    await ChatDB.update_one({"chat_id": "global_stats"}, update, upsert=True)

async def get_chat_stats(chat_id: int):
    return await ChatDB.find_one({"chat_id": chat_id})

async def get_global_stats():
    return await ChatDB.find_one({"chat_id": "global_stats"})
