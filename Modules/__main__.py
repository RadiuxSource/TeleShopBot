import asyncio
import importlib
from aiohttp import web
from pyrogram import idle
from Modules.plugins import ALL_MODULES
from Modules import scheduler, db
from Modules.setup_db import setup_indexes

loop = asyncio.get_event_loop()

async def index(request):
    return web.Response(text='Hello from Telegram Bot!')

async def read_logs(request):
    try:
        with open('zenova.log', 'r') as f:
            return web.Response(text=f.read())
    except FileNotFoundError:
        return web.Response(status=404, text="Log file not found")
    except Exception as e:
        return web.Response(status=500, text=str(e))

async def cbot_boot():
    await setup_indexes(db)
    for all_module in ALL_MODULES:
        importlib.import_module("Modules.plugins." + all_module)
    print(str(ALL_MODULES))
    print("𝖻𝗈𝗍 𝗌𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎lly 𝗌𝗍𝖺𝗋𝗍")
    scheduler.start()
    await idle()

if __name__ == "__main__":
    # app = web.Application()
    # app.router.add_get('/', index)
    # app.router.add_get('/logs', read_logs)

    # # Start the aiohttp web server
    # runner = web.AppRunner(app)
    # loop.run_until_complete(runner.setup())
    # site = web.TCPSite(runner, '0.0.0.0', 8000)
    # loop.run_until_complete(site.start())

    # Start the bot
    loop.run_until_complete(cbot_boot())
