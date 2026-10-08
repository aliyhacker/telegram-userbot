from telethon import events


def register_delall(client):

    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"\.del all$"
        )
    )
    async def del_all(event):

        # Only allow the command in groups
        if not event.is_group:
            return await event.edit(
                "❌ This command only works in groups."
            )

        me = await client.get_me()

        command_message_id = event.id
        message_ids = []

        # Find only messages sent by the current account
        async for message in client.iter_messages(
            event.chat_id,
            from_user=me.id
        ):
            message_ids.append(message.id)

        # Delete all own messages
        if message_ids:
            try:
                await client.delete_messages(
                    event.chat_id,
                    message_ids
                )
            except Exception as e:
                print(f"❌ Delete error: {e}")

        print(
            f"🗑 Deleted {len(message_ids)} "
            f"own messages from group {event.chat_id}"
        )