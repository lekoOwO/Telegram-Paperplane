from userbot import LOGS, CMD_HELP
import os
from io import BytesIO
from psutil import swap_memory, virtual_memory
from telethon.tl.types import MessageMediaPhoto
from datetime import datetime
from userbot.events import register

from typing import Union

def count(limit = 10):
    count = 0
    while True:
        yield not count
        count += 1
        count %= limit

def download_progress(callback=None):
    counter = count()
    async def _download_progress(current, total):
        """ Logs the download progress """
        LOGS.info(f"Downloaded {current} of {total}\nCompleted {round((current / total) * 100, 2)}%")
        if callback and next(counter):
            await callback(current, total)

    return _download_progress

def upload_progress(callback=None):
    counter = count()
    async def _upload_progress(current, total):
        """ Logs the upload progress """
        LOGS.info(f"Uploaded {current} of {total}\nCompleted {round((current / total) * 100, 2)}%")
        if callback and next(counter): 
            await callback(current, total)

    return _upload_progress

async def download_from_tg(message, callback=None) -> (str, Union[BytesIO, None]):
    """
    Download files from Telegram
    """
    async def dl_file() -> BytesIO:
        buffer = BytesIO()
        await message.client.download_media(
            message,
            buffer,
            progress_callback=download_progress(callback),
        )
        buffer.seek(0)
        return buffer
    
    buf = None

    avail_mem = virtual_memory().available + swap_memory().free
    try:
        if message.file.size >= avail_mem:  # unlikely to happen but baalaji crai
            filen = await message.client.download_media(
                message,
                progress_callback=download_progress(callback),
            )
        else:
            buf = await dl_file()
            filen = message.file.name
            if not buf.name:
                buf.name = filen

    except AttributeError:
        buf = await dl_file()
        try:
            filen = message.file.name
        except AttributeError:
            if message.photo:
                filen = 'photo-' + str(datetime.today())\
                    .split('.')[0].replace(' ', '-') + '.jpg'
            else:
                filen = message.file.mime_type\
                    .replace('/', '-' + str(datetime.today())
                             .split('.')[0].replace(' ', '-') + '.')
    return filen, buf

@register(pattern=r"^.resendf(?:[ |$]?)(.*)", outgoing=True)
async def resend(bot):
    text = bot.pattern_match.group(1)
    text = text if text else '`.`'

    if not bot.file:
        print(bot)
        await bot.reply(message="`No file found!`", parse_mode='Markdown')
        return

    filen, buf = await download_from_tg(bot)

    if buf:
        uploaded_file = await bot.client.upload_file(file=buf, file_name=filen, part_size_kb=512,
            progress_callback=upload_progress()
        )
        await bot.edit(text=text, parse_mode='Markdown', file=uploaded_file)
    else:
        uploaded_file = await bot.client.upload_file(file=filen, progress_callback=upload_progress())
        await bot.edit(text=text, parse_mode='Markdown', file=uploaded_file, part_size_kb=512)
        os.remove(filen)

@register(pattern=r"^.resendr(?:[ |$]?)(.*)", outgoing=True)
async def resend_reply(bot):
    text = bot.pattern_match.group(1)
    text = text if text else '`.`'

    message = await bot.get_reply_message()

    if not message.file:
        print(message)
        await bot.edit(text="`No file found!`", parse_mode='Markdown')
        return

    await bot.delete()
    empty_file = BytesIO(" ".encode("UTF-8"))
    empty_file.name = "empty"
    bot = await message.reply(message="Downloading...", parse_mode="Markdown", file=empty_file)

    filen, buf = await download_from_tg(await bot.get_reply_message(), 
        lambda current, total: bot.edit(f"`Downloading... {round((current / total) * 100, 2)}%`")
    )

    await bot.edit(text="`Uploading...`", parse_mode='Markdown')

    if buf:
        uploaded_file = await bot.client.upload_file(file=buf, file_name=filen, part_size_kb=512, 
            progress_callback=upload_progress(lambda current, total: bot.edit(f"`Uploading... {round((current / total) * 100, 2)}%`"))
        )
        await bot.edit(text=text, parse_mode='Markdown', file=uploaded_file)
    else:
        uploaded_file = await bot.client.upload_file(file=filen, part_size_kb=512,
            progress_callback=upload_progress(lambda current, total: bot.edit(f"`Uploading... {round((current / total) * 100, 2)}%`"))
        )
        await bot.edit(text=text, parse_mode='Markdown', file=uploaded_file)
        os.remove(filen)

CMD_HELP.update({
    "resend":
    ".resend [Your text to send]\n"
    "Usage: Resend a file in case of stubi Unigram always send files as document."
})

CMD_HELP.update({
    "resend_reply":
    ".resend_reply [Your text to send] [in reply to TG file]\n"
    "Usage: Resend a file in case of stubi Unigram always send files as document. For reply use."
})