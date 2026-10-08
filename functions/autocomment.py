from telethon import events

auto_commenting = False
comment_channel = None
comment_text = ""


def register_autocomment(client):

    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"\.autocomment(?:\s+(.+))?$"
        )
    )
    async def start_autocomment(event):

        global auto_commenting
        global comment_channel
        global comment_text

        raw = event.raw_text.strip()

        parts = raw.split(" ", 2)

        if len(parts) < 3:
            return await event.edit(
                "❌ Usage:\n"
                ".autocomment <channel_username> <text>\n\n"
                "Example:\n"
                ".autocomment @mychannel Nice post!"
            )

        channel = parts[1].lstrip("@").strip()
        text = parts[2].strip()

        if not channel:
            return await event.edit(
                "❌ Channel username is required."
            )

        if not text:
            return await event.edit(
                "❌ Comment text is required."
            )

        comment_channel = channel
        comment_text = text
        auto_commenting = True

        await event.edit(
            f"✅ Auto Comment enabled.\n"
            f"📢 Channel: @{comment_channel}\n"
            f"💬 Text: {comment_text}"
        )

    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"\.commentoff$"
        )
    )
    async def stop_autocomment(event):

        global auto_commenting
        global comment_channel
        global comment_text

        auto_commenting = False
        comment_channel = None
        comment_text = ""

        await event.edit(
            "❌ Auto Comment disabled."
        )

    @client.on(events.NewMessage())
    async def auto_comment_handler(event):

        if not auto_commenting:
            return

        if not comment_channel:
            return

        # Only process channel posts
        if not event.is_channel:
            return

        # Ignore outgoing messages
        if event.out:
            return

        chat = await event.get_chat()

        username = getattr(chat, "username", None)

        if not username:
            return

        if username.lower() != comment_channel.lower():
            return

        try:
            await client.send_message(
                event.chat_id,
                comment_text,
                comment_to=event.id
            )

            print(
                f"💬 Auto comment sent to "
                f"@{username} | Post ID: {event.id}"
            )

        except Exception as e:
            print(
                f"❌ Auto comment error: {e}"
            )