from telethon import events, types


def register_staff(client):

    # Group staff list
    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"\.staff(?: (me))?$"
        )
    )
    async def staff_list(event):

        send_to_me = (
            event.pattern_match.group(1) == "me"
        )

        if not event.is_group:
            if send_to_me:
                await event.delete()
                return await client.send_message(
                    "me",
                    "❗ The .staff command can only be used in groups."
                )

            return await event.edit(
                "❗ The .staff command can only be used in groups."
            )

        creators = []
        admins = []

        try:
            async for participant in client.iter_participants(
                event.chat_id
            ):
                participant_data = participant.participant

                # Group creator
                if isinstance(
                    participant_data,
                    types.ChannelParticipantCreator
                ):
                    creators.append(participant)

                # Group administrator
                elif isinstance(
                    participant_data,
                    types.ChannelParticipantAdmin
                ):
                    admins.append(participant)

        except Exception as e:
            error_text = (
                f"❌ Failed to get staff list:\n{e}"
            )

            if send_to_me:
                await event.delete()
                return await client.send_message(
                    "me",
                    error_text
                )

            return await event.edit(error_text)

        text = "📌 <b>GROUP STAFF</b>\n\n"

        # Creator
        if creators:
            text += "👑 <b>Creator</b>\n"

            for user in creators:
                display_name = (
                    f"@{user.username}"
                    if user.username
                    else str(user.id)
                )

                first_name = (
                    user.first_name
                    or "Unknown"
                )

                text += (
                    f" └ {display_name} » "
                    f"{first_name}\n"
                )

            text += "\n"

        # Administrators
        if admins:
            text += "👮 <b>Administrators</b>\n"

            for user in admins:
                display_name = (
                    f"@{user.username}"
                    if user.username
                    else str(user.id)
                )

                text += (
                    f" ├ {display_name} » "
                    f"{user.id}\n"
                )

        if not creators and not admins:
            text += "No administrators found."

        # Send result to Saved Messages
        if send_to_me:
            await event.delete()

            await client.send_message(
                "me",
                text,
                parse_mode="html"
            )

        # Show result in current group
        else:
            await event.edit(
                text,
                parse_mode="html"
            )