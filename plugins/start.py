# KeralaCapitan Bot Full Code (Updated with Advanced Features)
# Make sure you have updated 'info.py' with:
# LINK_URL = "https://yourdomain.in"
# LOG_CHANNEL = <your_log_channel_id>
# ADMIN = <your_admin_id>

import random
import requests
import humanize
import base64
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import LOG_CHANNEL, LINK_URL, ADMIN
from plugins.database import checkdb, db, get_count, get_withdraw, record_withdraw, record_visit
from urllib.parse import quote_plus, urlencode
from TechVJ.util.file_properties import get_name, get_hash, get_media_file_size
from TechVJ.util.human_readable import humanbytes

async def encode(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    return base64_bytes.decode("ascii").strip("=")

async def decode(base64_string):
    base64_string = base64_string.strip("=")
    base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes)
    return string_bytes.decode("ascii")

@Client.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if not await checkdb.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        name = await client.ask(message.chat.id, "<b>Welcome to KeralaCapitan\n\nSend your Business Name (e.g. <code>KeralaCapitan</code>)</b>")
        if not name.text:
            return await message.reply("**Invalid input. Use /start again.**")
        await db.set_name(message.from_user.id, name=name.text)

        link = await client.ask(message.chat.id, "<b>Send your Telegram Channel Link (e.g. <code>https://t.me/KeralaCaptain</code>) ✅</b>")
        if not link.text or not link.text.startswith(('http://', 'https://')):
            return await message.reply("**Invalid input. Use /start again.**")
        await db.set_link(message.from_user.id, link=link.text)

        await checkdb.add_user(message.from_user.id, message.from_user.first_name)
        return await message.reply("<b>🎉 Account created successfully!\n\nUse /quality to upload with options or send files directly.</b>")
    else:
        rm = InlineKeyboardMarkup([[InlineKeyboardButton("✨ Update Channel", url="https://t.me/KeralaCaptain")]])
        await client.send_message(
            chat_id=message.from_user.id,
            text=script.START_TXT.format(message.from_user.mention),
            reply_markup=rm,
            parse_mode=enums.ParseMode.HTML
        )

@Client.on_message(filters.private & (filters.document | filters.video))
async def stream_start(client, message):
    file = getattr(message, message.media.value)
    fileid = file.file_id
    user_id = message.from_user.id
    log_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
    params = {'u': user_id, 'w': str(log_msg.id), 's': '0', 't': '0'}
    link = await encode(urlencode(params))
    encoded_url = f"{LINK_URL}?KeralaCapitan={link}"
    rm = InlineKeyboardMarkup([[InlineKeyboardButton("🖇️ Open Link", url=encoded_url)]])
    await message.reply_text(f"<code>{encoded_url}</code>", reply_markup=rm)

@Client.on_message(filters.private & filters.command("quality"))
async def quality_link(client, message):
    qualities = {}
    available = ["480", "720", "1080"]
    used = []
    for _ in range(3):
        prompt = f"<b>Send Quality (480 / 720 / 1080) or /getlink to finish</b>"
        q = await client.ask(message.chat.id, prompt)
        if q.text == "/getlink":
            break
        if q.text not in available or q.text in used:
            await message.reply("**Invalid or Duplicate Quality. Try again.**")
            continue
        f = await client.ask(message.chat.id, f"Now send the file for {q.text}p quality")
        if not (f.video or f.document):
            await message.reply("**Invalid file. Try again.**")
            continue
        file = getattr(f, f.media.value)
        msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=file.file_id)
        qualities[q.text] = str(msg.id)
        used.append(q.text)

    if not qualities:
        return await message.reply("**No qualities uploaded. Use /quality again.**")

    params = {
        'u': str(message.from_user.id),
        'w': qualities.get("480", "0"),
        's': qualities.get("720", "0"),
        't': qualities.get("1080", "0")
    }
    link = await encode(urlencode(params))
    encoded_url = f"{LINK_URL}?KeralaCapitan={link}"
    rm = InlineKeyboardMarkup([[InlineKeyboardButton("🖇️ Open Link", url=encoded_url)]])
    await message.reply_text(f"<code>{encoded_url}</code>", reply_markup=rm)

@Client.on_message(filters.private & filters.command("account"))
async def show_account(client, message):
    link_clicks = get_count(message.from_user.id)
    balance = (link_clicks or 0) / 1000.0
    formatted = f"{balance:.2f}"
    await message.reply(f"<b>API Key: <code>{message.from_user.id}</code>\nVideo Plays: {link_clicks}\nBalance: ${formatted}</b>")

@Client.on_message(filters.private & filters.command("update"))
async def update_account(client, message):
    name = await client.ask(message.chat.id, "<b>Send new Business Name</b>")
    if name.text:
        await db.set_name(message.from_user.id, name=name.text)
    link = await client.ask(message.chat.id, "<b>Send new Telegram Channel Link</b>")
    if link.text and link.text.startswith(('http://', 'https://')):
        await db.set_link(message.from_user.id, link=link.text)
        await message.reply("<b>✅ Updated Successfully.</b>")
    else:
        await message.reply("**Invalid link. Try /update again.**")

@Client.on_message(filters.private & filters.text & ~filters.command(["start", "account", "quality", "update"]))
async def handle_links(client, message):
    if not message.text.startswith(LINK_URL):
        return
    link_part = message.text[len(LINK_URL + "?KeralaCapitan="):].strip()
    try:
        original = await decode(link_part)
        u, user_id, id, sec, th = original.split("=")
        user_id = user_id.replace("&w", "")
        id = id.replace("&s", "")
        sec = sec.replace("&t", "")
        if user_id == str(message.from_user.id):
            await message.reply_text(f"<code>{message.text}</code>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🖇️ Open Link", url=message.text)]]))
        else:
            params = {'u': message.from_user.id, 'w': id, 's': sec, 't': th}
            new_link = await encode(urlencode(params))
            encoded_url = f"{LINK_URL}?KeralaCapitan={new_link}"
            await message.reply_text(f"<code>{encoded_url}</code>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🖇️ Open Link", url=encoded_url)]]))
    except:
        await message.reply("**Invalid or corrupted link.**")
            
