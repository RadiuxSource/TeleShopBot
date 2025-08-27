import asyncio
import importlib
from pyrogram import idle
from Modules.modules import ALL_MODULES
from . import initialize_bot

loop = asyncio.get_event_loop()

async def cbot_boot():
    await initialize_bot()
    for all_module in ALL_MODULES:
        importlib.import_module("Modules.modules." + all_module)
    print(str(ALL_MODULES))
    print("𝖻𝗈𝗍 𝗌𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎lly 𝗌𝗍𝖺𝗋𝗍")
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
