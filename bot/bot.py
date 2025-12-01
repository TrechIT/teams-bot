# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ChannelAccount
import echo_bot.bot.query as query
import re


class MyBot(ActivityHandler):
    # See https://aka.ms/about-bot-activity-message to learn more about the message and other activity types.

    async def on_message_activity(self, turn_context: TurnContext):
        text = turn_context.activity.text.strip().lower()
        ticket_id = None
        match = re.search(r"/ticketid\s*(\d+)", text)
        # if user provided a ticket id, extract it
        if match:
            try:
                ticket_id = int(match.group(1))
            except ValueError:
                await turn_context.send_activity(
                    f"⚠️ Error: Invalid ticket ID provided."
                )
                return
            await turn_context.send_activity(f"Ticket Context Received.")
        try:
            answer = await query.get_response(text, ticket_id)
            await turn_context.send_activity(f"{answer}")
        except Exception as e:
            await turn_context.send_activity(f"⚠️ Error talking to backend: `{e}`")

    async def on_members_added_activity(
        self, members_added: ChannelAccount, turn_context: TurnContext
    ):
        for member_added in members_added:
            if member_added.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Hello and welcome!")
