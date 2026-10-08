import asyncio
from datetime import datetime, timedelta

from telethon import events, functions


circle_map = {
    "0": "⓿",
    "1": "❶",
    "2": "❷",
    "3": "❸",
    "4": "❹",
    "5": "❺",
    "6": "❻",
    "7": "❼",
    "8": "❽",
    "9": "❾",
    ":": ":",
}


def to_circle(text):
    return "".join(circle_map.get(ch, ch) for ch in text)


async def update_profile_time(client, tz, get_clock_state, set_clock_state):
    while get_clock_state():
        current_time = datetime.now(tz)
        time_str = current_time.strftime("%H:%M")
        beautiful_time = to_circle(time_str)

        new_name = f"무하마드 알리⁵⁷¹ {beautiful_time}"

        try:
            await client(
                functions.account.UpdateProfileRequest(
                    first_name=new_name
                )
            )
            print("Profile updated:", new_name)

        except Exception as e:
            print("Error:", e)

        current_time = datetime.now(tz)

        next_minute = (
            current_time + timedelta(minutes=1)
        ).replace(second=0, microsecond=0)

        wait_time = (next_minute - current_time).total_seconds()

        await asyncio.sleep(wait_time)


def register_profile_clock(client, tz, get_clock_state, set_clock_state):

    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"\.clock (on|off)"
        )
    )
    async def profile_clock_handler(event):

        cmd = event.pattern_match.group(1)

        if cmd == "on":

            if not get_clock_state():

                set_clock_state(True)

                asyncio.create_task(
                    update_profile_time(
                        client,
                        tz,
                        get_clock_state,
                        set_clock_state
                    )
                )

                await event.edit(
                    "⏰ Profile clock enabled!"
                )

            else:
                await event.edit(
                    "❗ Profile clock is already enabled."
                )

        else:

            set_clock_state(False)

            await event.edit(
                "⏰ Profile clock disabled."
            )