import json
import os
import re
import requests

from telethon import events, functions
from telethon.tl.types import ReactionEmoji

from config import (
    OPENROUTER_API_KEY,
    AUTO_REPLY_PROMPT,
    AUTO_REPLY_PROFILE_PROMPT,
    EXCLUDE_USERS
)


MAX_LEN = 10
MEMORY_FILE = "autoreply_memory.json"

autoreply_enabled = True

REACTION_COOLDOWN = 30
last_reaction_time = {}

ALLOWED_REACTIONS = {
    "👍",
    "👎",
    "❤️",
    "🔥",
    "🥰",
    "👏",
    "😁",
    "😢",
    "😱",
    "🤔",
    "🤯",
    "🤬",
    "😡",
    "🥳",
    "🎉",
    "💯",
    "🤣",
    "😂",
    "😮",
    "😇",
    "🙏",
}


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}

    try:
        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    except Exception:
        return {}


def save_memory(memory):
    with open(
        MEMORY_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            memory,
            file,
            ensure_ascii=False,
            indent=2
        )


def trim_memory(memory, chat_id):
    if len(memory[chat_id]) > MAX_LEN:
        memory[chat_id] = memory[chat_id][-MAX_LEN:]


async def get_profile_context(client, user):
    """Get publicly available Telegram profile information."""

    first_name = user.first_name or "Unknown"

    last_name = user.last_name or "None"

    username = (
        f"@{user.username}"
        if user.username
        else "None"
    )

    user_type = (
        "Bot"
        if getattr(user, "bot", False)
        else "User"
    )

    premium = (
        "Yes"
        if getattr(user, "premium", False)
        else "No"
    )

    verified = (
        "Yes"
        if getattr(user, "verified", False)
        else "No"
    )

    bio = "None"

    try:
        full_user = await client(
            functions.users.GetFullUserRequest(
                user
            )
        )

        if full_user.full_user.about:
            bio = full_user.full_user.about

    except Exception:
        pass

    return (
        "PROFILE INFORMATION:\n"
        f"First name: {first_name}\n"
        f"Last name: {last_name}\n"
        f"Username: {username}\n"
        f"Telegram ID: {user.id}\n"
        f"Account type: {user_type}\n"
        f"Premium: {premium}\n"
        f"Verified: {verified}\n"
        f"Bio: {bio}"
    )


def parse_ai_response(content):
    """Safely parse AI JSON response."""

    if not isinstance(content, str):
        return None

    content = content.strip()

    # Remove markdown code fences.
    content = re.sub(
        r"```json\s*",
        "",
        content,
        flags=re.IGNORECASE
    )

    content = content.replace(
        "```",
        ""
    ).strip()

    # Try normal JSON parsing first.
    try:
        result = json.loads(content)

        if isinstance(result, dict):
            return result

    except json.JSONDecodeError:
        pass

    # Try to recover values from partially valid JSON.
    reply_match = re.search(
        r'"reply"\s*:\s*(true|false)',
        content,
        flags=re.IGNORECASE
    )

    reaction_match = re.search(
        r'"reaction"\s*:\s*(true|false)',
        content,
        flags=re.IGNORECASE
    )

    emoji_match = re.search(
        r'"emoji"\s*:\s*"([^"]*)"',
        content
    )

    text_match = re.search(
        r'"text"\s*:\s*"([^"]*)"',
        content
    )

    if not reply_match and not reaction_match:
        print(
            f"⚠️ Could not parse AI response:\n{content}"
        )
        return None

    result = {
        "reply": (
            reply_match.group(1).lower() == "true"
            if reply_match
            else False
        ),
        "reaction": (
            reaction_match.group(1).lower() == "true"
            if reaction_match
            else False
        ),
        "emoji": (
            emoji_match.group(1)
            if emoji_match
            else ""
        ),
        "text": (
            text_match.group(1)
            if text_match
            else ""
        )
    }

    return result


def normalize_ai_result(result):
    """Validate and normalize AI decision."""

    if not isinstance(result, dict):
        return None

    reply = result.get("reply", False)
    reaction = result.get("reaction", False)

    emoji = result.get("emoji", "")
    text = result.get("text", "")

    reply = reply is True
    reaction = reaction is True

    if not isinstance(emoji, str):
        emoji = ""

    if not isinstance(text, str):
        text = ""

    emoji = emoji.strip()
    text = text.strip()

    if emoji not in ALLOWED_REACTIONS:
        reaction = False
        emoji = ""

    if not text:
        reply = False

    return {
        "reply": reply,
        "reaction": reaction,
        "emoji": emoji,
        "text": text
    }


def register_autoreply(client):

    # Enable or disable auto reply.
    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"\.autoreply (on|off)$"
        )
    )
    async def toggle_autoreply(event):

        global autoreply_enabled

        me = await client.get_me()

        if event.sender_id != me.id:
            return await event.edit(
                "❌ Only the owner can control Auto Reply."
            )

        mode = event.pattern_match.group(1)

        if mode == "on":
            autoreply_enabled = True

            await event.edit(
                "✅ Auto Reply enabled.\n"
                "Reaction + text response system is active."
            )

        else:
            autoreply_enabled = False

            await event.edit(
                "🛑 Auto Reply disabled."
            )

    # Auto Reply + Reaction handler.
    @client.on(events.NewMessage(incoming=True))
    async def handle_autoreply(event):

        if not autoreply_enabled:
            return

        # Private chats only.
        if not event.is_private:
            return

        sender = await event.get_sender()

        if not sender:
            return

        # Excluded users.
        if sender.id in EXCLUDE_USERS:
            return

        # Ignore bots.
        if getattr(sender, "bot", False):
            return

        user_msg = event.text

        if not user_msg:
            return

        # Get Telegram profile information.
        profile_context = await get_profile_context(
            client,
            sender
        )

        memory = load_memory()

        chat_id = str(event.chat_id)

        if chat_id not in memory:
            memory[chat_id] = []

        # Save user message.
        memory[chat_id].append({
            "role": "user",
            "content": user_msg
        })

        trim_memory(
            memory,
            chat_id
        )

        messages = [
            {
                "role": "system",
                "content": AUTO_REPLY_PROMPT
            },
            {
                "role": "system",
                "content": (
                    f"{AUTO_REPLY_PROFILE_PROMPT}\n\n"
                    f"{profile_context}"
                )
            }
        ]

        messages.extend(
            memory[chat_id]
        )

        payload = {
            "model": "dots-studio/dots-3-note-preview:free",
            "messages": messages,
            "max_tokens": 1200,
            "temperature": 0.7,
            "top_p": 0.9,
            "response_format": {
                "type": "json_object"
            }
        }

        try:

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": (
                        f"Bearer {OPENROUTER_API_KEY}"
                    ),
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30
            )

            if response.status_code != 200:
                return await event.reply(
                    f"❌ API error:\n{response.text}"
                )

            data = response.json()

            choices = data.get("choices", [])

            if not choices:
                print(
                    "⚠️ AI returned no choices."
                )
                print(data)

                return

            message = choices[0].get(
                "message"
            ) or {}

            content = message.get(
                "content"
            )

            if not isinstance(content, str):
                content = ""

            content = content.strip()

            if not content:
                print(
                    "⚠️ OpenRouter returned "
                    "an empty answer."
                )
                print(data)
                return

            # Parse AI decision.
            result = parse_ai_response(
                content
            )

            if not result:
                print(
                    "⚠️ Could not parse AI decision."
                )
                print(content)
                return

            result = normalize_ai_result(
                result
            )

            if not result:
                return

            should_reply = result["reply"]
            should_react = result["reaction"]
            emoji = result["emoji"]
            reply_text = result["text"]

            print(
                f"🤖 AI decision | "
                f"Reply: {should_reply} | "
                f"Reaction: {should_react} | "
                f"Emoji: {emoji}"
            )

            # Send reaction if AI decided to react.
            if should_react:

                import time

                now = time.time()

                last_time = last_reaction_time.get(
                    chat_id,
                    0
                )

                if (
                    now - last_time
                    >= REACTION_COOLDOWN
                ):

                    try:

                        await client(
                            functions.messages.SendReactionRequest(
                                peer=event.chat_id,
                                msg_id=event.id,
                                reaction=[
                                    ReactionEmoji(
                                        emoticon=emoji
                                    )
                                ]
                            )
                        )

                        last_reaction_time[
                            chat_id
                        ] = now

                        print(
                            f"👍 Reaction sent: "
                            f"{emoji}"
                        )

                    except Exception as e:

                        print(
                            "❌ Reaction error: "
                            f"{e}"
                        )

            # Save AI text response to memory.
            if should_reply:

                memory[chat_id].append({
                    "role": "assistant",
                    "content": reply_text
                })

                trim_memory(
                    memory,
                    chat_id
                )

                save_memory(
                    memory
                )

                # Send text response.
                await event.reply(
                    reply_text
                )

            else:

                # Save memory even when only reaction
                # was sent.
                save_memory(
                    memory
                )

        except Exception as e:

            print(
                f"❌ Auto Reply error: {e}"
            )