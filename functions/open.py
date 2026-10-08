import os
import time

from telethon import events


CODE_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".sh": "bash",
    ".html": "html",
    ".css": "css",
    ".php": "php",
    ".go": "go",
    ".rb": "ruby",
}


def register_open(client):

    # Open and preview a file
    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"\.open$"
        )
    )
    async def open_file(event):

        file_bytes = None
        file_name = "unknown"
        file_size = 0

        # Check replied message
        if event.is_reply:

            reply = await event.get_reply_message()

            if not reply.document:
                return await event.edit(
                    "❌ The replied message is not a file."
                )

            try:
                file_bytes = await reply.download_media(
                    file=bytes
                )
                file_name = reply.file.name or "unknown"
                file_size = len(file_bytes)

            except Exception as e:
                return await event.edit(
                    f"❌ Failed to download file:\n{e}"
                )

        # Find the latest file in the current chat
        else:

            chat = await event.get_chat()

            async for message in client.iter_messages(
                chat,
                limit=10
            ):
                if not message.document:
                    continue

                try:
                    file_bytes = await message.download_media(
                        file=bytes
                    )
                    file_name = (
                        message.file.name
                        or "unknown"
                    )
                    file_size = len(file_bytes)

                    break

                except Exception:
                    continue

            if not file_bytes:
                return await event.edit(
                    "❌ No readable file found in this chat."
                )

        # Show loading status
        try:
            msg = await event.edit(
                f"📖 Reading file: `{file_name}`...",
                parse_mode="markdown"
            )
        except Exception:
            msg = await event.respond(
                f"📖 Reading file: `{file_name}`...",
                parse_mode="markdown"
            )

        try:

            content = file_bytes.decode(
                errors="ignore"
            )

            info_text = (
                f"📄 <b>File:</b> "
                f"<code>{file_name}</code>\n"
                f"📏 <b>Size:</b> "
                f"<code>{file_size} bytes</code>\n"
                f"🕒 <b>Read time:</b> "
                f"<code>{time.strftime('%Y-%m-%d %H:%M:%S')}</code>\n\n"
            )

            _, extension = os.path.splitext(
                file_name.lower()
            )

            # Code file
            if extension in CODE_EXTENSIONS:

                language = CODE_EXTENSIONS[
                    extension
                ]

                if len(content) > 2500:
                    content = (
                        content[:2500]
                        + "\n\n... File is too large to display."
                    )

                content_preview = (
                    f"```{language}\n"
                    f"{content}\n"
                    f"```"
                )

                await msg.edit(
                    info_text + content_preview,
                    parse_mode="markdown"
                )

            # Plain text file
            else:

                if len(content) > 2500:
                    content_preview = (
                        content[:2500]
                        + "\n\n... File is too large to display."
                    )
                else:
                    content_preview = content

                await msg.edit(
                    info_text
                    + f"<code>{content_preview}</code>",
                    parse_mode="html"
                )

        except Exception as e:

            await msg.edit(
                f"❌ Failed to read file:\n{e}"
            )