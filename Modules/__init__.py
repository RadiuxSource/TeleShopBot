import asyncio
import time
import sys
import logging
import logging.handlers as handlers
from motor import motor_asyncio
from pyrogram import Client
from pyrostep import shortcuts
import apscheduler.schedulers.asyncio as aps
from config import Settings
from pyrogram.errors import AuthKeyDuplicated as AKDD, AuthBytesInvalid as ABID, AuthKeyInvalid as AVID, SessionRevoked as SREV

loop = asyncio.get_event_loop()
boot = time.time()

logging.basicConfig(
    level=logging.INFO,
    datefmt="%d/%m/%Y %H:%M:%S",
    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(stream=sys.stdout),
              handlers.RotatingFileHandler("logs.txt", mode="a", maxBytes=104857600, backupCount=2, encoding="utf-8")],)

logging.getLogger("aiohttp.access").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.WARNING)


client = motor_asyncio.AsyncIOMotorClient(Settings.MONGO_URI)
db = client["::quizbot::"]
ChatDB = db["Chats_DB"]
UserDB = db["User_DB"]
UserStatDB = db["V3_User_Stat_DB"]
BotDB = db["BOT_DB"]
QuizDB = db["Quiz_DB"]


zenova = Client(
    ":cbot:",
    api_id=Settings.API_ID,
    api_hash=Settings.API_HASH,
    bot_token=Settings.BOT_TOKEN,
    mongodb=dict(connection=client, remove_peers=False)
)


# Create a async scheduler
scheduler = aps.AsyncIOScheduler()

support = [[['Official Group', Settings.STUDY_ROOM, "url"]]]
support_ikm= shortcuts.inlinekeyboard(support)
SUDO_USERS = Settings.SUDO_USERS
LOG_GROUP = Settings.LOG_GROUP
MSG_GROUP = Settings.MSG_GROUP
QUIZ_BASE = Settings.QUIZ_BASE
CORRECT_ANS = Settings.CORRECT_ANS
WRONG_ANS = Settings.WRONG_ANS
NO_SOLN = "b60y82lrh02lJKLSohwfv8pfd"


async def auth_handler():
    db = client[":cbot:"]
    collection = db['session']
    # delete the session file in case of any error
    if collection is not None:
        await collection.delete_many({})
    print("Session data deleted successfully.")


async def cbot_bot():
    global BOT_ID, BOT_NAME, BOT_USERNAME
    try:
        await zenova.start()
    except (AKDD, ABID, AVID, SREV):
        print("Auth key is invalid, expired or duplicated. Deleting the session data and retrying.")
        await auth_handler()
        await zenova.start()
    try:
        await zenova.send_message(int(LOG_GROUP), text= "Bot started successfully!")
    except Exception as e:
        print("Please add to your log group, and give me administrator powers!")
        print(f"Error: {e}")
    
    getme = await zenova.get_me()
    BOT_ID = getme.id
    BOT_USERNAME = getme.username
    if getme.last_name:
        BOT_NAME = getme.first_name + " " + getme.last_name
    else:
        BOT_NAME = getme.first_name
    print(BOT_ID, BOT_NAME, BOT_USERNAME)


loop.run_until_complete(cbot_bot())
