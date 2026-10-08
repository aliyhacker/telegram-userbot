import asyncio
from datetime import datetime
from telethon import events

from functions.ban_state import ban_list, ban_info


def register_unglban(client):

    # Global ban removal simulation
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.unglban"))
    async def unglobal_ban(event):

        if not event.reply_to_msg_id:
            return await event.edit(
                "❗ Reply to a user to start the unban process."
            )

        reply = await event.get_reply_message()
        user = reply.sender_id

        if user not in ban_list:
            return await event.edit(
                "❗ User is not under global ban."
            )

        ban_list.discard(user)
        ban_info.pop(user, None)

        msg = await event.edit(
            "🔄 Cancelling global ban..."
        )

        steps = [
            ("🧩 Rechecking security logs...", 15),
            ("📊 Re-evaluating activity profile...", 30),
            ("🔁 Reviewing TEMP-FREEZE status...", 45),
            ("🛡 Reconfiguring security filters...", 60),
            ("🔓 Starting ban removal process...", 80),
            ("📥 Processing authorization signal...", 95),
            ("✅ Process completed.", 100),
        ]

        for text, percent in steps:
            filled = "█" * (percent // 10)
            empty = "░" * (10 - (percent // 10))

            try:
                await msg.edit(
                    f"{text}\n\n"
                    f"[{filled}{empty}] `{percent}%`"
                )
            except Exception:
                pass

            await asyncio.sleep(1.2)

        now_time = datetime.now().strftime("%Y-%m-%d %H:%M")

        await msg.edit(
            "✅ <b>Global Ban Request Status Canceled!</b>\n\n"
            "❄️ Server Response: <code>200 OK</code>\n"
            f"👤 User ID: <code>{user}</code>\n"
            "🔓 Status: <code>Restored</code>\n"
            f"📅 Date: <code>{now_time}</code>\n\n"
            f"📌 The security system has re-evaluated the user's activity and "
            f"removed the freeze measures."
        )