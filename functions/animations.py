import asyncio
from telethon import events


def register_animations(client):

    # ============ .snow ============
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.snow$"))
    async def snow_command(event):
        """Snow animation."""

        snow_frames = [
            "☁️🌨☁️🌨☁️🌨☁️🌨☁️🌨☁️\n\n\n\n\n\n"
            "⛄️☃️⛄️☃️⛄️☃️⛄️☃️⛄️☃️⛄️",

            "☁️🌨☁️🌨☁️🌨☁️🌨☁️🌨☁️\n"
            "    ❄️    ❄️     ❄️     ❄️     ❄️   ❄️\n\n\n\n\n"
            "⛄️☃️⛄️☃️⛄️☃️⛄️☃️⛄️☃️⛄️",

            "☁️🌨☁️🌨☁️🌨☁️🌨☁️🌨☁️\n"
            "    ❄️    ❄️     ❄️     ❄️     ❄️   ❄️\n"
            "❄️    ❄️    ❄️    ❄️    ❄️    ❄️\n\n\n\n"
            "⛄️☃️⛄️☃️⛄️☃️⛄️☃️⛄️☃️⛄️",

            "☁️🌨☁️🌨☁️🌨☁️🌨☁️🌨☁️\n"
            "    ❄️    ❄️     ❄️     ❄️     ❄️   ❄️\n"
            "❄️    ❄️    ❄️    ❄️    ❄️    ❄️\n"
            "    ❄️    ❄️    ❄️    ❄️    ❄️    ❄️\n\n\n"
            "⛄️☃️⛄️☃️⛄️☃️⛄️☃️⛄️☃️⛄️",

            "☁️🌨☁️🌨☁️🌨☁️🌨☁️🌨☁️\n"
            "    ❄️    ❄️     ❄️     ❄️     ❄️   ❄️\n"
            "❄️    ❄️    ❄️    ❄️    ❄️    ❄️\n"
            "    ❄️    ❄️    ❄️    ❄️    ❄️    ❄️\n"
            "❄️    ❄️    ❄️    ❄️    ❄️    ❄️\n\n"
            "⛄️☃️⛄️☃️⛄️☃️⛄️☃️⛄️☃️⛄️",

            "☁️🌨☁️🌨☁️🌨☁️🌨☁️🌨☁️\n"
            "    ❄️    ❄️     ❄️     ❄️     ❄️   ❄️\n"
            "❄️    ❄️    ❄️    ❄️    ❄️    ❄️\n"
            "    ❄️    ❄️    ❄️    ❄️    ❄️    ❄️\n"
            "❄️    ❄️    ❄️    ❄️    ❄️    ❄️\n"
            "  ❄️      ❄️    ❄️  ❄️      ❄️  ❄️\n"
            "⛄️☃️⛄️☃️⛄️☃️⛄️☃️⛄️☃️⛄️"
        ]

        for frame in snow_frames:
            await event.edit(frame)
            await asyncio.sleep(0.5)


    # ============ .police ============
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.police$"))
    async def police_command(event):
        """Police lights animation."""

        police_frames = [
            "🔴🔴🔴⬜️⬜️⬜️🔵🔵🔵\n"
            "🔴🔴🔴⬜️⬜️⬜️🔵🔵🔵\n"
            "🔴🔴🔴⬜️⬜️⬜️🔵🔵🔵",

            "🔵🔵🔵⬜️⬜️⬜️🔴🔴🔴\n"
            "🔵🔵🔵⬜️⬜️⬜️🔴🔴🔴\n"
            "🔵🔵🔵⬜️⬜️⬜️🔴🔴🔴"
        ]

        for _ in range(4):
            for frame in police_frames:
                await event.edit(frame)
                await asyncio.sleep(0.6)


    # ============ .love ============
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.love$"))
    async def love_command(event):
        """Heart animation."""

        hearts = [
            "❤️",
            "🧡",
            "💛",
            "💚",
            "💙",
            "💜",
            "🤎",
            "🖤",
            "💖"
        ]

        heart_frames = [
            "💖",

            "💖\n💖",

            "💖💖\n💖",

            "💖💖💖\n💖💖\n💖",

            " 💖💖💖 \n"
            "💖💖💖💖\n"
            " 💖💖💖 \n"
            "  💖💖  \n"
            "   💖   ",

            "  💖💖💖  \n"
            " 💖💖💖💖💖 \n"
            "💖💖💖💖💖💖\n"
            " 💖💖💖💖💖 \n"
            "  💖💖💖  \n"
            "   💖💖   \n"
            "    💖    "
        ]

        for frame in heart_frames:
            await event.edit(frame)
            await asyncio.sleep(0.5)

        for heart in hearts:
            colored_frame = heart_frames[-1].replace("💖", heart)
            await event.edit(colored_frame)
            await asyncio.sleep(0.3)

        await event.edit("💝 There is love here, but not for you! 💝")