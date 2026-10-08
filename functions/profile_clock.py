# @aliyhacker
import asyncio
import json
import os
import re
from datetime import datetime, timedelta

from telethon import events, functions


STATE_FILE = "profile_clock_state.json"


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


def load_clock_state():
    if not os.path.exists(STATE_FILE):
        return {
            "enabled": False,
            "original_last_name": None
        }

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {
            "enabled": False,
            "original_last_name": None
        }


def save_clock_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as file:
        json.dump(state, file, ensure_ascii=False, indent=2)


def remove_clock(last_name):
    if not last_name:
        return ""

    # Remove our clock from the end of the last name.
    pattern = r"\s+[⓿❶❷❸❹❺❻❼❽❾]{2}:[⓿❶❷❸❹❺❻❼❽❾]{2}$"

    cleaned = re.sub(pattern, "", last_name)
    return cleaned.strip()


async def update_profile_time(
    client,
    tz,
    get_clock_state,
    set_clock_state
):
    while get_clock_state():

        state = load_clock_state()
        original_last_name = state.get("original_last_name")

        current_time = datetime.now(tz)
        time_str = current_time.strftime("%H:%M")
        beautiful_time = to_circle(time_str)

        if original_last_name:
            new_last_name = f"{original_last_name} {beautiful_time}"
        else:
            new_last_name = beautiful_time

        try:
            await client(
                functions.account.UpdateProfileRequest(
                    last_name=new_last_name
                )
            )

            print("Profile clock updated:", new_last_name)

        except Exception as e:
            print("Error:", e)

        current_time = datetime.now(tz)

        next_minute = (
            current_time + timedelta(minutes=1)
        ).replace(second=0, microsecond=0)

        wait_time = (
            next_minute - current_time
        ).total_seconds()

        await asyncio.sleep(wait_time)


def register_profile_clock(
    client,
    tz,
    get_clock_state,
    set_clock_state
):

    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"\.clock (on|off)"
        )
    )
    async def profile_clock_handler(event):

        cmd = event.pattern_match.group(1)

        if cmd == "on":

            if get_clock_state():
                return await event.edit(
                    "❗ Profile clock is already enabled."
                )

            me = await client.get_me()

            # Save the original last name only once.
            state = load_clock_state()

            if state.get("original_last_name") is None:
                original_last_name = me.last_name or ""

                state["original_last_name"] = remove_clock(
                    original_last_name
                )

            state["enabled"] = True
            save_clock_state(state)

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

            state = load_clock_state()
            original_last_name = state.get(
                "original_last_name"
            )

            set_clock_state(False)

            state["enabled"] = False
            save_clock_state(state)

            try:
                await client(
                    functions.account.UpdateProfileRequest(
                        last_name=original_last_name or ""
                    )
                )

                print(
                    "Profile clock disabled. "
                    "Original last name restored."
                )

            except Exception as e:
                print("Error restoring profile:", e)

            await event.edit(
                "⏰ Profile clock disabled."
            )

    # Restore clock automatically after restart.
    state = load_clock_state()

    if state.get("enabled"):

        set_clock_state(True)

        asyncio.create_task(
            update_profile_time(
                client,
                tz,
                get_clock_state,
                set_clock_state
            )
        )
