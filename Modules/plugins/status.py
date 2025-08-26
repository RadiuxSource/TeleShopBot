import psutil
import time
from pyrogram import filters, types
from Modules import zenova as app, BOT_NAME, boot as start_time



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

@app.on_message(filters.command('RocksStatusBot'))
async def get_stats(client, msg: types.Message):
    # Calculate uptime
    uptime = time_formatter((time.time() - start_time) * 1000)

    # Get CPU, RAM, and Disk usage
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    txt = (
        f"ᴜᴘᴛɪᴍᴇ : {uptime} | ᴄᴘᴜ : {cpu}%\n"
        f"ㅤ╰⊚ ʀᴀᴍ : {ram}% | ᴅɪsᴋ : {disk}%"
    )

    await msg.reply(txt)
