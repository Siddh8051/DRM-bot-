from fileinput import filename
from pyrogram import filters, Client as ace
from main import LOGGER, prefixes
from pyrogram.types import Message
from main import Config
import os
import subprocess
import tgcrypto
import shutil
import sys
from handlers.uploader import Upload_to_Tg
from handlers.tg import TgClient
import aiohttp
# Define authentication headers
#auth_headers = "eyJjb3Vyc2VJZCI6IjQ1NjY4NyIsInR1dG9ySWQiOm51bGwsIm9yZ0lkIjo0ODA2MTksImNhdGVnb3J5SWQiOm51bGx9"

@ace.on_message(
    (filters.chat(Config.GROUPS) | filters.chat(Config.AUTH_USERS)) &
    filters.incoming & filters.command("drm", prefixes=prefixes)
)
async def drm(bot: ace, m: Message):
    path = f"{Config.DOWNLOAD_LOCATION}/{m.chat.id}"
    tPath = f"{Config.DOWNLOAD_LOCATION}/THUMB/{m.chat.id}"
    os.makedirs(path, exist_ok=True)

    inputData = await bot.ask(m.chat.id, "**Send**\n\nMPD\nNAME\nQUALITY\nCAPTION")
    mpd, raw_name, Q, CP = inputData.text.split("\n")
    name = f"{TgClient.parse_name(raw_name)} ({Q}p)"
    print(mpd, name, Q)
    
class Download:
    def __init__(self, mpd):
        self._remoteapi = "https://app.magmail.eu.org/get_keys"
        self.mpd = mpd

    async def get_keys(self):
        async with aiohttp.ClientSession() as session:
            async with session.post(self._remoteapi, json={"mpd": self.mpd}) as response:
                data = await response.json()
                # Assuming the API returns keys in the format "KID:KEY"
                keys = data["keys"]
                return keys
    print(keys)

    BOT = TgClient(bot, m, path)
    Thumb = await BOT.thumb()
    prog  = await bot.send_message(m.chat.id, f"**Downloading Drm Video!** - [{name}]({mpd})")

    cmd1 = f'yt-dlp -o "{path}/fileName.%(ext)s" -f "bestvideo[height<={int(Q)}]+bestaudio" --allow-unplayable-format --external-downloader aria2c "{mpd}"'
    os.system(cmd1)
    avDir = os.listdir(path)
    print(avDir)
    print("Decrypting")
    
    try:
        for data in avDir:
            if data.endswith("mp4"):
                cmd2 = f'mp4decrypt {keys} --show-progress "{path}/{data}" "{path}/video.mp4"'
                os.system(cmd2)
                os.remove(f'{path}/{data}')
            elif data.endswith("m4a"):
                cmd3 = f'mp4decrypt {keys} --show-progress "{path}/{data}" "{path}/audio.m4a"'
                os.system(cmd3)
                os.remove(f'{path}/{data}')


        cmd4 = f'ffmpeg -i "{path}/video.mp4" -i "{path}/audio.m4a" -c copy "{path}/{name}.mp4"'
        os.system(cmd4)
        os.remove(f"{path}/video.mp4")
        os.remove(f"{path}/audio.m4a")
        filename = f"{path}/{name}.mp4"
        cc = f"{name}.mp4\n\n**Description:-**\n{CP}"
        # await DownUP.sendVideo(bot, m, filename, cc, Thumb, name, prog, path)
        UL = Upload_to_Tg(bot=bot, m=m, file_path=filename, name=name,
                            Thumb=Thumb, path=path, show_msg=prog, caption=cc)
        await UL.upload_video()
        print("Done")
    except Exception as e:
        await prog.delete(True)
        await m.reply_text(f"**Error**\n\n`{str(e)}`\n\nOr May be Video not Availabe in {Q}")
    finally:
        if os.path.exists(tPath):
            shutil.rmtree(tPath)
        shutil.rmtree(path)
        await m.reply_text("Done")
