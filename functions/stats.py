from telethon import events

from functions.echo_state import echo_groups
from functions.antidel_state import antidel_groups
from functions import alwaysonline
from functions import autoreply


def register_stats(client, get_clock_state):

    # Userbot statistics
    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"\.stats"
        )
    )
    async def stats_cmd(event):

        dialogs = await client.get_dialogs()

        groups = sum(
            1 for d in dialogs
            if d.is_group
        )

        privates = sum(
            1 for d in dialogs
            if d.is_user
        )

        clock_status = (
            "✅ Enabled"
            if get_clock_state()
            else "❌ Disabled"
        )

        online_status = (
            "🟢 ON"
            if alwaysonline.online_enabled
            else "🔴 OFF"
        )

        autoreply_status = (
            "🟢 ON"
            if autoreply.autoreply_enabled
            else "🔴 OFF"
        )

        text = (
            f"<b>📊 Userbot Statistics:</b>\n"
            f"• 👥 Groups: {groups}\n"
            f"• 🔐 Private chats: {privates}\n\n"
            f"• ♻️ Echo (active chats): "
            f"{len(echo_groups)}\n"
            f"• ⏰ Profile clock: {clock_status}\n"
            f"• 🟢 Always Online: {online_status}\n"
            f"• 🤖 Auto Reply: {autoreply_status}\n"
            f"• 🛰 AntiDel (active chats): "
            f"{len(antidel_groups)}"
        )

        await event.edit(
            text,
            parse_mode="html"
        )