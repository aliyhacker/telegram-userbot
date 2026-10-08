# @aliyhacker
from telethon import events
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
import textwrap
import tempfile
from pathlib import Path
from datetime import datetime
from bidi.algorithm import get_display

from config import ALLOWED_USERS

# Telegram Dark-Style Sticker

BASE_DIR = Path(__file__).resolve().parent.parent
FONT_REG = BASE_DIR / "font" / "NotoSerifCJK.ttc"
FONT_BOLD = FONT_REG


def fix_ar(text):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


def register_stik(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.stik"))
    async def stik_handler(event):

        # Ignore unauthorized users
        if event.sender_id not in ALLOWED_USERS:
            return

        await make_real_telegram_stik(event)


async def make_real_telegram_stik(event):
    try:
        await event.delete()
    except Exception:
        pass

    cmd = event.raw_text[len(".stik"):].strip()

    user = None
    name = "Jallodbek"

    
    if event.is_reply:
        reply_message = await event.get_reply_message()

        try:
            user = await event.client.get_entity(reply_message.sender_id)
        except Exception:
            user = None

        if not cmd:
            text = reply_message.raw_text or ""
        else:
            text = cmd

    
    else:
        if not cmd:
            return await event.reply("❗ Please enter some text.")

        target = None
        text = cmd

        parts = cmd.rsplit(" ", 1)

        if len(parts) == 2:
            last = parts[1]

            if last.startswith("@") or last.isdigit():
                target = last
                text = parts[0]

        
        if target:
            try:
                if target.isdigit():
                    user = await event.client.get_entity(int(target))
                else:
                    user = await event.client.get_entity(target)
            except Exception:
                user = None

        # Use current account if no target was specified
        if user is None:
            user = await event.client.get_me()

    
    text = fix_ar(text)

    
    if user:
        name = (
            (user.first_name or "")
            + (" " + user.last_name if user.last_name else "")
        ).strip()

        if not name:
            name = user.username or "Jallodbek"

    current_time = datetime.now().strftime("%H:%M")

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)

        avatar_path = td / "avatar.jpg"
        final_path = td / "final.webp"

        
        if user:
            avatar_downloaded = await event.client.download_profile_photo(
                user,
                file=avatar_path
            )
        else:
            avatar_downloaded = False

        if not avatar_downloaded:
            Image.new("RGB", (300, 300), "#444").save(avatar_path)

        
        avatar = (
            Image.open(avatar_path)
            .convert("RGBA")
            .resize((110, 110))
        )

        mask = Image.new("L", (110, 110), 0)

        ImageDraw.Draw(mask).ellipse(
            (0, 0, 110, 110),
            fill=255
        )

        avatar.putalpha(mask)

        
        font_name = ImageFont.truetype(FONT_BOLD, 40)
        font_text = ImageFont.truetype(FONT_REG, 36)
        font_time = ImageFont.truetype(FONT_REG, 24)

        
        max_text_width = 22
        wrapped = textwrap.wrap(text, max_text_width)

        dummy = Image.new("RGB", (1, 1))
        draw = ImageDraw.Draw(dummy)

        if not wrapped:
            wrapped = [""]

        text_height = sum(
            draw.textbbox(
                (0, 0),
                line,
                font=font_text
            )[3]
            for line in wrapped
        )

        name_width = draw.textbbox(
            (0, 0),
            name,
            font=font_name
        )[2]

        text_width = max(
            draw.textbbox(
                (0, 0),
                line,
                font=font_text
            )[2]
            for line in wrapped
        )

        bubble_width = max(name_width, text_width) + 60
        bubble_height = text_height + 120

        bubble_width = min(
            820,
            max(360, bubble_width)
        )

        bubble_height = min(
            400,
            bubble_height
        )

        
        bubble = Image.new(
            "RGBA",
            (bubble_width, bubble_height),
            (0, 0, 0, 0)
        )

        draw = ImageDraw.Draw(bubble)

        draw.rounded_rectangle(
            (0, 0, bubble_width, bubble_height),
            radius=35,
            fill="#1f1f1f"
        )

        if user:
            draw.text(
                (30, 20),
                name,
                font=font_name,
                fill="#8ab4f8"
            )

        y = 75

        for line in wrapped:
            draw.text(
                (30, y),
                line,
                font=font_text,
                fill="white"
            )

            y += font_text.size + 6

        draw.text(
            (bubble_width - 70, bubble_height - 35),
            current_time,
            font=font_time,
            fill="#9aa0a6"
        )

        
        canvas = Image.new(
            "RGBA",
            (512, 300),
            (0, 0, 0, 0)
        )

        canvas.paste(
            avatar,
            (20, 45),
            avatar
        )

        resized_height = int(
            bubble_height * 360 / bubble_width
        )

        bubble = bubble.resize(
            (360, resized_height)
        )

        canvas.paste(
            bubble,
            (140, 30),
            bubble
        )

        canvas.save(
            final_path,
            "WEBP",
            lossless=True
        )

        
        await event.client.send_file(
            event.chat_id,
            final_path,
            reply_to=event.reply_to_msg_id
        )