import asyncio

from telethon import events


def register_whatsup(client):

    # Whatsup animation
    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"\.whatsup"
        )
    )
    async def whatsup(event):

        msg = event.message

        frames = [
            "💎 What's up 💎",
            "💫 What's up 💫",
            "⚡️ What's up ⚡️",
            "✨ What's up ✨",
            "⚜ What's up ⚜",
            "🔥 What's up 🔥",
            "💎 What's up 💎",
            "💫 What's up 💫",
            "⚡️ What's up ⚡️",
            "✨ What's up ✨",
            "⚜ What's up ⚜",
            "🔥 What's up 🔥"
        ]

        for frame in frames:

            try:
                await msg.edit(frame)
            except Exception:
                pass

            await asyncio.sleep(0.6)