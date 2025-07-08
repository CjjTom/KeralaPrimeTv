import re
from os import environ

# Bot Session Name
SESSION = environ.get('SESSION', 'CjTomBot')

# Your Telegram Account Api Id And Api Hash
API_ID = int(environ.get('API_ID', '24026226'))
API_HASH = environ.get('API_HASH', '76b243b66cf12f8b7a603daef8859837')

# Bot Token, This Is Main Bot
BOT_TOKEN = environ.get('BOT_TOKEN', "8168332779:AAGH8Wm-P6iL46KkGUKZ0NqiDFub5GcDfdo")

# Admin Telegram Account Id For Withdraw Notification Or Anything Else
ADMIN = int(environ.get('ADMIN', '7898534200'))

# Back Up Bot Token For Fetching Message When Floodwait Comes
BACKUP_BOT_TOKEN = environ.get('BACKUP_BOT_TOKEN', "7648703946:AAGWnLrXG-tdE68AUYZcqQnQTs-_-8MxfLI")

# Log Channel, In This Channel Your All File Stored.
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '-1002805592130'))

# Mongodb Database For User Link Click Count Etc Data Store.
MONGODB_URI = environ.get("MONGODB_URI", "mongodb+srv://primemastix:o84aVniXFmKfyMwH@cluster0.qgiry.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

# Stream Url Means Your Deploy Server App Url, Here You Media Will Be Stream And Ads Will Be Shown.
STREAM_URL = environ.get("STREAM_URL", "")

# This Link Used As Permanent Link That If Your Deploy App Deleted Then You Change Stream Url, So This Link Will Redirect To Stream Url.
LINK_URL = environ.get("LINK_URL", "https://keralaprime.infy.uk/10-2")

# Others, Not Usefull
PORT = environ.get("PORT", "8080")
MULTI_CLIENT = False
SLEEP_THRESHOLD = int(environ.get('SLEEP_THRESHOLD', '60'))
PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))  # 20 minutes
if 'DYNO' in environ:
    ON_HEROKU = True
else:
    ON_HEROKU = False
