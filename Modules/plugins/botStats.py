import psutil
import time
from pyrogram import filters, types
from pyrogram.types import InlineKeyboardMarkup as IKM, InlineKeyboardButton as IKB
from Modules import zenova, SUDO_USERS, BOT_NAME
from Modules import db, ChatDB, UserDB, UserStatDB, BotDB, QuizDB
from utils import get_invite_link
from Modules.plugins.stats import get_user_quiz_stats, get_quiz_stats
from database import get_served_chats, get_served_users

start_time = time.time()

def time_formatter(milliseconds):
    minutes, seconds = divmod(int(milliseconds / 1000), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)
    tmp = (((str(weeks) + "ᴡ:") if weeks else "") +
           ((str(days) + "ᴅ:") if days else "") +
           ((str(hours) + "ʜ:") if hours else "") +
           ((str(minutes) + "ᴍ:") if minutes else "") +
           ((str(seconds) + "s") if seconds else ""))
    if not tmp:
        return "0s"
    if tmp.endswith(":"):
        return tmp[:-1]
    return tmp

@zenova.on_message(filters.command('stats') & filters.user(SUDO_USERS))
async def get_stats(client, msg: types.Message):
    k = await msg.reply("Wait, fetching detailed stats...")
    users = await get_served_users()
    chats = await get_served_chats()
    uptime = time_formatter((time.time() - start_time) * 1000)
    
    # System Metrics
    cpu_usage = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    cpu_stats = psutil.cpu_stats()
    cpu_count = psutil.cpu_count()
    
    # MongoDB Statistics
    db_stats = await db.command("dbstats")
    mongo_stats = f"""
📊 **Collections:**
   💬 Chats: `{await ChatDB.count_documents({}):,}`
   👤 Users: `{await UserDB.count_documents({}):,}`
   📈 User Stats: `{await UserStatDB.count_documents({}):,}`
   🤖 Bot Data: `{await BotDB.count_documents({}):,}`
   ❓ Quizzes: `{await QuizDB.count_documents({}):,}`

📦 **Database Storage:**
   Total: `{db_stats['dataSize'] / 10**6:.1f} MB`
   Avg Doc Size: `{db_stats['avgObjSize']:.2f} bytes`
   Storage Used: `{db_stats['storageSize'] / 10**6:.1f} MB`
   Indexes: `{db_stats['indexes']}`
    """
    
    # Formatting Numbers
    ram_total = f"{ram.total / (1024**3):.1f}"
    ram_used = f"{ram.used / (1024**3):.1f}"
    disk_total = f"{disk.total / (1024**3):.1f}"
    disk_used = f"{disk.used / (1024**3):.1f}"

    txt = f"""
**🤖 {BOT_NAME} Advanced Statistics Panel**

━━━━━━  **Bot Metrics**  ━━━━━━
📊 **Chats:** `{len(chats):,}` 
👥 **Users:** `{len(users):,}`
⏱️ **Uptime:** `{uptime}`

━━━━━━  **Database Statistics**  ━━━━━━
{mongo_stats}

━━━━━━  **System Health**  ━━━━━━
💻 **CPU Usage:** `{cpu_usage}%`
• Cores: `{cpu_count} ({'Logical' if psutil.cpu_count(logical=True) else 'Physical'})`
• CTX Switches: `{cpu_stats.ctx_switches:,}`
• Interrupts: `{cpu_stats.interrupts:,}`

🧠 **RAM Usage:** `{ram.percent}%`
• Total: `{ram_total} GB`
• Used: `{ram_used} GB`

💾 **Disk Usage:** `{disk.percent}%`
• Total: `{disk_total} GB`
• Used: `{disk_used} GB`

━━━━━━  **Performance Insights**  ━━━━━━
📈 **Active Processes:** `{len(psutil.pids())}`
🌐 **Network Stats:** 
   ↑ `{psutil.net_io_counters().bytes_sent / 1024**2:.1f} MB`
   ↓ `{psutil.net_io_counters().bytes_recv / 1024**2:.1f} MB`
"""

    await k.edit_text(txt)


@zenova.on_message(filters.command('prof', ['/', '.', '#']) & filters.user(SUDO_USERS))
async def admin_profiles(client, msg: types.Message):
    k=msg.text.split(' ')
    if not k[1]:
        return msg.reply('Provide id also with command.\nEg.:`/prof 6393380026`')
    id = int(k[1])
    stats = await get_user_quiz_stats(id)
    markup = IKM([[IKB('User account ↗', user_id= id)]])
    await msg.reply(stats, reply_markup=markup)

@zenova.on_message(filters.command('gprof', ['/', '.', '#']) & filters.user(SUDO_USERS))
async def admin_profiles(client, msg: types.Message):
    k=msg.text.split(' ')
    if not k[1]:
        return msg.reply('Provide id also with command.\nEg.:`/prof -1001833844898`')
    id = int(k[1])
    stats = await get_quiz_stats(id)
    link = await get_invite_link(id, client)
    markup = IKM([[IKB('Chat link ↗', url=link)]])
    await msg.reply(stats, reply_markup=markup)
