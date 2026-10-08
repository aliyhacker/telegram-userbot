import json
import requests

from telethon import events

from config import OWNER_ID, OPENROUTER_API_KEY


ai_chats = {}


def register_aimode(client):

    # AI mode on/off
    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"\.aimode (on|off)"
        )
    )
    async def ai_toggle(event):

        chat_id = event.chat_id
        mode = event.pattern_match.group(1)

        # Only owner can control AI mode
        if event.sender_id != OWNER_ID:
            return await event.edit(
                "❌ Only the owner can enable or disable AI chat."
            )

        # Enable AI mode
        if mode == "on":

            ai_chats[chat_id] = {
                "active": True,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a professional AI assistant. "
                            "Always respond in Uzbek. "
                            "Your answers must be clear, understandable, "
                            "polite, and grammatically correct. "
                            "Provide useful, logical, and complete answers "
                            "whenever possible. "
                            "Help the user with the topic they ask about."
                        )
                    }
                ],
                "all_users": False
            }

            return await event.edit(
                "🤖 AI chat mode enabled. "
                "Only the owner will receive AI responses."
            )

        # Disable AI mode
        else:

            ai_chats.pop(chat_id, None)

            return await event.edit(
                "🤖 AI chat mode disabled."
            )

    # AI chat handler
    @client.on(events.NewMessage())
    async def ai_chat_handler(event):

        chat_id = event.chat_id

        # AI mode is not enabled
        if (
            chat_id not in ai_chats
            or not ai_chats[chat_id]["active"]
        ):
            return

        # Ignore commands
        if event.raw_text.startswith(".ai"):
            return

        # Only owner can use AI chat
        if event.sender_id != OWNER_ID:
            return

        user_msg = event.raw_text
        msg = event

        # Add user message to memory
        ai_chats[chat_id]["messages"].append({
            "role": "user",
            "content": user_msg
        })

        url = "https://openrouter.ai/api/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "dots-studio/dots-3-note-preview:free",
            "messages": ai_chats[chat_id]["messages"],
            "max_tokens": 850,
            "temperature": 0.7
        }

        try:

            response = requests.post(
                url,
                headers=headers,
                data=json.dumps(payload),
                timeout=60
            )

            if response.status_code != 200:
                return await msg.reply(
                    f"❌ API error:\n{response.text}"
                )

            result = response.json()

            answer = (
                result["choices"][0]["message"]["content"]
            )

            await msg.reply(
                f"🤖 AI:\n{answer}"
            )

            # Add assistant response to memory
            ai_chats[chat_id]["messages"].append({
                "role": "assistant",
                "content": answer
            })

        except Exception as e:

            await msg.reply(
                f"❌ Error:\n{e}"
            )