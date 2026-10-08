# @aliyhacker

import time
import pytz

from datetime import datetime

from telethon import TelegramClient
import config

from config import ALLOWED_USERS

from functions.profile_clock import register_profile_clock
from functions.com import register_com
from functions.restart import register_restart
from functions.echo import register_echo
from functions.antidel import register_antidel
from functions.info import register_info
from functions.math import register_math
from functions.translate import register_translate
from functions.broadcast import register_broadcast
from functions.edit import register_edit
from functions.ping import register_ping
from functions.nettest import register_nettest
from functions.chatinfo import register_chatinfo
from functions.hack import register_hack
from functions.glban import register_glban
from functions.unglban import register_unglban
from functions.banlist import register_banlist
from functions.stats import register_stats
from functions.aimode import register_aimode
from functions.whatsup import register_whatsup
from functions.open import register_open
from functions.term import register_term
from functions.ai import register_ai
from functions.staff import register_staff
from functions.code import register_code
from functions.autoreply import register_autoreply
from functions.weather import register_weather
from functions.day import register_day
from functions.stik import register_stik
from functions.forward import register_forward
from functions.animations import register_animations
from functions.alwaysonline import register_always_online
from functions.rsave import register_rsave
from functions.com import register_com
from functions.delall import register_delall
from functions.autocomment import register_autocomment

# TELEGRAM CLIENT

client = TelegramClient(
    "UserbotSession",
    config.API_ID,
    config.API_HASH
)

# GLOBAL SETTINGS / STATES

clock_running = False

tz = pytz.timezone("Asia/Tashkent")

ban_list = set()
ban_info = {}

antidel_private = set()

bot_start_time = time.time()
register_delall(client)
register_autocomment(client)
# AI chat states
# chat_id : {
#     "active": bool,
#     "all_users": bool,
#     "messages": []
# }
ai_chats = {}


# FORWARD SETTINGS

# Add your target chat/channel IDs in config.py if needed.
forwchannel = getattr(config, "FORW_CHANNEL", [])
forwgroup = getattr(config, "FORW_GROUP", [])
forwchat = getattr(config, "FORW_CHAT", [])


# PROFILE CLOCK STATE

def get_clock_state():
    return clock_running


def set_clock_state(value):
    global clock_running
    clock_running = value


# REGISTER FUNCTIONS

register_animations(client)

register_forward(
    client,
    forwchannel,
    forwgroup,
    forwchat
)

register_stik(client)

register_day(client)

register_weather(client)

register_code(client)

register_staff(client)

register_ai(client)

register_term(
    client,
    ALLOWED_USERS
)

register_open(client)
register_rsave(client)
register_com(client)
register_whatsup(client)

register_aimode(client)

register_echo(client)

register_antidel(client)

register_stats(
    client,
    get_clock_state
)

register_translate(client)

register_info(client)

register_math(client)

register_restart(client)

register_broadcast(client)

register_edit(client)

register_chatinfo(client)

register_nettest(client)

register_ping(
    client,
    bot_start_time
)

register_hack(client)

register_autoreply(client)

register_glban(client)

register_unglban(client)

register_banlist(client)

register_com(client)


# PROFILE CLOCK

register_profile_clock(
    client,
    tz,
    get_clock_state,
    set_clock_state
)

register_always_online(client)
# START USERBOT

print("Starting userbot...")

client.start()


print("Userbot is running!")

client.run_until_disconnected()
