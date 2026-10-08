import subprocess
import time
import requests
from telethon import events


def register_ping(client, bot_start_time):

    # Ping and speed test
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.ping"))
    async def ping_cmd(event):
        start = time.time()
        msg = await event.edit("🛜 Pinging...")

        ping_ms = round((time.time() - start) * 1000, 2)

        await msg.edit("📡 Checking internet speed...")

        # Cloudflare ping
        try:
            ping_result = subprocess.check_output(
                "ping -c 1 1.1.1.1",
                shell=True,
                text=True,
                stderr=subprocess.STDOUT
            )

            line = next(
                line for line in ping_result.splitlines()
                if "time=" in line
            )

            cloudflare_ping = line.split("time=")[1].strip()

        except Exception:
            cloudflare_ping = "Unknown"

        # Cloudflare download speed
        try:
            test_url = "https://speed.cloudflare.com/__down?bytes=5000000"

            t1 = time.time()
            response = requests.get(test_url, timeout=20)
            response.raise_for_status()
            t2 = time.time()

            size_mb = len(response.content) / (1024 * 1024)
            seconds = t2 - t1

            download_speed = round(size_mb / seconds, 2)

        except Exception as e:
            return await msg.edit(f"❌ Download error:\n`{e}`")

        # Bot uptime
        uptime_seconds = int(time.time() - bot_start_time)

        h = uptime_seconds // 3600
        m = (uptime_seconds % 3600) // 60
        s = uptime_seconds % 60

        uptime_text = f"{h}h {m}m {s}s"

        await msg.edit(
            f"🛜 PING / SPEEDTEST\n\n"
            f"📡 Telegram Ping: `{ping_ms} ms`\n"
            f"⚡ Cloudflare Ping: `{cloudflare_ping}`\n"
            f"⬇️ Download Speed: `{download_speed} MB/s`\n"
            f"⏳ Bot uptime: `{uptime_text}`"
        )