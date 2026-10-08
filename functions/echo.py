from telethon import events

from functions.echo_state import echo_groups


def register_echo(client):

    # Echo command
    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"\.echo (on|off)"
        )
    )
    async def echo_command(event):

        chat_id = event.chat_id
        command = event.pattern_match.group(1)

        if command == "on":
            echo_groups.add(chat_id)
            await event.edit("🔁 Echo mode ENABLED!")

        else:
            echo_groups.discard(chat_id)
            await event.edit("🔇 Echo mode DISABLED!")

    # Echo handler
    @client.on(events.NewMessage(incoming=True))
    async def echo_handler(event):

        if event.chat_id in echo_groups:
            if not event.out:
                await event.reply(event.text)