import re
import jinja2
import logging
import aiohttp
from info import *
import urllib.parse
from TechVJ.bot import TechVJBot, TechVJBackUpBot
from TechVJ.util.human_readable import humanbytes
from TechVJ.server.exceptions import InvalidHash
from pyrogram.errors import FloodWait
from TechVJ.util.file_properties import get_name, get_hash, get_media_file_size, get_file_ids
from plugins.database import db

async def render_page(id, user, secid=None, thid=None, fourid=None, fiveid=None, src=None):
    file_data = None
    file_urls = {}
    quality_map = {
        '360': None,
        '420': None,
        '480': None,
        '540': None,
        '720': None,
        '1080': None
    }

    id_mapping = {
        '360': id,
        '420': secid,
        '480': thid,
        '540': fourid,
        '720': fiveid,
        '1080': src
    }

    for quality, msg_id in id_mapping.items():
        if msg_id and msg_id != '0':
            try:
                msg = await TechVJBot.get_messages(int(LOG_CHANNEL), int(msg_id))
            except:
                msg = await TechVJBackUpBot.get_messages(int(LOG_CHANNEL), int(msg_id))

            file_data = await get_file_ids(msg)

            file_urls[f'file_url_{quality}'] = urllib.parse.urljoin(
                STREAM_URL + "dl/",
                f"{msg_id}/{urllib.parse.quote_plus(file_data.file_name)}?hash={file_data.unique_id[:6]}",
            )
            quality_map[quality] = quality
        else:
            file_urls[f'file_url_{quality}'] = None

    if not file_data:
        for msg_id in [id, secid, thid, fourid, fiveid, src]:
            if msg_id and msg_id != '0':
                try:
                    msg = await TechVJBot.get_messages(int(LOG_CHANNEL), int(msg_id))
                except:
                    msg = await TechVJBackUpBot.get_messages(int(LOG_CHANNEL), int(msg_id))
                file_data = await get_file_ids(msg)
                if file_data:
                    break

    if not file_data:
        raise InvalidHash("No valid file data found")

    tag = file_data.mime_type.split("/")[0].strip()
    file_size = humanbytes(file_data.file_size)

    if tag in ["document", "video", "audio"]:
        template_file = "TechVJ/template/req.html"
    else:
        template_file = "TechVJ/template/dl.html"
        async with aiohttp.ClientSession() as s:
            async with s.get(src) as u:
                file_size = humanbytes(int(u.headers.get("Content-Length")))

    with open(template_file) as f:
        template = jinja2.Template(f.read())

    old_file_name = file_data.file_name.replace("_", " ")
    file_name_clean = clean_file_name(old_file_name)
    file_name = remove_after_year(file_name_clean)
    link = await db.get_link(int(user))
    name = await db.get_name(int(user))

    context = {
        "file_name": file_name,
        "file_size": file_size,
        "user_id": user,
        "link": link,
        "name": name,
        "thumbnail_url": THUMBNAIL_URL
    }

    context.update(file_urls)
    return template.render(**context)


def clean_file_name(file_name):
    file_name = re.sub(r"(_|\-|\.|\+)", " ", str(file_name)) 
    unwanted_chars = ['[', ']', '(', ')', '{', '}']

    for char in unwanted_chars:
        file_name = file_name.replace(char, '')

    return ' '.join(filter(lambda x: not x.startswith('@') and not x.startswith('http') and not x.startswith('www.') and not x.startswith('t.me'), file_name.split()))


def remove_after_year(filename):
    match = re.search(r'\d{4}', filename)
    if match:
        year_index = match.start()
        year_end_index = match.end()
        new_filename = filename[:year_end_index].strip()
        return new_filename
    return filename
