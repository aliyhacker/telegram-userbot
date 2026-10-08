import asyncio
from datetime import datetime, timedelta
from telethon import events

from functions.ban_state import ban_list, ban_info


def register_glban(client):

    # Global ban simulation
    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"\.glban"
        )
    )
    async def global_ban(event):

        if not event.reply_to_msg_id:
            return await event.edit(
                "❗ Reply to a user to start a global ban."
            )

        reply = await event.get_reply_message()
        user = reply.sender_id

        # Already banned
        if user in ban_list:
            return await event.edit(
                "❗ User is already under global ban."
            )

        ban_list.add(user)

        msg = await event.edit(
            "⛔ Checking user..."
        )

        steps = [
            ("🔍 Analyzing profile activity...", 10),
            ("📡 Processing security request...", 25),
            ("🔐 Checking permission levels...", 40),
            ("⚠️ Running security filters...", 55),
            ("🚧 Security protection activated...", 70),
            ("🛑 Starting freeze process...", 85),
            ("📁 Preparing security report...", 95),
            ("🔒 Finalizing action...", 100),
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

            await asyncio.sleep(0.5)

        await asyncio.sleep(1.4)

        # Calculate scheduled freeze time
        frozen_date = (
            datetime.now() + timedelta(days=3)
        ).strftime("%Y-%m-%d %H:%M")

        now_time = datetime.now().strftime(
            "%Y-%m-%d %H:%M"
        )

        ban_info[user] = {
            "process_time": now_time,
            "frozen_time": frozen_date,
            "status": "Global Ban",
            "server_response": "207 TEMP-FREEZE",
            "note": (
                "Account is under monitoring and "
                "temporary freeze has been scheduled."
            ),
        }

        final_text = (
            "🚫 <b>Global Ban Request Submitted!</b>\n\n"
            f"🌐 Server Response: <code>202 ACCEPTED</code>\n"
            f"👤 User ID: <code>{user}</code>\n"
            f"📅 Process Time: <code>{now_time}</code>\n"
            f"🔒 Status: <code>TEMP-FREEZE</code>\n"
            f"❄ Scheduled Freeze: <code>{frozen_date}</code>\n"
            "🛡 Account is currently under monitoring "
            "and a temporary freeze has been scheduled.\n"
            "❗ This ban is applied by an automatic security system."
        )

        await msg.edit(
            final_text,
            parse_mode="html"
        )