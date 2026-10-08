import json
import requests

from telethon import events

from config import OPENROUTER_API_KEY


OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)

AI_MODEL = "dots-studio/dots-3-note-preview:free"

SYSTEM_PROMPT = (
    "You are a professional AI assistant. "
    "Give clear, accurate, useful, and professional answers."
)


def register_ai(client):

    # .ai command
    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"\.ai(?: |$)(.*)"
        )
    )
    async def ai_single(event):

        query = event.pattern_match.group(1).strip()

        # Use replied message when available
        if event.is_reply:
            reply_msg = await event.get_reply_message()
            user_text = reply_msg.message or ""
        else:
            user_text = query

        if not user_text.strip():
            return await event.edit(
                "❌ Please enter a question or reply to a message."
            )

        await event.edit("🤖 Thinking...")

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_text
            }
        ]

        try:
            response = requests.post(
                OPENROUTER_URL,
                headers={
                    "Authorization": (
                        f"Bearer {OPENROUTER_API_KEY}"
                    ),
                    "Content-Type": "application/json"
                },
                json={
                    "model": AI_MODEL,
                    "messages": messages,
                    "max_tokens": 850,
                    "temperature": 0.8,
                    "top_p": 0.9,
                    "frequency_penalty": 0.6,
                    "presence_penalty": 0.4
                },
                timeout=60
            )

            if response.status_code != 200:
                return await event.edit(
                    f"❌ API error:\n{response.text}"
                )

            data = response.json()

            answer = (
                data["choices"][0]["message"]["content"]
                .strip()
            )

            await event.edit(answer)

        except Exception as e:
            await event.edit(
                f"❌ Error:\n{e}"
            )

    # .ai1 command
    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"\.ai1(?: |$)(.*)"
        )
    )
    async def ai_single_force(event):

        query = event.pattern_match.group(1).strip()

        # .ai1 never uses replied message
        if not query:
            return await event.edit(
                "❌ Please enter text after .ai1."
            )

        await event.edit("🤖 Thinking...")

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": query
            }
        ]

        try:
            response = requests.post(
                OPENROUTER_URL,
                headers={
                    "Authorization": (
                        f"Bearer {OPENROUTER_API_KEY}"
                    ),
                    "Content-Type": "application/json"
                },
                json={
                    "model": AI_MODEL,
                    "messages": messages,
                    "max_tokens": 850,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "frequency_penalty": 0.6,
                    "presence_penalty": 0.4
                },
                timeout=60
            )

            if response.status_code != 200:
                return await event.edit(
                    f"❌ API error:\n{response.text}"
                )

            data = response.json()

            answer = (
                data["choices"][0]["message"]["content"]
                .strip()
            )

            await event.edit(answer)

        except Exception as e:
            await event.edit(
                f"❌ Error:\n{e}"
            )