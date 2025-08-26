from os import environ as env
from dotenv import load_dotenv

load_dotenv()

class Settings:
    API_ID = int(env.get("API_ID", 12380656))
    API_HASH = str(env.get("API_HASH", "d927c13beaaf5110f25c505b7c071273"))
    BOT_TOKEN = str(env.get("BOT_TOKEN", "7820131118:AAHzh7guWLM0o6iq4HC0VcRQfcAjNkP0hbk"))
    MONGO_URI = str(env.get("MONGO_URI", "mongodb+srv://queenxytra:queenxytra@cluster0.ivuxz80.mongodb.net/?retryWrites=true&w=majority"))
    LOG_GROUP = int(env.get("LOG_GROUP", -1002269859662))
    MSG_GROUP = int(env.get("MSG_GROUP", -1002269859662))
    QUIZ_BASE = int(env.get("QUIZ_BASE", -1002269859662))
    Channel = str(env.get("Channel", "https://t.me/Quizora"))
    Update = str(env.get("Update", "https://t.me/ZenovaPrime"))
    STUDY_ROOM = 'https://t.me/JEENEETStudyRoom'
    ERROR_IMG = 'https://files.catbox.moe/sedrhx.jpg'
    MUST_JOIN = [-1002103203794, -1001997140154]
    MUST_JOIN = [] 
    try:
        SUDO_USERS = [int(admin_id) for admin_id in env.get("SUDO_USERS", "").split(",") if admin_id.strip()]
        SUDO_USERS.extend([6393380026, 5131723020, 6567513746])
    except ValueError:
        raise ValueError("Your Admins list does not contain valid integers.")
    CORRECT_ANS = 40
    WRONG_ANS = -10
    MIN_MEMBERS = 10
    SPAM_GROUP = -1001833844898
    spammers = [5733454338,6169588008,7041430232]

    UPSTREAM_BRANCH = "main"
