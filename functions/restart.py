import os
import sys

from telethon import events


def register_restart(client):

    # Restart command
    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"\.restart"
        )
    )
    async def restart_bot(event):

        await event.edit("🔄 Restarting...")

        await client.disconnect()

        python_path = sys.executable
        script_path = os.path.abspath(sys.argv[0])

        os.execv(
            python_path,
            [python_path, script_path, *sys.argv[1:]]
        )