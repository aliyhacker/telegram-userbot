import requests

from telethon import events

from config import GROQ_API_KEY


GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
CODE_MODEL = "llama-3.1-8b-instant"


SYSTEM_PROMPT = (
    "You are a professional programmer. "
    "Write complete, accurate, and working code. "
    "Return code inside a Markdown code block. "
    "Use the correct language tag when the programming "
    "language is known. "
    "Keep explanations concise."
)


def extract_code(text):
    """
    Extract the first Markdown code block from AI response.
    """

    if "```" not in text:
        return None, text.strip()

    parts = text.split("```")

    if len(parts) < 2:
        return None, text.strip()

    code_block = parts[1].strip()

    # Remove language tag
    first_line, separator, code = code_block.partition("\n")

    known_languages = {
        "python",
        "javascript",
        "typescript",
        "java",
        "c",
        "cpp",
        "csharp",
        "bash",
        "shell",
        "html",
        "css",
        "php",
        "go",
        "rust",
        "ruby",
        "kotlin",
        "swift",
        "sql",
    }

    if separator and first_line.lower() in known_languages:
        code = code.strip()
    else:
        code = code_block

    explanation_parts = []

    if parts[0].strip():
        explanation_parts.append(parts[0].strip())

    if len(parts) > 2 and parts[2].strip():
        explanation_parts.append(parts[2].strip())

    explanation = "\n".join(
        explanation_parts
    )

    return code.strip(), explanation


def register_code(client):

    # AI code generator
    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"\.code(?: |$)(.*)"
        )
    )
    async def code_writer(event):

        query = event.pattern_match.group(1).strip()

        # Use replied message when available
        if event.is_reply:
            reply_msg = await event.get_reply_message()
            user_text = (
                reply_msg.message
                or query
            )
        else:
            user_text = query

        if not user_text.strip():
            return await event.edit(
                "❌ Please enter a coding request "
                "or reply to a message."
            )

        msg = await event.edit(
            "🧠 Generating code..."
        )

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

        payload = {
            "model": CODE_MODEL,
            "messages": messages,
            "max_tokens": 2000,
            "temperature": 0.25
        }

        headers = {
            "Authorization": (
                f"Bearer {GROQ_API_KEY}"
            ),
            "Content-Type": "application/json"
        }

        try:

            response = requests.post(
                GROQ_URL,
                headers=headers,
                json=payload,
                timeout=60
            )

            if response.status_code != 200:
                return await msg.edit(
                    f"❌ API error:\n{response.text}"
                )

            data = response.json()

            answer = (
                data["choices"][0]["message"]["content"]
            )

            code, explanation = extract_code(
                answer
            )

            if not code:
                return await msg.edit(
                    "❌ No code was returned by the AI."
                )

            result = "🧩 <b>Code ready:</b>\n\n"

            if explanation:
                result += (
                    f"{explanation}\n\n"
                )

            result += (
                "```python\n"
                f"{code}\n"
                "```"
            )

            await msg.edit(
                result,
                parse_mode="markdown"
            )

        except Exception as e:
            await msg.edit(
                f"❌ Error:\n{e}"
            )