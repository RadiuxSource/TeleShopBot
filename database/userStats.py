import time
from . import get_chat_stats, get_global_stats
from Modules import UserStatDB
from Types import Exam


async def update_user_stats(user_id: int, score: int, exam_type: str):
    user_stats = await UserStatDB.find_one({"user_id": user_id}) or {}
    exam_data = user_stats.get(exam_type, {"score": 0, "total_attempts": 0, "last_attempt_time": 0})
    exam_data["score"] += score
    exam_data["total_attempts"] += 1
    exam_data["last_attempt_time"] = time.time()
    await UserStatDB.update_one(
        {"user_id": user_id},
        {"$set": {exam_type: exam_data}},
        upsert=True
    )

async def set_preferred_exam(user_id: int, exam_type: str):
    """
    Set the preferred exam type for a user.
    """
    await UserStatDB.update_one(
        {"user_id": user_id},
        {"$set": {"preferred_exam": exam_type}},
        upsert=True)

async def get_preferred_exam(user_id: int):
    """
    Get the preferred exam type for a user.
    """
    user_stats = await UserStatDB.find_one({"user_id": user_id})
    if user_stats:
        return user_stats.get("preferred_exam", None) 
    return None
# async def get_user_stats(user_id: int, raw: bool = False):
#     """
#     Retrieve user statistics from the database.
#     """
#     user_stats = await UserStatDB.find_one({"user_id": user_id})
#     if raw:
#         return user_stats  # Return raw data if requested
#     # Initialize the response with default values
#     response = {
#         "user_id": user_id,
#             Exam.JEE: {
#             "score": 0,
#             "total_attempts": 0
#         },
#         Exam.GOVT_EXAM: {
#             "score": 0,
#             "total_attempts": 0
#         }
#     }
#     if user_stats:
#         response[Exam.JEE] = user_stats.get(Exam.JEE, response[Exam.JEE])
#         response[Exam.GOVT_EXAM] = user_stats.get(Exam.GOVT_EXAM, response[Exam.GOVT_EXAM])
#     return response
async def get_user_stats(user_id: int, raw: bool = False):
    """
    Retrieve user statistics from the database in a flexible way using Exam class.
    """
    user_stats = await UserStatDB.find_one({"user_id": user_id})
    if raw:
        return user_stats
    response = {"user_id": user_id}
    for exam in Exam.exam_names:
        response[exam] = {
            "score": 0,
            "total_attempts": 0
        }
    if user_stats:
        for exam in Exam.exam_names:
            if exam in user_stats:
                response[exam].update(user_stats[exam])  
    return response



async def get_global_rank(user_id: int, exam_type: str):
    """
    Get the global rank of a user based on their score for a specific exam type.
    """
    user_stats = await get_user_stats(user_id)
    user_score = user_stats.get(exam_type, {}).get("score", 0) 
    higher_scores = await UserStatDB.count_documents({f"{exam_type}.score": {"$gt": user_score}})
    return higher_scores + 1


async def get_top_global_users(limit: int = 10, exam_type: str = Exam.JEE):
    """
    Get the top global users based on their scores for a specific exam type.
    """
    cursor = UserStatDB.find().sort(f"{exam_type}.score", -1).limit(limit)
    top_users = await cursor.to_list(length=limit)
    return [(user["user_id"], user.get(exam_type, {}).get("score", 0)) for user in top_users]  


async def get_highest_scorer_in_chat(chat_id: int, exam_type: str, limit: int = 1):
    chat_stats = await get_chat_stats(chat_id)
    if not chat_stats:
        return None, 0
    unique_participants = chat_stats.get("unique_participants", [])
    highest_scorer = await UserStatDB.find(
        {"user_id": {"$in": list(unique_participants)}}
    ).sort(f"{exam_type}.score", -1).limit(1).to_list(length=limit)
    if highest_scorer:
        return highest_scorer[0]['user_id'], highest_scorer[0].get(exam_type, {}).get('score', 0)  
    return None, 0


async def get_global_top_scorers(limit: int = 3, exam_type: str = Exam.JEE):
    global_stats = await get_global_stats()
    if not global_stats:
        return []
    unique_participants = global_stats.get("unique_participants", [])
    top_scorers = await UserStatDB.find(
        {"user_id": {"$in": list(unique_participants)}}
    ).sort(f"{exam_type}.score", -1).limit(limit).to_list(length=limit)
    return top_scorers