from telethon import events

from functions.ban_state import ban_list, ban_info


def register_banlist(client):

    # Ban list command
    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"\.banlist(?: (\d+))?"
        )
    )
    async def show_banlist(event):
        user_id = event.pattern_match.group(1)

        if user_id:
            user_id = int(user_id)

            if user_id in ban_list:
                info = ban_info.get(user_id, {})

                text = (
                    f"🚫 Global Ban request submitted!\n\n"
                    f"🌐 Server Response: "
                    f"`{info.get('server_response', 'N/A')}`\n"
                    f"👤 User ID: `{user_id}`\n"
                    f"📅 Process Date: "
                    f"`{info.get('process_time', 'N/A')}`\n"
                    f"🔒 Status: `{info.get('status', 'N/A')}`\n"
                    f"❄ Scheduled Freeze Time: "
                    f"`{info.get('frozen_time', 'N/A')}`\n"
                    f"🛡 Note: {info.get('note', 'N/A')}"
                )

            else:
                text = (
                    f"❌ User `{user_id}` is not "
                    f"in the global ban list."
                )

            return await event.edit(text)

        # Show all banned users
        if not ban_list:
            return await event.reply(
                "✅ There are no globally banned users."
            )

        text = (
            "🗃 Global Security Database — Sync: `OK`\n"
            "📌 Security monitoring for your server:\n\n"
        )

        for uid in ban_list:
            text += f"🆔 `{uid}`\n"

        text += (
            "\n⚠ This list is regularly processed "
            "by the security system.\n"
            "🔄 Data is under continuous monitoring."
        )

        await event.reply(text)