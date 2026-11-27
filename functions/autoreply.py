# By @aliyhacker
# autoreply version 5
import asyncio
import io
import json
import os
import re
import time
import zipfile
import xml.etree.ElementTree as ET

from google import genai
from google.genai import types
from telethon import events, functions
from telethon.tl.types import PeerChannel, ReactionEmoji

from config import (
    GEMINI_API_KEY,
    AUTO_REPLY_PROMPT,
    AUTO_REPLY_PROFILE_PROMPT,
    EXCLUDE_USERS,
    CLOUDFLARE_WORKER_URL,
)

MAX_LEN = 10
MEMORY_FILE = "autoreply_memory.json"
EXCLUDE_FILE = "autoreply_exclude.json"
MODEL_TIMEOUT = 25.0

OWNER_CONTEXT_TTL = 900
CHANNEL_POST_LIMIT = 15
MAX_POST_CHARS = 700

MAX_IMAGE_BYTES = 5 * 1024 * 1024   # Max 5 MB
MAX_AUDIO_BYTES = 5 * 1024 * 1024   # Max 5 MB
MAX_AUDIO_SECONDS = 180  # Max 3 min
MAX_VIDEO_BYTES = 10 * 1024 * 1024  # Max 10 MB
MAX_VIDEO_SECONDS = 45  # Max: 45 sec
MAX_DOC_BYTES = 10 * 1024 * 1024  # Max 10 MB
MAX_DOC_CHARS = 12000

TEXT_FILE_EXTENSIONS = {
    ".txt", ".md", ".csv", ".json", ".xml", ".yaml", ".yml",
    ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css",
    ".sql", ".sh", ".bash", ".log", ".ini", ".cfg", ".env",
    ".c", ".cpp", ".h", ".java", ".go", ".rs", ".php",
}

autoreply_enabled = True

REACTION_COOLDOWN = 30
last_reaction_time = {}
memory_lock = asyncio.Lock()
owner_context_lock = asyncio.Lock()

owner_context_cache = {
    "text": "",
    "updated_at": 0.0,
}

GEMINI_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-pro-preview",
]

genai_client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options=types.HttpOptions(
        base_url=CLOUDFLARE_WORKER_URL
    ),
)

ALLOWED_REACTIONS = {
    "👍", "👎", "❤️", "🔥", "🥰", "👏", "😁",
    "😢", "😱", "🤔", "🤯", "🤬", "😡", "🥳",
    "🎉", "💯", "🤣", "😂", "😮", "😇", "🙏",
}


def load_excluded():
    users = set(EXCLUDE_USERS)
    if os.path.exists(EXCLUDE_FILE):
        try:
            with open(EXCLUDE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    users.update(int(x) for x in data)
        except Exception:
            pass
    return users


def save_excluded(users_set):
    with open(EXCLUDE_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(list(users_set)), f, indent=2)


excluded_users = load_excluded()


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}


def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(memory, file, ensure_ascii=False, indent=2)


def trim_memory(memory, chat_id):
    if len(memory[chat_id]) > MAX_LEN:
        memory[chat_id] = memory[chat_id][-MAX_LEN:]


def get_doc_filename(msg):
    file_obj = getattr(msg, "file", None)
    name = getattr(file_obj, "name", None) if file_obj else None
    return (name or "").strip()


def is_image_message(msg):
    if not msg:
        return False
    if getattr(msg, "photo", None):
        return True
    doc = getattr(msg, "document", None)
    mime = (getattr(doc, "mime_type", "") or "").lower()
    if doc and mime.startswith("image/"):
        return True
    return False


def is_audio_message(msg):
    if not msg:
        return False
    if getattr(msg, "voice", None) or getattr(msg, "audio", None):
        return True
    doc = getattr(msg, "document", None)
    mime = (getattr(doc, "mime_type", "") or "").lower()
    if doc and mime.startswith("audio/"):
        return True
    return False


def is_video_message(msg):
    if not msg:
        return False
    if getattr(msg, "video", None) or getattr(msg, "video_note", None):
        return True
    doc = getattr(msg, "document", None)
    mime = (getattr(doc, "mime_type", "") or "").lower()
    if doc and mime.startswith("video/"):
        return True
    return False


def is_supported_doc_message(msg):
    if not msg:
        return False
    doc = getattr(msg, "document", None)
    if not doc:
        return False
    if is_image_message(msg) or is_audio_message(msg) or is_video_message(msg):
        return False

    mime = (getattr(doc, "mime_type", "") or "").lower()
    fname = get_doc_filename(msg).lower()
    _, ext = os.path.splitext(fname)

    if mime == "application/pdf" or ext == ".pdf":
        return True
    if (
        mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        or ext == ".docx"
    ):
        return True
    if mime.startswith("text/") or mime in ("application/json", "application/xml"):
        return True
    if ext in TEXT_FILE_EXTENSIONS:
        return True
    return False


def has_supported_attachment(msg):
    return (
        is_image_message(msg)
        or is_audio_message(msg)
        or is_video_message(msg)
        or is_supported_doc_message(msg)
    )


def extract_docx_text(file_bytes, max_chars=MAX_DOC_CHARS):
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
            if "word/document.xml" not in zf.namelist():
                return ""
            xml_content = zf.read("word/document.xml")
        tree = ET.fromstring(xml_content)
        paragraphs = []
        for elem in tree.iter():
            if elem.tag.endswith("}p"):
                texts = [t.text for t in elem.iter() if t.tag.endswith("}t") and t.text]
                if texts:
                    paragraphs.append("".join(texts))
        full_text = "\n".join(paragraphs).strip()
        if len(full_text) > max_chars:
            full_text = full_text[:max_chars] + "\n...[text truncated]"
        return full_text
    except Exception as e:
        print(f"⚠️ Error reading DOCX file: {e}")
        return ""


def extract_plain_text(file_bytes, max_chars=MAX_DOC_CHARS):
    try:
        text = file_bytes.decode("utf-8", errors="replace").strip()
        if len(text) > max_chars:
            text = text[:max_chars] + "\n...[text truncated]"
        return text
    except Exception as e:
        print(f"⚠️ Error reading text file: {e}")
        return ""



async def extract_attachment_from_event(client, event):
    target_msg = None
    if has_supported_attachment(event.message):
        target_msg = event.message
    elif event.is_reply:
        try:
            reply_msg = await event.get_reply_message()
            if has_supported_attachment(reply_msg):
                target_msg = reply_msg
        except Exception:
            pass

    if not target_msg:
        return None

    doc = getattr(target_msg, "document", None)
    file_obj = getattr(target_msg, "file", None)
    file_size = (getattr(doc, "size", 0) or getattr(file_obj, "size", 0) or 0)
    duration = (getattr(file_obj, "duration", 0) or 0)
    fname = get_doc_filename(target_msg)
    mime = (getattr(doc, "mime_type", "") or "").strip().lower()

    if is_image_message(target_msg):
        if file_size > MAX_IMAGE_BYTES:
            return {
                "kind": "rejected",
                "text": "[User sent an image larger than 5 MB — unable to open due to file size]",
                "label": "image_too_large",
            }
        img_mime = "image/jpeg" if getattr(target_msg, "photo", None) else (mime or "image/jpeg")
        data = await client.download_media(target_msg, file=bytes)
        if data:
            return {"kind": "image", "bytes": data, "mime": img_mime, "label": "image"}
        return None

    if is_audio_message(target_msg):
        if file_size > MAX_AUDIO_BYTES or duration > MAX_AUDIO_SECONDS:
            return {
                "kind": "rejected",
                "text": "[User sent audio longer than 3 minutes or larger than 5 MB — unable to process]",
                "label": "audio_too_large",
            }
        aud_mime = mime or ("audio/ogg" if getattr(target_msg, "voice", None) else "audio/mpeg")
        data = await client.download_media(target_msg, file=bytes)
        if data:
            return {"kind": "audio", "bytes": data, "mime": aud_mime, "label": "audio"}
        return None

    if is_video_message(target_msg):
        if file_size > MAX_VIDEO_BYTES or duration > MAX_VIDEO_SECONDS:
            return {
                "kind": "rejected",
                "text": "[This video exceeds our technical limits (45 seconds or 10 MB). Please send a shorter video or describe its contents in text. Thank you for your understanding!]",
                "label": "video_too_large",
            }
        vid_mime = mime or "video/mp4"
        data = await client.download_media(target_msg, file=bytes)
        if data:
            return {"kind": "video", "bytes": data, "mime": vid_mime, "label": "video"}
        return None

    if is_supported_doc_message(target_msg):
        display_name = fname or "document"
        if file_size > MAX_DOC_BYTES:
            return {
                "kind": "rejected",
                "text": f"[User sent a document named '{display_name}' larger than 10 MB — unable to open due to file size]",
                "label": "doc_too_large",
            }

        data = await client.download_media(target_msg, file=bytes)
        if not data:
            return None

        _, ext = os.path.splitext(fname.lower())
        if mime == "application/pdf" or ext == ".pdf":
            return {
                "kind": "pdf",
                "bytes": data,
                "mime": "application/pdf",
                "label": f"pdf:{display_name}",
            }

        if (
            mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            or ext == ".docx"
        ):
            extracted = await asyncio.to_thread(extract_docx_text, data)
            if not extracted:
                extracted = "(The Word document is empty or its text could not be extracted)"
            return {
                "kind": "doc_text",
                "text": f"[Document: {display_name}]\n{extracted}",
                "label": f"docx:{display_name}",
            }

        extracted = await asyncio.to_thread(extract_plain_text, data)
        if not extracted:
            extracted = "(File is empty)"
        return {
            "kind": "doc_text",
            "text": f"[File: {display_name}]\n{extracted}",
            "label": f"file:{display_name}",
        }

    return None

async def resolve_target_user(client, event, arg):
    """Resolve a user via chat, reply, username, or ID."""
    if arg:
        target = int(arg) if arg.isdigit() else arg
        return await client.get_entity(target)
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        return await reply_msg.get_sender()
    if event.is_private:
        return await event.get_chat()
    return None

async def get_profile_context(client, user):
    """Get publicly available Telegram profile information of the sender."""
    first_name = user.first_name or "Unknown"
    last_name = user.last_name or "None"
    username = f"@{user.username}" if user.username else "None"
    user_type = "Bot" if getattr(user, "bot", False) else "User"
    premium = "Yes" if getattr(user, "premium", False) else "No"
    verified = "Yes" if getattr(user, "verified", False) else "No"
    bio = "None"

    try:
        full_user = await client(functions.users.GetFullUserRequest(user))
        if full_user.full_user.about:
            bio = full_user.full_user.about
    except Exception:
        pass

    return (
        "SENDER PROFILE INFORMATION:\n"
        f"First name: {first_name}\n"
        f"Last name: {last_name}\n"
        f"Username: {username}\n"
        f"Telegram ID: {user.id}\n"
        f"Account type: {user_type}\n"
        f"Premium: {premium}\n"
        f"Verified: {verified}\n"
        f"Bio: {bio}"
    )


async def fetch_owner_context(client):
    me = await client.get_me()
    first_name = me.first_name or "Unknown"
    last_name = me.last_name or "None"
    username = f"@{me.username}" if me.username else "None"
    bio = "None"
    personal_channel_id = None

    try:
        full_me = await client(functions.users.GetFullUserRequest("me"))
        if full_me.full_user.about:
            bio = full_me.full_user.about
        personal_channel_id = getattr(full_me.full_user, "personal_channel_id", None)
    except Exception as e:
        print(f"⚠️ Owner full profile error: {e}")

    lines = [
        "OWNER (YOUR) PROFILE INFORMATION:",
        f"First name: {first_name}",
        f"Last name: {last_name}",
        f"Username: {username}",
        f"Telegram ID: {me.id}",
        f"Bio: {bio}",
    ]

    if personal_channel_id:
        try:
            try:
                channel = await client.get_entity(PeerChannel(personal_channel_id))
            except Exception:
                channel = await client.get_entity(personal_channel_id)

            ch_title = getattr(channel, "title", "Unknown")
            ch_username = f"@{channel.username}" if getattr(channel, "username", None) else "Private/None"
            ch_about = "None"

            try:
                full_ch = await client(functions.channels.GetFullChannelRequest(channel))
                if full_ch.full_chat.about:
                    ch_about = full_ch.full_chat.about
            except Exception:
                pass

            lines.extend([
                "",
                "OWNER LINKED PERSONAL CHANNEL:",
                f"Channel title: {ch_title}",
                f"Channel username: {ch_username}",
                f"Channel ID: {personal_channel_id}",
                f"Channel description: {ch_about}",
            ])

            posts = []
            async for msg in client.iter_messages(channel, limit=CHANNEL_POST_LIMIT * 2):
                text = (msg.message or "").strip()
                if not text:
                    continue
                text = re.sub(r"\s+", " ", text)
                if len(text) > MAX_POST_CHARS:
                    text = text[:MAX_POST_CHARS] + "..."
                date_str = msg.date.strftime("%Y-%m-%d") if msg.date else ""
                posts.append(f"- [{date_str}] {text}")
                if len(posts) >= CHANNEL_POST_LIMIT:
                    break

            if posts:
                lines.append(f"RECENT CHANNEL POSTS (latest {len(posts)}):")
                lines.extend(posts)
            else:
                lines.append("RECENT CHANNEL POSTS: None")

        except Exception as e:
            print(f"⚠️ Personal channel fetch error: {e}")
    else:
        lines.append("OWNER LINKED PERSONAL CHANNEL: None")

    return "\n".join(lines)


async def get_owner_context(client, force_refresh=False):
    now = time.time()
    if (
        not force_refresh
        and owner_context_cache["text"]
        and (now - owner_context_cache["updated_at"] < OWNER_CONTEXT_TTL)
    ):
        return owner_context_cache["text"]

    async with owner_context_lock:
        now = time.time()
        if (
            not force_refresh
            and owner_context_cache["text"]
            and (now - owner_context_cache["updated_at"] < OWNER_CONTEXT_TTL)
        ):
            return owner_context_cache["text"]

        context_text = await fetch_owner_context(client)
        owner_context_cache["text"] = context_text
        owner_context_cache["updated_at"] = time.time()
        return context_text


async def ask_gemini_fallback(system_instruction, history, attachment=None):
    contents = []
    last_idx = len(history) - 1
    for idx, msg in enumerate(history):
        role = "model" if msg.get("role") == "assistant" else "user"
        parts = [types.Part.from_text(text=msg.get("content", ""))]
        if idx == last_idx and role == "user" and attachment:
            kind = attachment.get("kind")
            if kind in ("image", "audio", "video", "pdf") and attachment.get("bytes"):
                parts.append(
                    types.Part.from_bytes(
                        data=attachment["bytes"],
                        mime_type=attachment["mime"],
                    )
                )
            elif kind in ("doc_text", "rejected") and attachment.get("text"):
                parts.append(types.Part.from_text(text=attachment["text"]))
        contents.append(types.Content(role=role, parts=parts))

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.7,
        top_p=0.9,
        max_output_tokens=1200,
        response_mime_type="application/json",
    )

    for model_name in GEMINI_MODELS:
        try:
            response = await asyncio.wait_for(
                genai_client.aio.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=config,
                ),
                timeout=MODEL_TIMEOUT,
            )
            text = (response.text or "").strip()
            if text:
                print(f"✅ Responding model: {model_name}")
                return text
        except asyncio.TimeoutError:
            print(f"⏱️ {model_name} did not respond within {MODEL_TIMEOUT}s. Switching to the next model...")
            continue
        except Exception as e:
            print(f"⚠️ {model_name} failed ({e}). Switching to the next model...")
            continue

    print("❌ All Gemini models are busy or returned an error.")
    return None


def parse_ai_response(content):
    """Safely parse AI JSON response."""
    if not isinstance(content, str):
        return None

    content = content.strip()
    content = re.sub(r"```json\s*", "", content, flags=re.IGNORECASE)
    content = content.replace("```", "").strip()

    try:
        result = json.loads(content)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass

    reply_match = re.search(r'"reply"\s*:\s*(true|false)', content, flags=re.IGNORECASE)
    reaction_match = re.search(r'"reaction"\s*:\s*(true|false)', content, flags=re.IGNORECASE)
    emoji_match = re.search(r'"emoji"\s*:\s*"([^"]*)"', content)
    text_match = re.search(r'"text"\s*:\s*"([^"]*)"', content)

    if not reply_match and not reaction_match:
        print(f"⚠️ Could not parse AI response:\n{content}")
        return None

    return {
        "reply": reply_match.group(1).lower() == "true" if reply_match else False,
        "reaction": reaction_match.group(1).lower() == "true" if reaction_match else False,
        "emoji": emoji_match.group(1) if emoji_match else "",
        "text": text_match.group(1) if text_match else "",
    }


def normalize_ai_result(result):
    """Validate and normalize AI decision."""
    if not isinstance(result, dict):
        return None

    reply = result.get("reply", False) is True
    reaction = result.get("reaction", False) is True
    emoji = result.get("emoji", "")
    text = result.get("text", "")

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
        "text": text,
    }


def register_autoreply(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.autoreply (on|off)$"))
    async def toggle_autoreply(event):
        global autoreply_enabled
        me = await client.get_me()

        if event.sender_id != me.id:
            return await event.edit("❌ Only the owner can control Auto Reply.")

        mode = event.pattern_match.group(1)
        if mode == "on":
            autoreply_enabled = True
            await event.edit(
                "✅ Auto Reply enabled.\n"
                "Text + vision + voice + video + docs response system is active."
            )
        else:
            autoreply_enabled = False
            await event.edit("🛑 Auto Reply disabled.")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.arrefresh$"))
    async def refresh_owner_info(event):
        await event.edit("🔄 Updating profile and channel posts...")
        try:
            await get_owner_context(client, force_refresh=True)
            await event.edit("✅ Profile and channel posts cache updated successfully.")
        except Exception as e:
            await event.edit(f"❌ Error updating: `{e}`")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.arblock(?:\s+(.+))?$"))
    async def block_autoreply_user(event):
        arg = (event.pattern_match.group(1) or "").strip()
        try:
            user = await resolve_target_user(client, event, arg)
            if not user:
                return await event.edit("❌ Please send this in a private chat or enter `@username` / ID.")

            excluded_users.add(user.id)
            save_excluded(excluded_users)
            name = getattr(user, "first_name", str(user.id))
            await event.edit(f"🚫 **{name}** (`{user.id}`) has been added to Auto Reply exceptions.")
        except Exception as e:
            await event.edit(f"❌ Error: `{e}`")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.arunblock(?:\s+(.+))?$"))
    async def unblock_autoreply_user(event):
        arg = (event.pattern_match.group(1) or "").strip()
        try:
            user = await resolve_target_user(client, event, arg)
            if not user:
                return await event.edit("❌ Please send this in a private chat or enter `@username` / ID.")

            if user.id in excluded_users:
                excluded_users.discard(user.id)
                save_excluded(excluded_users)
                name = getattr(user, "first_name", str(user.id))
                await event.edit(f"✅ **{name}** (`{user.id}`) has been removed from the exceptions list.")
            else:
                await event.edit("ℹ️ This user is not on the exceptions list.")
        except Exception as e:
            await event.edit(f"❌ Error: `{e}`")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.arlist$"))
    async def list_excluded_users(event):
        if not excluded_users:
            return await event.edit("📋 The Auto Reply exceptions list is empty.")
        lines = [f"• `{uid}`" for uid in sorted(excluded_users)]
        await event.edit("📋 **Auto Reply Exceptions:**\n" + "\n".join(lines))

    @client.on(events.NewMessage(incoming=True))
    async def handle_autoreply(event):
        if not autoreply_enabled:
            return
        if not event.is_private:
            return

        sender = await event.get_sender()
        if not sender:
            return
        if sender.id in excluded_users:
            return
        if getattr(sender, "bot", False):
            return

        user_msg = (event.text or "").strip()
        has_direct_attachment = has_supported_attachment(event.message)

        if not user_msg and not has_direct_attachment:
            return

        profile_context, owner_context, attachment = await asyncio.gather(
            get_profile_context(client, sender),
            get_owner_context(client),
            extract_attachment_from_event(client, event),
        )
        chat_id = str(event.chat_id)

        if has_direct_attachment:
            tag = attachment["label"] if attachment else "file"
            stored_text = f"[{tag} sent] {user_msg}".strip()
        else:
            stored_text = user_msg

        async with memory_lock:
            memory = load_memory()
            if chat_id not in memory:
                memory[chat_id] = []
            memory[chat_id].append({"role": "user", "content": stored_text})
            trim_memory(memory, chat_id)
            save_memory(memory)
            history_snapshot = list(memory[chat_id])

        system_instruction = (
            f"{AUTO_REPLY_PROMPT}\n\n"
            f"{AUTO_REPLY_PROFILE_PROMPT}\n\n"
            f"{owner_context}\n\n"
            f"{profile_context}"
        )

        try:
            content = await ask_gemini_fallback(
                system_instruction,
                history_snapshot,
                attachment=attachment,
            )
            if not content:
                return

            result = parse_ai_response(content)
            if not result:
                print(f"⚠️ Could not parse AI decision.\n{content}")
                return

            result = normalize_ai_result(result)
            if not result:
                return

            should_reply = result["reply"]
            should_react = result["reaction"]
            emoji = result["emoji"]
            reply_text = result["text"]

            media_tag = attachment["label"] if attachment else "none"
            print(
                f"🤖 AI decision | "
                f"Reply: {should_reply} | "
                f"Reaction: {should_react} | "
                f"Emoji: {emoji} | "
                f"Attachment: {media_tag}"
            )

            if should_react:
                now = time.time()
                last_time = last_reaction_time.get(chat_id, 0)
                if now - last_time >= REACTION_COOLDOWN:
                    try:
                        await client(
                            functions.messages.SendReactionRequest(
                                peer=event.chat_id,
                                msg_id=event.id,
                                reaction=[ReactionEmoji(emoticon=emoji)],
                            )
                        )
                        last_reaction_time[chat_id] = now
                        print(f"👍 Reaction sent: {emoji}")
                    except Exception as e:
                        print(f"❌ Reaction error: {e}")

            if should_reply:
                async with memory_lock:
                    memory = load_memory()
                    if chat_id not in memory:
                        memory[chat_id] = []
                    memory[chat_id].append({"role": "assistant", "content": reply_text})
                    trim_memory(memory, chat_id)
                    save_memory(memory)
                await event.reply(reply_text)

        except Exception as e:
            print(f"❌ Auto Reply error: {e}")
