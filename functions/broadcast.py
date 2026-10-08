from telethon import events


def register_broadcast(client):

    # Send to all chats
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.allchat (.+)"))
    async def all_chat(event):
        text = event.pattern_match.group(1).strip()

        if not text:
            return await event.edit("❗ Please enter a message.")

        await event.edit("📤 Sending...")

        async for dialog in client.iter_dialogs():
            try:
                await client.send_message(dialog.id, text)
            except Exception:
                pass

        await event.edit("✅ Message sent to all chats!")

    # Send to private chats
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.shaxsiychat (.+)"))
    async def private_chat(event):
        text = event.pattern_match.group(1).strip()

        if not text:
            return await event.edit("❗ Please enter a message.")

        await event.edit("📤 Sending...")

        async for dialog in client.iter_dialogs():
            if dialog.is_user:
                try:
                    await client.send_message(dialog.id, text)
                except Exception:
                    pass

        await event.edit("✅ Message sent to private chats!")