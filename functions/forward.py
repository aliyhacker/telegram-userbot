from telethon import events


forward_enabled = False


# ============ Auto Forward ============
def register_forward(client, forwchannel, forwgroup, forwchat):

    @client.on(events.NewMessage(incoming=True))
    async def forward_handler(event):
        global forward_enabled

        if not forward_enabled:
            return

        try:
            if event.is_channel and not event.is_group:
                targets = forwchannel

            elif event.is_group:
                targets = forwgroup

            elif event.is_private:
                targets = forwchat

            else:
                return

            for target in targets:
                await client.forward_messages(
                    target,
                    event.message
                )

        except Exception as e:
            print(f"Forward error: {e}")


    # ============ Forward Toggle ============
    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"\.forward (on|off)"
        )
    )
    async def forward_toggle(event):
        global forward_enabled

        mode = event.pattern_match.group(1)

        if mode == "on":
            forward_enabled = True
            await event.edit("✅ Auto Forward enabled.")

        else:
            forward_enabled = False
            await event.edit("⛔ Auto Forward disabled.")


    # ============ Edit Detector ============
    @client.on(events.MessageEdited(incoming=True))
    async def edit_handler(event):
        if not forward_enabled:
            return

        try:
            if event.is_channel and not event.is_group:
                targets = forwchannel
                tag = "CHANNEL EDIT"

            elif event.is_group:
                targets = forwgroup
                tag = "GROUP EDIT"

            elif event.is_private:
                targets = forwchat
                tag = "CHAT EDIT"

            else:
                return

            original = event.message.text or ""

            msg = (
                f"✏️ <b>{tag}</b>\n\n"
                f"🆕 <b>New content:</b>\n"
                f"{original}\n\n"
                f"🆔 <b>Message ID:</b> {event.message.id}"
            )

            for target in targets:
                await client.send_message(
                    target,
                    msg,
                    parse_mode="html"
                )

        except Exception as e:
            print(f"Edit error: {e}")