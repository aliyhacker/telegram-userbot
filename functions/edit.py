# @aliyhacker
import asyncio
from telethon import events


def register_edit(client):

    # Edit animation
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.edit (.+)"))
    async def edit_animation(event):
        text = event.pattern_match.group(1)

        await event.edit("⬜")
        await asyncio.sleep(0.1)

        display = ""
        speed = 0.04

        for char in text:
            display += char
            try:
                await event.edit(display + "░")
            except Exception:
                pass
            await asyncio.sleep(speed)