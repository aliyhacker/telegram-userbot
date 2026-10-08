import os
import shlex
import subprocess

from telethon import events


# Safe cross-platform aliases
ALIASES = {
    "ll": ["ls", "-la"],
    "la": ["ls", "-la"],
    "ls": ["ls"],
    "pwd": ["pwd"],
    "who": ["whoami"],
    "py": ["python3", "--version"],
    "python": ["python3", "--version"],
    "pip": ["python3", "-m", "pip", "--version"],
    "disk": ["df", "-h"],
    "memory": ["free", "-h"],
    "uptime": ["uptime"],
}


# Commands allowed through .term
ALLOWED_COMMANDS = {
    "ls",
    "pwd",
    "whoami",
    "python3",
    "df",
    "free",
    "uptime",
}


def register_term(client, allowed_users):

    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"\.term(?: (.+))?$"
        )
    )
    async def terminal_cmd(event):

        # Access control
        if event.sender_id not in allowed_users:
            return await event.edit(
                "❌ You are not authorized to use the terminal."
            )

        cmd_text = event.pattern_match.group(1)

        if not cmd_text:
            return await event.edit(
                "❗ Usage: `.term <command>`"
            )

        cmd_text = cmd_text.strip()

        # Alias
        if cmd_text in ALIASES:
            command = ALIASES[cmd_text]
        else:
            try:
                command = shlex.split(cmd_text)
            except ValueError as e:
                return await event.edit(
                    f"❌ Invalid command syntax:\n{e}"
                )

        if not command:
            return await event.edit(
                "❗ Command is empty."
            )

        # Command whitelist
        if command[0] not in ALLOWED_COMMANDS:
            return await event.edit(
                "❌ This command is not allowed."
            )

        await event.edit(
            f"💻 Running: <code>{cmd_text}</code>",
            parse_mode="html"
        )

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=os.getcwd()
            )

            output = result.stdout.strip()
            error = result.stderr.strip()

            if output:
                result_text = output
            elif error:
                result_text = error
            else:
                result_text = (
                    "✅ Command completed successfully. "
                    "No output."
                )

        except subprocess.TimeoutExpired:
            result_text = (
                "❌ Command timed out after 30 seconds."
            )

        except Exception as e:
            result_text = f"❌ Error: {e}"

        # Telegram message limit
        max_len = 3900

        if len(result_text) <= max_len:
            await event.respond(
                f"<code>{result_text}</code>",
                parse_mode="html"
            )
            return

        for i in range(0, len(result_text), max_len):
            chunk = result_text[i:i + max_len]

            await event.respond(
                f"<code>{chunk}</code>",
                parse_mode="html"
            )