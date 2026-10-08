# @aliyhacker
import os
import re
import sqlite3
from datetime import datetime

from telethon import events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument


DEST_DIR = "/storage/emulated/0/Download/TelegramSaver"
DATABASE_FILE = "download_stats.db"

URL_RE = re.compile(
    r"https?://t\.me/([^\s/]+)(?:/(\d+))?|https?://t\.me/c/(\d+)/(\d+)",
    flags=re.IGNORECASE
)


# ============================================================
# DATABASE
# ============================================================

def init_database():
    """Create the download statistics database."""
    conn = sqlite3.connect(DATABASE_FILE)

    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS download_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            chat_title TEXT,
            download_count INTEGER DEFAULT 0,
            last_download TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    conn.close()


def update_download_stats(chat_id, chat_title):
    """Increase the download counter for a chat."""
    conn = sqlite3.connect(DATABASE_FILE)

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM download_stats WHERE chat_id = ?",
        (chat_id,)
    )

    existing = cursor.fetchone()

    if existing:
        cursor.execute(
            """
            UPDATE download_stats
            SET download_count = download_count + 1,
                last_download = CURRENT_TIMESTAMP
            WHERE chat_id = ?
            """,
            (chat_id,)
        )
    else:
        cursor.execute(
            """
            INSERT INTO download_stats (
                chat_id,
                chat_title,
                download_count
            )
            VALUES (?, ?, 1)
            """,
            (chat_id, chat_title)
        )

    conn.commit()
    conn.close()


def get_download_stats():
    """Return download statistics sorted by download count."""
    conn = sqlite3.connect(DATABASE_FILE)

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT chat_title, download_count, last_download
        FROM download_stats
        ORDER BY download_count DESC
        """
    )

    stats = cursor.fetchall()

    conn.close()

    return stats


# ============================================================
# FILE HELPERS
# ============================================================

def ensure_dir(path: str):
    """Create a directory if it does not exist."""
    os.makedirs(path, exist_ok=True)


def sanitize_filename(name: str) -> str:
    """Remove characters that are invalid in filenames."""
    invalid = r'\/:*?"<>|'

    cleaned = "".join(
        character
        for character in name
        if character not in invalid
    ).strip()

    return cleaned or "file"


def unique_path(dirpath: str, filename: str) -> str:
    """Generate a unique file path without overwriting existing files."""
    base, ext = os.path.splitext(filename)

    candidate = os.path.join(
        dirpath,
        filename
    )

    counter = 1

    while os.path.exists(candidate):
        candidate = os.path.join(
            dirpath,
            f"{base} ({counter}){ext}"
        )

        counter += 1

    return candidate


# ============================================================
# CHAT INFORMATION
# ============================================================

async def get_chat_info(entity):
    """Get a readable ID and title for a Telegram entity."""
    try:
        if hasattr(entity, "title") and entity.title:
            return entity.id, entity.title

        elif hasattr(entity, "first_name"):
            name = entity.first_name or ""

            if getattr(entity, "last_name", None):
                name += f" {entity.last_name}"

            return entity.id, name or "Unknown"

        elif hasattr(entity, "username") and entity.username:
            return entity.id, f"@{entity.username}"

        else:
            return entity.id, "Unknown"

    except Exception:
        return "Unknown", "Unknown"


# ============================================================
# FETCH MESSAGE FROM TELEGRAM LINK
# ============================================================

async def fetch_message_from_link(client, link: str):
    """Fetch a Telegram message using a t.me link."""

    # Private/internal Telegram chat link:
    # https://t.me/c/123456789/100
    private_match = re.match(
        r"https?://t\.me/c/(\d+)/(\d+)",
        link,
        flags=re.IGNORECASE
    )

    if private_match:
        chat_num = int(private_match.group(1))
        msg_id = int(private_match.group(2))

        full_chat_id = int(f"-100{chat_num}")

        try:
            entity = await client.get_entity(full_chat_id)

        except Exception as error:
            raise Exception(
                f"Unable to access the private/internal chat "
                f"(chat_id={chat_num}). "
                f"Your account must be a member or the chat may not exist: "
                f"{error}"
            )

        try:
            fetched = await client.get_messages(
                entity,
                ids=msg_id
            )

            return fetched, entity

        except Exception as error:
            raise Exception(
                f"Unable to retrieve the message "
                f"(chat_id={chat_num}, message_id={msg_id}): "
                f"{error}"
            )

    # Public Telegram link:
    # https://t.me/channel/123
    public_match = re.match(
        r"https?://t\.me/([^/\s]+)/(\d+)",
        link,
        flags=re.IGNORECASE
    )

    if public_match:
        username = public_match.group(1)
        msg_id = int(public_match.group(2))

        try:
            entity = await client.get_entity(username)

        except Exception as error:
            raise Exception(
                f"Entity not found (username='{username}'): {error}"
            )

        try:
            fetched = await client.get_messages(
                entity,
                ids=msg_id
            )

            return fetched, entity

        except Exception as error:
            raise Exception(
                f"Unable to retrieve the message "
                f"(username='{username}', message_id={msg_id}): "
                f"{error}"
            )

    # Fallback: let Telethon try to resolve the link directly.
    try:
        fetched = await client.get_messages(link)

        if fetched:
            if isinstance(fetched, (list, tuple)):
                fetched = fetched[0] if fetched else None

            if fetched:
                entity = await client.get_entity(
                    fetched.peer_id
                )

                return fetched, entity

    except Exception as error:
        raise Exception(
            f"Unable to parse the link or retrieve the message directly: "
            f"{error}"
        )

    raise Exception(
        "None of the supported methods could process the Telegram link."
    )


# ============================================================
# PROFILE MEDIA DOWNLOADER
# ============================================================

async def download_chat_profile_media(client, chat_id: int):
    """Download all available profile photos of a Telegram entity."""

    try:
        entity = await client.get_entity(chat_id)

    except Exception as error:
        raise Exception(
            f"Chat not found: {error}"
        )

    chat_title = getattr(
        entity,
        "title",
        str(chat_id)
    )

    ensure_dir(DEST_DIR)

    profile_dir = os.path.join(
        DEST_DIR,
        sanitize_filename(chat_title)
    )

    ensure_dir(profile_dir)

    downloaded_files = []

    async for photo in client.iter_profile_photos(entity):
        try:
            photo_path = await client.download_media(
                photo,
                file=profile_dir
            )

            if photo_path:
                downloaded_files.append(photo_path)

        except Exception as error:
            print(
                f"Profile media download error: {error}"
            )

    return downloaded_files, entity


# ============================================================
# SAVE MEDIA COMMAND
# ============================================================

async def handle_rsave(event, client):
    """Handle the .rsave command."""

    try:
        await event.delete()

    except Exception:
        pass

    try:
        reply = await event.get_reply_message()

        target_msg = None
        source_entity = None

        # ----------------------------------------------------
        # Mode 1: Reply to a media message
        # ----------------------------------------------------

        if reply and getattr(reply, "media", None) is not None:

            target_msg = reply

            source_entity = await client.get_entity(
                reply.peer_id
            )

            print(
                f"Media found through reply: "
                f"message_id={getattr(reply, 'id', None)}"
            )

        else:
            arg = event.pattern_match.group(1)

            # ------------------------------------------------
            # Mode 2: Download profile media using chat ID
            # ------------------------------------------------

            if arg and re.fullmatch(
                r"-100\d+",
                arg.strip()
            ):

                chat_id = int(arg.strip())

                try:
                    files, source_entity = (
                        await download_chat_profile_media(
                            client,
                            chat_id
                        )
                    )

                    if not files:
                        await client.send_message(
                            event.chat_id,
                            "No profile media was found."
                        )

                        return

                    chat_info_id, chat_title = (
                        await get_chat_info(source_entity)
                    )

                    update_download_stats(
                        chat_info_id,
                        chat_title
                    )

                    saved_messages = await client.get_entity("me")

                    for file_path in files:
                        await client.send_file(
                            saved_messages,
                            file_path,
                            caption=(
                                f"Profile media: {chat_title}"
                            )
                        )

                    await client.send_message(
                        event.chat_id,
                        f"{len(files)} profile media files downloaded."
                    )

                    return

                except Exception as error:
                    await client.send_message(
                        event.chat_id,
                        f"Profile media download error: {error}"
                    )

                    return

            # ------------------------------------------------
            # No argument
            # ------------------------------------------------

            if not arg:
                await client.send_message(
                    event.chat_id,
                    "Reply to a media file or use "
                    ".rsave <t.me link>."
                )

                return

            # ------------------------------------------------
            # Mode 3: Download media from Telegram URL
            # ------------------------------------------------

            link_match = re.search(
                r"https?://t\.me/\S+",
                arg
            )

            if not link_match:
                await client.send_message(
                    event.chat_id,
                    "No Telegram t.me link was found "
                    "in the provided argument."
                )

                return

            link = link_match.group(0)

            print(
                f"Telegram link found: {link}"
            )

            try:
                fetched, source_entity = (
                    await fetch_message_from_link(
                        client,
                        link
                    )
                )

            except Exception as error:
                error_message = (
                    f"An error occurred: {error}"
                )

                print(error_message)

                await client.send_message(
                    event.chat_id,
                    error_message
                )

                return

            if not fetched:
                await client.send_message(
                    event.chat_id,
                    "No message was found at the provided link."
                )

                return

            if isinstance(fetched, (list, tuple)):
                fetched = (
                    fetched[0]
                    if fetched
                    else None
                )

            if fetched and getattr(
                fetched,
                "media",
                None
            ) is not None:

                target_msg = fetched

                print(
                    f"Media found from link: "
                    f"message_id={getattr(fetched, 'id', None)}"
                )

            else:
                await client.send_message(
                    event.chat_id,
                    "No media was found in the linked message."
                )

                return

        # ====================================================
        # PREPARE DOWNLOAD DIRECTORY
        # ====================================================

        ensure_dir(DEST_DIR)

        filename = None

        try:
            if (
                getattr(target_msg, "file", None)
                and getattr(
                    target_msg.file,
                    "name",
                    None
                )
            ):
                filename = sanitize_filename(
                    target_msg.file.name
                )

        except Exception:
            filename = None

        # ====================================================
        # GENERATE FILENAME
        # ====================================================

        if not filename:
            extension = ""

            if isinstance(
                target_msg.media,
                MessageMediaPhoto
            ):
                extension = ".jpg"

            elif isinstance(
                target_msg.media,
                MessageMediaDocument
            ):
                mime_type = ""

                if getattr(
                    target_msg,
                    "file",
                    None
                ):
                    mime_type = getattr(
                        target_msg.file,
                        "mime_type",
                        ""
                    )

                mime_type = mime_type.lower()

                if "mp4" in mime_type:
                    extension = ".mp4"

                elif "gif" in mime_type:
                    extension = ".gif"

                elif "webp" in mime_type:
                    extension = ".webp"

                elif (
                    "mpeg" in mime_type
                    or "mp3" in mime_type
                ):
                    extension = ".mp3"

                else:
                    extension = ".bin"

            else:
                extension = ".bin"

            filename = (
                f"msg_{getattr(target_msg, 'id', 'unknown')}"
                f"{extension}"
            )

        # ====================================================
        # UNIQUE DESTINATION
        # ====================================================

        dest_path = unique_path(
            DEST_DIR,
            filename
        )

        print(
            f"Downloading -> {dest_path} ..."
        )

        # ====================================================
        # DOWNLOAD PROGRESS
        # ====================================================

        async def progress_callback(
            current,
            total
        ):
            if total:
                percent = (
                    current / total
                ) * 100

                print(
                    f"Downloading: "
                    f"{percent:.1f}% "
                    f"({current}/{total} bytes)"
                )

        downloaded = await target_msg.download_media(
            file=dest_path,
            progress_callback=progress_callback
        )

        final_path = (
            downloaded
            if (
                downloaded
                and os.path.exists(downloaded)
            )
            else dest_path
        )

        # ====================================================
        # SUCCESS
        # ====================================================

        if os.path.exists(final_path):

            success_message = (
                f"File successfully saved: "
                f"{os.path.basename(final_path)}"
            )

            print(success_message)

            chat_id, chat_title = (
                await get_chat_info(
                    source_entity
                )
            )

            update_download_stats(
                chat_id,
                chat_title
            )

            # Send a copy to Saved Messages.
            try:
                saved_messages = await client.get_entity(
                    "me"
                )

                await client.send_file(
                    saved_messages,
                    final_path,
                    caption=(
                        f"Downloaded from: {chat_title}"
                    )
                )

                print(
                    "File was successfully sent "
                    "to Saved Messages."
                )

            except Exception as error:
                print(
                    f"Saved Messages upload error: {error}"
                )

        # ====================================================
        # DOWNLOAD FAILED
        # ====================================================

        else:
            error_message = (
                f"File was not saved: {final_path}"
            )

            print(error_message)

            await client.send_message(
                event.chat_id,
                error_message
            )

    except Exception as error:

        error_message = (
            f"An unexpected error occurred: {error}"
        )

        print(error_message)

        await client.send_message(
            event.chat_id,
            error_message
        )


# ============================================================
# DOWNLOAD STATISTICS COMMAND
# ============================================================

async def handle_rsinfo(event, client):
    """Show download statistics."""

    try:
        await event.delete()

    except Exception:
        pass

    stats = get_download_stats()

    if not stats:
        message = (
            "No files have been downloaded yet."
        )

    else:
        message = (
            "Download Statistics:\n\n"
        )

        total_downloads = 0

        for index, (
            chat_title,
            count,
            last_download
        ) in enumerate(stats, 1):

            total_downloads += count

            try:
                last_datetime = datetime.strptime(
                    last_download,
                    "%Y-%m-%d %H:%M:%S"
                ).strftime(
                    "%d.%m.%Y %H:%M"
                )

            except Exception:
                last_datetime = str(
                    last_download
                )

            message += (
                f"{index}. {chat_title}: "
                f"{count} time(s) "
                f"(last: {last_datetime})\n"
            )

        message += (
            f"\nTotal: {total_downloads} "
            f"file(s) downloaded."
        )

    await client.send_message(
        event.chat_id,
        message
    )


# ============================================================
# REGISTER
# ============================================================

def register_rsave(client):
    """Register all Telegram Saver commands."""

    # Initialize database when the module is registered.
    init_database()

    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"\.rsave(?:\s+(.+))?$"
        )
    )
    async def rsave_handler(event):
        await handle_rsave(
            event,
            client
        )

    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"\.rsinfo$"
        )
    )
    async def rsinfo_handler(event):
        await handle_rsinfo(
            event,
            client
        )