import asyncio
import os
import shutil
from datetime import datetime

import urllib3
from pyrogram import filters
from Modules import zenova
from utils import paste
import config
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

async def update_(client, message):
    response = await message.reply_text("Updating...")
    try:
        repo = Repo()
    except GitCommandError:
        return await response.edit("Error: Git command failed.")
    except InvalidGitRepositoryError:
        return await response.edit("Error: Invalid Git repository.")
    to_exc = f"git fetch origin {config.Settings.UPSTREAM_BRANCH} &> /dev/null"
    os.system(to_exc)
    await asyncio.sleep(7)
    verification = ""
    REPO_ = repo.remotes.origin.url.split(".git")[0]
    for checks in repo.iter_commits(f"HEAD..origin/{config.Settings.UPSTREAM_BRANCH}"):
        verification = str(checks.count())
    if verification == "":
        return await response.edit("No updates available.")
    updates = ""
    for info in repo.iter_commits(f"HEAD..origin/{config.Settings.UPSTREAM_BRANCH}"):
        updates += f"#{info.count()}: {info.summary}\n\t\t\t\tCommitted on: {datetime.fromtimestamp(info.committed_date).strftime('%d %b, %Y')}\n\n"
    _final_updates_ = f"Updates available:\n\n{updates}"
    if len(_final_updates_) > 4096:
        url = await paste(updates)
        nrs = await response.edit(f"Updates available:\n\n<a href={url}>Check updates</a>")
    else:
        nrs = await response.edit(_final_updates_, disable_web_page_preview=True)
    os.system("git stash &> /dev/null && git pull")
    await response.edit(f"```\n{nrs.text}\n```\n\n**Update successful!**")

async def restart_(client, message):
    response = await message.reply_text("Restarting...")
    try:
        shutil.rmtree("downloads")
        shutil.rmtree("raw_files")
        shutil.rmtree("cache")
    except:
        pass
    await response.edit_text("Restart process initiated.")
    print("Restart process initiated.")
    os.system(f"kill -9 {os.getpid()} && ulimit -n 16384 && python3 -m Modules")

@zenova.on_message(filters.command(["update", "gitpull"]) & filters.user(config.Settings.SUDO_USERS))
async def update(client, message):
    await update_(client, message)

@zenova.on_message(filters.command(["restart", "reboot"])& filters.user(config.Settings.SUDO_USERS))
async def restart(client, message):
    await restart_(client, message)