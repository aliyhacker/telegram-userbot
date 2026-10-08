from telethon import events, types


def register_chatinfo(client):

    # Chat info command
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.chatinfo(?: (me))?$"))
    async def chat_info(event):
        send_to_me = event.pattern_match.group(1) == "me"

        try:
            chat = await event.get_chat()

            title = (
                getattr(chat, "title", None)
                or getattr(chat, "first_name", None)
                or "Unknown"
            )

            text = (
                f"💬 <b>Chat Information:</b>\n"
                f"• 🔖 <b>Name:</b> {title}\n"
                f"• 🆔 <b>ID:</b> {chat.id}\n"
            )

            # Members count
            participants_count = getattr(
                chat, "participants_count", None
            )

            if participants_count is not None:
                text += f"• 🧮 <b>Members:</b> {participants_count}\n"

            # Chat type
            if getattr(chat, "broadcast", False):
                chat_type = "Channel"
            elif getattr(chat, "megagroup", False):
                chat_type = "Supergroup"
            else:
                chat_type = "Group"

            text += f"• 🔐 <b>Type:</b> {chat_type}\n"

            # Username link
            username = getattr(chat, "username", None)

            if username:
                text += f"• 🔗 <b>Link:</b> https://t.me/{username}\n"
            else:
                text += "• 🔗 <b>Link:</b> None\n"

            # Admin count
            if not getattr(chat, "broadcast", False):
                try:
                    admins = [
                        admin async for admin in client.iter_participants(
                            chat.id,
                            filter=types.ChannelParticipantsAdmins
                        )
                    ]

                    text += f"• 👑 <b>Admins:</b> {len(admins)}\n"

                except Exception:
                    text += "• 👑 <b>Admins:</b> Unknown\n"

            # Saved Messages mode
            if send_to_me:
                await event.delete()
                await client.send_message(
                    "me",
                    text,
                    parse_mode="html"
                )

            # Normal mode
            else:
                await event.reply(
                    text,
                    parse_mode="html"
                )
        except Exception as e:
            if send_to_me:
                await client.send_message(
                    "me",
                    f"❌ Chat info error:\n{e}"
                )
            else:
                await event.reply(
                    f"❌ Error: {e}"
                )