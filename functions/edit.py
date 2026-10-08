# @aliyhacker
import asyncio
from telethon import events


def register_edit(client):

    # --------- Edit ----------
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.edit (.+)"))
    async def edit_animation(event):
        text = event.pattern_match.group(1)

        await event.edit("⬜")

        display = ""
        speed = 0.04

        for c in text:
            display += c
            try:
                await event.edit(display)
            except Exception:
                pass
            await asyncio.sleep(speed)
