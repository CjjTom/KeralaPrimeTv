import random
import requests
import humanize
import base64
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, CallbackQuery
from info import LOG_CHANNEL, LINK_URL, ADMIN
from plugins.database import checkdb, db, get_count, get_withdraw, record_withdraw, record_visit
from urllib.parse import quote_plus, urlencode
from TechVJ.util.file_properties import get_name, get_hash, get_media_file_size
from TechVJ.util.human_readable import humanbytes

async def encode(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    base64_string = base64_bytes.decode("ascii").strip("=")
    return base64_string

async def decode(base64_string):
    base64_string = base64_string.strip("=")
    base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes)
    string = string_bytes.decode("ascii")
    return string

@Client.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if not await checkdb.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        name = await client.ask(message.chat.id, "<b>Welcome To KeralaCapitan.\n\nCreate your account now.\n\nSend your Business Name (e.g. <code>KeralaCapitan</code>)</b>")
        if name.text:
            await db.set_name(message.from_user.id, name=name.text)
        else:
            return await message.reply("**Invalid input. Restart with /start**")
        link = await client.ask(message.chat.id, "<b>Send your Telegram channel link (e.g. <code>https://t.me/KeralaCapitan</code>) ✅</b>")
        if link.text and link.text.startswith(('http://', 'https://')):
            await db.set_link(message.from_user.id, link=link.text)
        else:
            return await message.reply("**Invalid input. Restart with /start**")
        await checkdb.add_user(message.from_user.id, message.from_user.first_name)
        return await message.reply("<b>🎉 Account created!\n\nUse /quality to upload with options.\nUse /account, /update, /withdraw for other actions.\nOr send file directly.</b>")
    else:
        rm = InlineKeyboardMarkup([[InlineKeyboardButton("✨ Update Channel", url="https://t.me/KeralaCapitan")]])
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
    params = {'u': user_id, 'w': str(log_msg.id), 's': str(0), 't': str(0)}
    link = await encode(urlencode(params))
    encoded_url = f"{LINK_URL}?KeralaCapitan={link}"
    rm = InlineKeyboardMarkup([[InlineKeyboardButton("🖇️ Open Link", url=encoded_url)]])
    await message.reply_text(f"<code>{encoded_url}</code>", reply_markup=rm)

@Client.on_message(filters.private & filters.command("account"))
async def show_account(client, message):
    link_clicks = get_count(message.from_user.id)
    if link_clicks:
        balance = link_clicks / 1000.0
        formatted_balance = f"{balance:.2f}"
        response = f"<b>API Key: <code>{message.from_user.id}</code>\n\nVideo Plays: {link_clicks}\nBalance: ${formatted_balance}</b>"
    else:
        response = f"<b>API Key: <code>{message.from_user.id}</code>\nVideo Plays: 0\nBalance: $0</b>"
    await message.reply(response)

@Client.on_message(filters.private & filters.command("update"))
async def update(client, message):
    name = await client.ask(message.chat.id, "<b>Send new Business Name (e.g. <code>KeralaCapitan</code>)</b>")
    if name.text == "/cancel":
        return await message.reply("**Update cancelled.**")
    if name.text:
        await db.set_name(message.from_user.id, name=name.text)
    else:
        return await message.reply("**Invalid input. Try /update again**")

    link = await client.ask(message.chat.id, "<b>Send your updated Telegram channel link (e.g. <code>https://t.me/KeralaCapitan</code>) ✅</b>")
    if link.text and link.text.startswith(('http://', 'https://')):
        await db.set_link(message.from_user.id, link=link.text)
    else:
        return await message.reply("**Invalid input. Try /update again**")
    return await message.reply("<b>✅ Update successful.</b>")

@Client.on_message(filters.private & filters.text & ~filters.command(["account", "withdraw", "notify", "quality", "start", "update"]))
async def link_start(client, message):
    if not message.text.startswith(LINK_URL):
        return
    link_part = message.text[len(LINK_URL + "?KeralaCapitan="):].strip()
    try:
        original = await decode(link_part)
    except:
        return await message.reply("**Link Invalid**")
    try:
        u, user_id, id, sec, th = original.split("=")
    except:
        return await message.reply("**Link Invalid**")

    user_id = user_id.replace("&w", "")
    if user_id == str(message.from_user.id):
        rm = InlineKeyboardMarkup([[InlineKeyboardButton("🖇️ Open Link", url=message.text)]])
        return await message.reply_text(f"<code>{message.text}</code>", reply_markup=rm)

    id = id.replace("&s", "")
    sec = sec.replace("&t", "")
    params = {'u': message.from_user.id, 'w': id, 's': sec, 't': th}
    link = await encode(urlencode(params))
    encoded_url = f"{LINK_URL}?KeralaCapitan={link}"
    rm = InlineKeyboardMarkup([[InlineKeyboardButton("🖇️ Open Link", url=encoded_url)]])
    await message.reply_text(f"<code>{encoded_url}</code>", reply_markup=rm)
