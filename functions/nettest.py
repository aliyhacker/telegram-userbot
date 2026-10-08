import os
import time
import requests
from telethon import events


def register_nettest(client):

    # Network test
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.nettest"))
    async def nettest(event):
        msg = await event.edit("📡 Checking internet...")

        # Safe ping
        def soft_ping(ip):
            try:
                t1 = time.time()
                requests.get(f"http://{ip}", timeout=2)
                t2 = time.time()
                return f"{round((t2 - t1) * 1000, 2)} ms"
            except Exception:
                return "Disconnected"

        # Cloudflare ping
        cf_ping = soft_ping("1.1.1.1")

        # Google ping
        google_ping = soft_ping("8.8.8.8")

        # Download speed
        try:
            test_url = "https://speed.cloudflare.com/__down?bytes=5000000"

            t1 = time.time()
            response = requests.get(test_url, timeout=20)
            t2 = time.time()

            size_mb = len(response.content) / (1024 * 1024)
            download_speed = f"{round(size_mb / (t2 - t1), 2)} MB/s"

        except Exception:
            download_speed = "Error"

        # Upload speed
        try:
            data = os.urandom(1024 * 1024)

            t1 = time.time()
            requests.post(
                "https://speed.cloudflare.com/__up",
                data=data,
                timeout=20
            )
            t2 = time.time()

            upload_speed = f"{round(1 / (t2 - t1), 2)} MB/s"

        except Exception:
            upload_speed = "Error"

        # IP and location
        try:
            ipinfo = requests.get(
                "https://ipinfo.io/json",
                timeout=10
            ).json()

            ip = ipinfo.get("ip", "Unknown")
            country = ipinfo.get("country", "Unknown")
            isp = ipinfo.get("org", "Unknown")

        except Exception:
            ip = country = isp = "Unknown"

        # Network type
        network_type = "🌐 Internet active"

        # Signal strength
        signal = "Unknown"

        # Result
        await msg.edit(
            f"📶 Internet Diagnostics\n\n"
            f"🌐 IP: `{ip}`\n"
            f"🌍 Country: `{country}`\n"
            f"🏢 ISP: `{isp}`\n"
            f"📱 Network type: {network_type}\n"
            f"📡 Signal strength: `{signal}`\n\n"
            f"⚡ Cloudflare Ping: `{cf_ping}`\n"
            f"⚡ Google Ping: `{google_ping}`\n"
            f"⬇️ Download: `{download_speed}`\n"
            f"⬆️ Upload: `{upload_speed}`"
        )