import html
import pytz

from telethon import events

from functions.antidel_state import (
    antidel_groups,
    antidel_private
)

from config import LOG_CHAT_ID


emoji_map = {
    "text": "📝",
    "photo": "🖼",
    "sticker": "🔖",
    "video": "🎬",
    "document": "📄",
    "unknown": "❔"
}


def register_antidel(client):

    # AntiDel command
    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"\.antidel (on|off)"
        )
    )
    async def antidel_toggle(event):

        chat_id = event.chat_id
        command = event.pattern_match.group(1)

        if command == "on":
            antidel_groups.add(chat_id)

            await event.edit(
                "🛰 AntiDel enabled! "
                "Deleted messages will be shown."
            )

        else:
            antidel_groups.discard(chat_id)

            await event.edit(
                "🛰 AntiDel disabled."
            )

    # Private AntiDel
    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"\.antidel_private (on|off)"
        )
    )
    async def antidel_private_cmd(event):

        command = event.pattern_match.group(1)

        if command == "on":

            antidel_private.clear()
            count = 0

            async for dialog in client.iter_dialogs():

                if dialog.is_user:
                    antidel_private.add(dialog.id)
                    count += 1

            await event.edit(
                f"🛰 AntiDel enabled for private chats! "
                f"({count} chats)"
            )

        else:

            antidel_private.clear()

            await event.edit(
                "🛰 AntiDel disabled for private chats."
            )

    # Deleted message handler
    @client.on(events.MessageDeleted())
    async def deleted_message_handler(event):

        chat = event.chat_id

        if (
            chat not in antidel_groups
            and chat not in antidel_private
        ):
            return

        for msg_id in event.deleted_ids:

            try:
                deleted_msg = await client.get_messages(
                    chat,
                    ids=msg_id
                )

                if deleted_msg is None:
                    continue

            except Exception:
                continue

            # Message sender
            try:
                sender = await client.get_entity(
                    deleted_msg.sender_id
                )

                sender_name = (
                    f"{sender.first_name or ''} "
                    f"{sender.last_name or ''}"
                ).strip() or "Unknown"

            except Exception:
                sender_name = "Unknown"

            # Telegram does not provide the deleter
            deleter_name = "Unknown"

            # Chat information
            try:
                chat_entity = await client.get_entity(chat)

                if getattr(chat_entity, "title", None):

                    chat_name = chat_entity.title

                    if getattr(
                        chat_entity,
                        "username",
                        None
                    ):
                        chat_link = (
                            f"https://t.me/"
                            f"{chat_entity.username}"
                        )
                    else:
                        chat_link = "None"

                    chat_type = "Group/Channel"

                else:

                    chat_name = (
                        f"{chat_entity.first_name or ''} "
                        f"{chat_entity.last_name or ''}"
                    ).strip() or "Unknown"

                    chat_link = "Private chat"
                    chat_type = "Private chat"

            except Exception:

                chat_name = "Unknown"
                chat_link = "Unknown"
                chat_type = "Unknown"

            # Message content
            if deleted_msg.message:

                content_type = "text"

                safe_text = html.escape(
                    deleted_msg.message
                )

                content = f"<code>{safe_text}</code>"

            elif deleted_msg.media:

                if getattr(deleted_msg, "photo", None):
                    content_type = "photo"
                    content = "Photo deleted."

                elif getattr(deleted_msg, "video", None):
                    content_type = "video"
                    content = "Video deleted."

                elif getattr(deleted_msg, "document", None):
                    content_type = "document"
                    content = "File deleted."

                elif getattr(deleted_msg, "sticker", None):
                    content_type = "sticker"
                    content = "Sticker deleted."

                else:
                    content_type = "unknown"
                    content = "Unknown message type deleted."

            else:

                content_type = "unknown"
                content = "Unknown message type deleted."

            # Message time
            try:

                time_str = (
                    deleted_msg.date
                    .astimezone(
                        pytz.timezone("Asia/Tashkent")
                    )
                    .strftime("%Y-%m-%d %H:%M:%S")
                )

            except Exception:

                time_str = "Unknown"

            # Send deletion log
            try:

                await client.send_message(
                    LOG_CHAT_ID,
                    (
                        f"🚨 <b>Message deleted!</b>\n"
                        f"👤 <b>Sender:</b> "
                        f"{html.escape(sender_name)}\n"
                        f"🗑 <b>Deleted by:</b> "
                        f"{html.escape(deleter_name)}\n"
                        f"📌 <b>Message ID:</b> {msg_id}\n"
                        f"🕒 <b>Date:</b> {time_str}\n"
                        f"💬 <b>Chat:</b> "
                        f"{html.escape(chat_name)}\n"
                        f"🔗 <b>Link:</b> {chat_link}\n"
                        f"📂 <b>Type:</b> {chat_type}\n"
                        f"{emoji_map.get(content_type, '❔')} "
                        f"{content}"
                    ),
                    parse_mode="html",
                    link_preview=False
                )

            except Exception:
                pass

    # AntiDel for all chats
    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"\.antidel_all (on|off)"
        )
    )
    async def antidel_all(event):

        command = event.pattern_match.group(1)

        if command == "on":

            antidel_groups.clear()
            count = 0

            async for dialog in client.iter_dialogs():

                if (
                    dialog.is_group
                    or dialog.is_channel
                    or dialog.is_user
                ):
                    antidel_groups.add(dialog.id)
                    count += 1

            await event.edit(
                f"🛰 AntiDel enabled for all chats! "
                f"({count} chats)"
            )

        else:

            antidel_groups.clear()

            await event.edit(
                "🛰 AntiDel disabled for all chats."
            )