import math

from telethon import events


def register_math(client):

    # Math command
    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"\.math (.+)"
        )
    )
    async def math_handler(event):

        expression = event.pattern_match.group(1)

        await event.edit("⏳ Calculating...")

        try:
            allowed = {
                "abs": abs,
                "round": round,
                "min": min,
                "max": max,
                "pow": pow,
                "sqrt": math.sqrt,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "pi": math.pi,
                "e": math.e,
            }

            result = eval(
                expression,
                {"__builtins__": {}},
                allowed
            )

            await event.edit(
                f"🧮 Answer: {result}"
            )

        except Exception as e:
            await event.edit(
                f"❌ Error: {e}"
            )