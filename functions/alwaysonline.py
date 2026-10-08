import asyncio

from telethon import events, functions


online_enabled = False
online_task = None


async def keep_online(client):
    """Keep the Telegram account online."""

    while online_enabled:
        try:
            await client(
                functions.account.UpdateStatusRequest(
                    offline=False
                )
            )

            print("🟢 Always Online: enabled")

        except Exception as e:
            print(f"❌ Always Online error: {e}")

        await asyncio.sleep(60)


def register_always_online(client):

    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"\.online (on|off)$"
        )
    )
    async def online_command(event):

        global online_enabled
        global online_task

        mode = event.pattern_match.group(1)

        if mode == "on":

            if online_enabled:
                return await event.edit(
                    "🟢 Always Online is already enabled."
                )

            online_enabled = True

            online_task = asyncio.create_task(
                keep_online(client)
            )

            await event.edit(
                "🟢 Always Online enabled."
            )

        else:

            if not online_enabled:
                return await event.edit(
                    "🔴 Always Online is already disabled."
                )

            online_enabled = False

            if online_task:
                online_task.cancel()
                online_task = None

            try:
                await client(
                    functions.account.UpdateStatusRequest(
                        offline=True
                    )
                )
            except Exception as e:
                print(
                    f"❌ Failed to update offline status: {e}"
                )

            await event.edit(
                "🔴 Always Online disabled."
            )