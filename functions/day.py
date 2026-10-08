from datetime import datetime
import pytz
from telethon import events
from hijridate import Gregorian
from astral import moon


# ============ City timezones ============
CITY_TIMEZONES = {
    # Uzbekistan
    "tashkent": "Asia/Tashkent",

    # Europe
    "london": "Europe/London",
    "paris": "Europe/Paris",
    "berlin": "Europe/Berlin",
    "madrid": "Europe/Madrid",
    "rome": "Europe/Rome",
    "moscow": "Europe/Moscow",
    "istanbul": "Europe/Istanbul",
    "amsterdam": "Europe/Amsterdam",
    "lisbon": "Europe/Lisbon",
    "vienna": "Europe/Vienna",

    # North America
    "washington": "America/New_York",
    "ottawa": "America/Toronto",
    "mexico city": "America/Mexico_City",

    # South America
    "brasilia": "America/Sao_Paulo",
    "buenos aires": "America/Argentina/Buenos_Aires",
    "lima": "America/Lima",
    "bogota": "America/Bogota",

    # Asia
    "tokyo": "Asia/Tokyo",
    "seoul": "Asia/Seoul",
    "beijing": "Asia/Shanghai",
    "singapore": "Asia/Singapore",
    "dubai": "Asia/Dubai",
    "delhi": "Asia/Kolkata",
    "bangkok": "Asia/Bangkok",

    # Africa
    "cairo": "Africa/Cairo",
    "pretoria": "Africa/Johannesburg",
    "nairobi": "Africa/Nairobi",

    # Australia / Oceania
    "canberra": "Australia/Sydney",
    "wellington": "Pacific/Auckland",
}


# ============ Moon phase ============
def moon_phase_name(phase):
    if phase == 0:
        return "New Moon"
    elif 0 < phase < 7:
        return "Waxing Crescent"
    elif phase == 7:
        return "First Quarter"
    elif 7 < phase < 14:
        return "Waxing Gibbous"
    elif phase == 14:
        return "Full Moon"
    elif 14 < phase < 21:
        return "Waning Gibbous"
    elif phase == 21:
        return "Last Quarter"
    else:
        return "Waning Crescent"


# ============ .day command ============
def register_day(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.day(?: |$)(.*)"))
    async def day_diagnostic(event):
        try:
            # --- Get city ---
            parts = event.text.split(maxsplit=1)

            if len(parts) > 1:
                city_input = parts[1].strip()
                city_key = city_input.lower()

                if city_key not in CITY_TIMEZONES:
                    return await event.edit(
                        f"❌ Unknown city: `{city_input}`\n\n"
                        "Example: `.day London`\n"
                        "Available cities: Tashkent, London, Paris, "
                        "Berlin, Tokyo, Seoul, Dubai..."
                    )

                city_name_display = city_input
                tz_name = CITY_TIMEZONES[city_key]

            else:
                city_name_display = "Tashkent"
                tz_name = CITY_TIMEZONES["tashkent"]

            # --- Current local time ---
            tz = pytz.timezone(tz_name)
            now = datetime.now(tz)

            # --- Gregorian date ---
            day_name = now.strftime("%A")
            month_name = now.strftime("%B")
            year = now.year
            week_num = now.isocalendar()[1]
            time_str = now.strftime("%H:%M:%S")
            day_num = now.day

            # --- Hijri date ---
            hijri_date = Gregorian(
                now.year,
                now.month,
                now.day
            ).to_hijri()

            hijri_day = hijri_date.day
            hijri_month = hijri_date.month_name()
            hijri_year = hijri_date.year

            # --- Moon phase ---
            phase = moon.phase(now.date())
            moon_phase = moon_phase_name(phase)

            # --- Result ---
            msg = (
                f"📍 <b>City:</b> <code>{city_name_display}</code>\n\n"

                f"🗓 <b>Gregorian:</b>\n"
                f"• Day: <code>{day_name}</code>\n"
                f"• Date: <code>{day_num}</code>\n"
                f"• Month: <code>{month_name}</code>\n"
                f"• Year: <code>{year}</code>\n"
                f"• Week number: <code>{week_num}</code>\n"
                f"• Time: <code>{time_str}</code>\n\n"

                f"🌙 <b>Hijri:</b>\n"
                f"• Day: <code>{hijri_day}</code>\n"
                f"• Month: <code>{hijri_month}</code>\n"
                f"• Year: <code>{hijri_year}</code>\n\n"

                f"🌔 <b>Moon phase:</b> <code>{moon_phase}</code>"
            )

            await event.edit(msg, parse_mode="html")

        except Exception as e:
            await event.edit(f"❌ Error: {e}")