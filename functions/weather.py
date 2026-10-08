import requests
from telethon import events
from config import OPENWEATHER_API_KEY


# ============ Air pollution level ============
def dust_level(pm2_5):
    if pm2_5 <= 12:
        return "Clean 🌿"
    elif pm2_5 <= 35.4:
        return "Good 🙂"
    elif pm2_5 <= 55.4:
        return "Moderate 😐"
    elif pm2_5 <= 150.4:
        return "Polluted 🌫️"
    elif pm2_5 <= 250.4:
        return "Very polluted ⚠️"
    else:
        return "Hazardous ☠️"


# ============ Wind speed ============
def wind_level(speed):
    if speed < 3:
        return "Light 🍃"
    elif speed < 7:
        return "Moderate 💨"
    else:
        return "Strong 🌬️"


# ============ Wind direction ============
def wind_direction(deg):
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    index = int((deg + 22.5) / 45) % 8
    return directions[index]


# ============ .weather command ============
def register_weather(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.weather (.+)"))
    async def get_weather(event):
        city_name = event.pattern_match.group(1).strip()

        if not city_name:
            return await event.edit(
                "❗ Please enter a city name: `.weather Tashkent`"
            )

        try:
            # --- Current weather ---
            weather_url = (
                "https://api.openweathermap.org/data/2.5/weather"
                f"?q={city_name}&appid={OPENWEATHER_API_KEY}&units=metric"
            )

            resp = requests.get(weather_url, timeout=15)

            if resp.status_code != 200:
                return await event.edit(
                    f"❌ API error: {resp.status_code}\n{resp.text[:200]}"
                )

            try:
                data = resp.json()
            except Exception:
                return await event.edit("❌ Invalid API JSON response.")

            if "weather" not in data:
                return await event.edit("❌ City not found!")

            # --- Main weather data ---
            weather_main = data["weather"][0]["main"]
            weather_desc = data["weather"][0]["description"].capitalize()

            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            pressure = data["main"]["pressure"]

            wind_speed = data["wind"]["speed"]
            wind_deg = data["wind"].get("deg", 0)

            visibility = data.get("visibility", 0)
            country = data["sys"]["country"]

            # --- Rain ---
            rain = 0

            if "rain" in data:
                rain = (
                    data["rain"].get("1h")
                    or data["rain"].get("3h")
                    or 0
                )

            # --- Snow ---
            snow = 0

            if "snow" in data:
                snow = (
                    data["snow"].get("1h")
                    or data["snow"].get("3h")
                    or 0
                )

            # --- Geocoding ---
            geo_url = (
                "https://api.openweathermap.org/geo/1.0/direct"
                f"?q={city_name}&limit=1&appid={OPENWEATHER_API_KEY}"
            )

            geo_resp = requests.get(geo_url, timeout=15)

            if geo_resp.status_code != 200:
                return await event.edit("❌ Geocoding API error!")

            try:
                geo_res = geo_resp.json()
            except Exception:
                return await event.edit("❌ Invalid geocoding JSON response.")

            if not geo_res:
                return await event.edit("❌ City not found.")

            lat = geo_res[0]["lat"]
            lon = geo_res[0]["lon"]

            # --- Weather translation ---
            weather_translate = {
                "Clear": "Clear",
                "Clouds": "Cloudy",
                "Rain": "Rain",
                "Drizzle": "Light rain",
                "Thunderstorm": "Thunderstorm",
                "Snow": "Snow",
                "Mist": "Mist",
                "Fog": "Fog",
                "Haze": "Haze",
                "Smoke": "Smoke",
                "Dust": "Dust",
                "Sand": "Sandstorm",
            }

            weather_main_en = weather_translate.get(
                weather_main,
                weather_main
            )

            # --- Weather emoji ---
            weather_emoji = {
                "Clear": "☀️",
                "Clouds": "☁️",
                "Rain": "🌧",
                "Drizzle": "🌦",
                "Thunderstorm": "⛈",
                "Snow": "❄️",
                "Mist": "🌫",
                "Fog": "🌫",
                "Haze": "🌫",
                "Smoke": "🌫",
                "Dust": "🌫",
            }

            emoji = weather_emoji.get(weather_main, "")

            # --- Air pollution ---
            pollution_url = (
                "https://api.openweathermap.org/data/2.5/air_pollution"
                f"?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
            )

            poll_resp = requests.get(pollution_url, timeout=15)

            if poll_resp.status_code != 200:
                return await event.edit("❌ Air pollution API error!")

            try:
                poll_res = poll_resp.json()
            except Exception:
                return await event.edit(
                    "❌ Invalid air pollution JSON response."
                )

            pm2_5 = poll_res["list"][0]["components"].get("pm2_5", 0)
            pm10 = poll_res["list"][0]["components"].get("pm10", 0)
            aqi = poll_res["list"][0]["main"].get("aqi", 0)

            # --- Result message ---
            msg = (
                f"{emoji} <b>Weather Information: {city_name}, {country}</b>\n"
                f"➖➖➖➖➖➖➖➖➖➖\n"
                f"☁️ <b>Condition:</b> {weather_main_en} ({weather_desc})\n"
                f"🌡 <b>Temperature:</b> {temp}°C\n"
                f"🤗 <b>Feels like:</b> {feels_like}°C\n"
                f"💧 <b>Humidity:</b> {humidity}%\n"
                f"🔵 <b>Pressure:</b> {pressure} hPa\n"
                f"💨 <b>Wind:</b> {wind_speed} m/s "
                f"({wind_direction(wind_deg)}, {wind_level(wind_speed)})\n"
                f"👁️ <b>Visibility:</b> {visibility / 1000:.1f} km\n"
                f"🌧 <b>Rain:</b> {rain} mm\n"
                f"❄️ <b>Snow:</b> {snow} mm\n"
                f"🌫 <b>Air pollution:</b> "
                f"{dust_level(pm2_5)} "
                f"(PM2.5: {pm2_5} µg/m³, PM10: {pm10} µg/m³)\n"
                f"⚠️ <b>Air Quality (AQI):</b> {aqi}"
            )

            await event.edit(msg, parse_mode="html")

        except Exception as e:
            await event.edit(f"❌ Error: {e}")