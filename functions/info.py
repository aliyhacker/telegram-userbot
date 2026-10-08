from telethon import events


def register_info(client):

    # Info command
    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"\.info(?: (me|\d+))?$"
        )
    )
    async def info(event):

        try:
            argument = event.pattern_match.group(1)
            send_to_me = argument == "me"

            # Get target user
            if argument and argument != "me":
                user = await client.get_entity(int(argument))

            elif event.is_reply:
                reply = await event.get_reply_message()
                user = await reply.get_sender()

            else:
                user = await client.get_me()

            # Online/offline status
            try:
                status = (
                    "🟢 Online"
                    if user.status
                    and user.status.__class__.__name__ == "UserStatusOnline"
                    else "⚪ Offline or hidden"
                )
            except Exception:
                status = "⚪ Unknown"

            # Phone number
            try:
                phone = user.phone if hasattr(user, "phone") else "No"
            except Exception:
                phone = "No"

            bot_status = "🤖 Bot" if user.bot else "👤 User"

            text = (
                f"👤 Profile Information:\n"
                f"• 👱 First name: {user.first_name or 'No'}\n"
                f"• 👪 Last name: {user.last_name or 'No'}\n"
                f"• 🌐 Username: @{user.username or 'No'}\n"
                f"• 🆔 ID: {user.id}\n"
                f"• 🔰 Status: {status}\n"
                f"• 📱 Phone: {phone}\n"
                f"• 👁‍🗨 Type: {bot_status}"
            )

            # Saved Messages mode
            if send_to_me:
                await event.delete()
                await client.send_message("me", text)

            # Normal mode
            else:
                await event.reply(text)

        except Exception as e:
            if send_to_me:
                await client.send_message(
                    "me",
                    f"❌ Error: {e}"
                )
            else:
                await event.reply(
                    f"❌ Error: {e}"
                )