# @aliyhacker
import asyncio
from telethon import events


def register_hack(client):

    # Hack
    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"\.hack(?: (.+))?$"
        )
    )
    async def hack(event):

        target_arg = event.pattern_match.group(1)

        try:
            # Get target from reply
            if event.is_reply and not target_arg:
                reply = await event.get_reply_message()
                user = await reply.get_sender()

                if not user:
                    return await event.edit(
                        "❌ Target not found."
                    )

            # Get target from username or ID
            elif target_arg:
                target = target_arg.strip()

                if target.startswith("@"):
                    target = target[1:]

                try:
                    if target.isdigit():
                        user = await client.get_entity(
                            int(target)
                        )
                    else:
                        user = await client.get_entity(
                            target
                        )

                except Exception:
                    return await event.edit(
                        "❌ User not found."
                    )

            else:
                return await event.edit(
                    "❗ Use `.hack @username`, `.hack ID`, "
                    "or reply to a user with `.hack`."
                )

            # Target name
            target_name = (
                f"{user.first_name or ''} "
                f"{user.last_name or ''}"
            ).strip() or "Unknown"

            # Telegram profile link
            target_link = f"tg://user?id={user.id}"

            msg = await event.edit(
                "💻 Starting hack..."
            )

            # Simulation steps
            steps = [
                "🔍 Scanning system...",
                "📡 Connecting to secure server...",
                "🔑 Checking firewall...",
                "🛜 Establishing encrypted tunnel...",
                "📁 Searching simulated files...",
                "⚠️ Processing data...",
                "📊 Finalizing..."
            ]

            for step in steps:
                try:
                    await msg.edit(step)
                except Exception:
                    pass

                await asyncio.sleep(0.5)

            # Progress bar
            for i in range(1, 11):
                filled = "▰" * i
                empty = "▱" * (10 - i)
                percent = i * 10

                try:
                    await msg.edit(
                        f"💻 Hacking...\n\n"
                        f"{filled}{empty} {percent}%"
                    )
                except Exception:
                    pass

                await asyncio.sleep(0.4)

            # Clickable target
            target_display = (
                f'<a href="{target_link}">'
                f'{target_name}'
                f'</a>'
            )

            # Final result
            await msg.edit(
                f"💻 <b>HACKING COMPLETE</b>\n\n"
                f"🎯 Target: {target_display}\n"
                f"📁 Files discovered: <code>17</code>\n"
                f"📦 Data extracted: <code>2.4 MB</code>\n"
                f"🔐 Encryption: <code>AES-256</code>\n"
                f"🧪 Session: <code>SESSION OBTAINED</code>\n"
                f"🟢 Status: <code>SUCCESS</code>",
                parse_mode="html"
            )

        except Exception as e:
            await event.edit(
                f"❌ Error: {e}"
            )