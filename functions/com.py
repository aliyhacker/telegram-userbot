# by @aliyhacker

from telethon import events
from telethon.tl.types import MessageEntityBlockquote
from telethon.extensions import html
from telethon.helpers import add_surrogate


def register_com(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.com$"))
    async def com_handler(event):

        sections = [
            (
                "<b>🔰 Extra Features:</b>\n"
                "• <code>.echo on/off</code> - Toggle echo mode\n"
                "• <code>.open</code> - Open/read files\n"
                "• <code>.weather</code> - Weather by region\n"
                "• <code>.day</code> - Target/capital information\n"
                "• <code>.clock on/off</code> - Live profile clock\n"
                "• <code>.online on/off</code> - Keep account online\n"
                "• <code>.restart</code> - Restart userbot\n"
                "• <code>.antidel</code> - View deleted messages\n"
                "• <code>.antidel_private on/off</code> - Private chats only\n"
                "• <code>.antidel_all on/off</code> - Enable/disable everywhere\n"
                "• <code>.forward on/off</code> - Forward system\n"
                "• <code>.stik</code> - Text to sticker\n"
                "• <code>.del all</code> - Delete all your messages in the current group\n"
                "• <code>.autocomment @channel &lt;text&gt;</code> - Automatic channel comments\n"
                "• <code>.rsave</code> - Save Telegram media\n"
                "• <code>.rsinfo</code> - Download statistics\n"
                "• <code>.com</code> - Show this list"
            ),

            (
                "<b>💻 Terminal:</b>\n"
                "• <code>.term</code> - Open terminal"
            ),

            (
                "<b>🎭 Animations:</b>\n"
                "• <code>.snow</code> - Snow animation\n"
                "• <code>.police</code> - Police animation\n"
                "• <code>.love</code> - Heart animation\n"
                "• <code>.hack</code> - Hack animation\n"
                "• <code>.whatsup</code> - What's up animation\n"
                "• <code>.glban</code> - Global ban\n"
                "• <code>.unglban</code> - Remove global ban\n"
                "• <code>.banlist</code> - Global ban list\n"
                "• <code>.edit &lt;text&gt;</code> - Text animation"
            ),

            (
                "<b>💬 Chat Features:</b>\n"
                "• <code>.allchat &lt;text&gt;</code> - Send to all chats\n"
                "• <code>.shaxsiychat &lt;text&gt;</code> - Send to private chats\n"
                "• <code>.info me</code> - Send your information to Saved Messages\n"
                "• <code>.info &lt;user_id&gt;</code> - User information\n"
                "• <code>.chatinfo</code> - Group information\n"
                "• <code>.chatinfo me</code> - Send group information to Saved Messages\n"
                "• <code>.staff</code> | <code>.staff me</code> - Group admins"
            ),
            (
                "<b>📚 Education:</b>\n"
                "• <code>.math &lt;expression&gt;</code> - Solve math problems\n"
                "• <code>.tr</code> - Easy translation\n"
                "• <code>.tr1</code> - Translate text only"
            ),

            (
                "<b>🤖 Artificial Intelligence:</b>\n"
                "• <code>.ai</code> - AI response\n"
                "• <code>.ai1</code> - Ask AI using text after .ai1\n"
                "• <code>.aimode</code> - Toggle AI chat mode\n"
                "• <code>.autoreply</code> - Toggle auto-reply\n"
                "• <code>.code</code> - Generate code with AI"
            ),

            (
                "<b>🌐 Diagnostics:</b>\n"
                "• <code>.stats</code> - Userbot statistics\n"
                "• <code>.ping</code> - Check ping\n"
                "• <code>.nettest</code> - Full network diagnostics"
            ),

            (
                "<b>📥 Telegram Restricted Saver:</b>\n"
                "• <code>.rsave</code> - Save replied media\n"
                "• <code>.rsave &lt;t.me link&gt;</code> - Save media from Telegram link\n"
                "• <code>.rsave &lt;-100chat_id&gt;</code> - Download profile media\n"
                "• <code>.rsinfo</code> - Show download statistics"
            ),

            (
                "<b>⚡ Powered by @aliyhacker</b>"
            )
        ]

        final_text = ""
        final_entities = []
        current_offset = 0

        for index, section in enumerate(sections):

            # Convert HTML into real Telegram text + entities
            clean_text, section_entities = html.parse(section)

            # Shift bold/code entities to their correct position
            for entity in section_entities:
                entity.offset += current_offset
                final_entities.append(entity)

            # Telegram uses UTF-16 entity lengths
            section_length = len(add_surrogate(clean_text))

            # Add separate collapsed quote
            final_entities.append(
                MessageEntityBlockquote(
                    offset=current_offset,
                    length=section_length,
                    collapsed=True
                )
            )

            final_text += clean_text
            current_offset += section_length

            # Space between quotes
            if index < len(sections) - 1:
                final_text += "\n\n"
                current_offset += 2

        await event.edit(
            final_text,
            formatting_entities=final_entities
        )