import requests

from telethon import events

import config


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
TRANSLATION_MODEL = "dots-studio/dots-3-note-preview:free"


def translate_text(target_lang, text, max_tokens=100):
    headers = {
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": TRANSLATION_MODEL,
        "max_tokens": max_tokens,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a professional translator. "
                    "Convert the requested language to its ISO code "
                    "(english→en, russian→ru, german→de, uzbek→uz). "
                    "Translate the text accurately into that language. "
                    "Return only the translation without explanations."
                )
            },
            {
                "role": "user",
                "content": f"Target language: {target_lang}"
            },
            {
                "role": "user",
                "content": text
            }
        ]
    }

    response = requests.post(
        OPENROUTER_URL,
        headers=headers,
        json=payload,
        timeout=40
    )

    if response.status_code != 200:
        raise RuntimeError(response.text)

    data = response.json()

    return data["choices"][0]["message"]["content"].strip()


def register_translate(client):

    # Translation command
    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"\.tr(?: |$)(.*)"
        )
    )
    async def ai_translate(event):

        args = event.pattern_match.group(1).strip()

        if event.is_reply:

            reply = await event.get_reply_message()

            if not reply.text:
                return await event.edit(
                    "❌ No text found to translate."
                )

            if not args:
                return await event.edit(
                    "❗ Reply translation: <code>.tr language</code>"
                )

            target_lang = args
            text_to_translate = reply.text

        else:

            parts = args.split(" ", 1)

            if len(parts) < 2:
                return await event.edit(
                    "❗ Formats:\n"
                    "• Reply → <code>.tr language</code>\n"
                    "• Without reply → <code>.tr language text</code>"
                )

            target_lang = parts[0]
            text_to_translate = parts[1]

        await event.edit("⌛ Translating...")

        try:
            translated = translate_text(
                target_lang,
                text_to_translate
            )

            await event.edit(translated)

        except Exception as e:
            await event.edit(
                f"❌ Error:\n{e}"
            )

    # Translation without reply
    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"\.tr1 (.+)"
        )
    )
    async def ai_translate_no_reply(event):

        args = event.pattern_match.group(1).strip()

        parts = args.split(" ", 1)

        if len(parts) < 2:
            return await event.edit(
                "❗ Format: <code>.tr1 language text</code>"
            )

        target_lang = parts[0]
        text_to_translate = parts[1]

        await event.edit("⌛ Translating...")

        try:
            translated = translate_text(
                target_lang,
                text_to_translate,
                max_tokens=2000
            )

            await event.edit(translated)

        except Exception as e:
            await event.edit(
                f"❌ Error:\n{e}"
            )