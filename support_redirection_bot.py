#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
Copyright (c) 2020 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""


import os
import sys
from urllib.parse import urljoin

from flask import Flask, request

from webexteamssdk import WebexTeamsAPI, Webhook
from config import WEBEX_TEAMS_ACCESS_TOKEN, PORT, WEBHOOK_URL, DESTINATION_SPACE_ID


# Constants
WEBHOOK_NAME = "botWithCardExampleWebhook"
WEBHOOK_URL_SUFFIX = "/events"
MESSAGE_WEBHOOK_RESOURCE = "messages"
MESSAGE_WEBHOOK_EVENT = "created"
CARDS_WEBHOOK_RESOURCE = "attachmentActions"
CARDS_WEBHOOK_EVENT = "created"

# Adaptive Card Design Schema for a sample form.
# To learn more about designing and working with buttons and cards,
# checkout https://developer.webex.com/docs/api/guides/cards
CARD_CONTENT = {
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "type": "AdaptiveCard",
    "version": "1.1",
    "body": [
        {
            "type": "TextBlock",
            "text": "Please type in your requirement: ",
            "size": "medium",
            "weight": "bolder"
        },
        {
            "type": "TextBlock",
            "text": "Enter your request in the following field, an agent will contact you once it is received ",
            "wrap": True
        },
        {
            "type": "Input.Text",
            "placeholder": "Type your requirement HERE",
            "style": "text",
            "maxLength": 0,
            "id": "TextFieldVal"
        },
        
    ],
    "actions": [
        {
            "type": "Action.Submit",
            "title": "Enter",
            "data": {
                "formDemoAction": "Submit"
            }
            
        }
    ]
}

# Module variables
webhook_url = WEBHOOK_URL
port = PORT
access_token = WEBEX_TEAMS_ACCESS_TOKEN
if not all((webhook_url, port, access_token)):
    print(
        """Missing required variable.  You must set:
        * WEBHOOK_URL -- URL for Webex Webhooks (ie: https://2fXX9c.ngrok.io)
        * PORT - Port for Webhook URL (ie: the port param passed to ngrok)
        * WEBEX_TEAMS_ACCESS_TOKEN -- Access token for a Webex bot
        """
    )
    sys.exit()

# Initialize the environment
# Create the web application instance
flask_app = Flask(__name__)
# Create the Webex Teams API connection object
api = WebexTeamsAPI(access_token)
# Get the details for the account who's access token we are using
me = api.people.me()


# Helper functions
def delete_webhooks_with_name():
    """List all webhooks and delete webhooks created by this script."""
    for webhook in api.webhooks.list():
        if webhook.name == WEBHOOK_NAME:
            print("Deleting Webhook:", webhook.name, webhook.targetUrl)
            api.webhooks.delete(webhook.id)


def create_webhooks(webhook_url):
    """Create the Webex Teams webhooks we need for our bot."""
    print("Creating Message Created Webhook...")
    webhook = api.webhooks.create(
        resource=MESSAGE_WEBHOOK_RESOURCE,
        event=MESSAGE_WEBHOOK_EVENT,
        name=WEBHOOK_NAME,
        targetUrl=urljoin(webhook_url, WEBHOOK_URL_SUFFIX)
    )
    print(webhook)
    print("Webhook successfully created.")

    print("Creating Attachment Actions Webhook...")
    webhook = api.webhooks.create(
        resource=CARDS_WEBHOOK_RESOURCE,
        event=CARDS_WEBHOOK_EVENT,
        name=WEBHOOK_NAME,
        targetUrl=urljoin(webhook_url, WEBHOOK_URL_SUFFIX)
    )
    print(webhook)
    print("Webhook successfully created.")


def respond_to_button_press(webhook):
    """Respond to a button press on the card we posted"""

    # Some server side debugging
    room = api.rooms.get(webhook.data.roomId)
    attachment_action = api.attachment_actions.get(webhook.data.id)
    person = api.people.get(attachment_action.personId)
    the_text = attachment_action.inputs['TextFieldVal']
    print("This is the text from the form: ", the_text)
    message_id = attachment_action.messageId
    print(
        f"""
        NEW BUTTON PRESS IN ROOM '{room.title}'
        FROM '{person.displayName}' EMAIL '{person.emails}
        """ 
    )
    api.messages.create(
        room.id,
        parentId=message_id,
        markdown=f"Your request has been received"
    )
    #Now we will send the query to the team space that receives the cases
    if len(person.emails) >= 1:
        the_email = person.emails[0]
    else:
        the_email=''
    
    the_text = 'Request from ' + person.displayName + ' (' + the_email + '): ' + the_text
    api.messages.create(
        DESTINATION_SPACE_ID,
        #parentId=message_id,
        markdown=the_text
    )



def respond_to_message(webhook):
    """Respond to a message to our bot"""

    # Some server side debugging
    room = api.rooms.get(webhook.data.roomId)
    message = api.messages.get(webhook.data.id)
    person = api.people.get(message.personId)
    print(
        f"""
        NEW MESSAGE IN ROOM '{room.title}'
        FROM '{person.displayName}'
        MESSAGE '{message.text}'
        """
    )
    

    # This is a VERY IMPORTANT loop prevention control step.
    # If you respond to all messages...  You will respond to the messages
    # that the bot posts and thereby create a loop condition.
    if message.personId == me.id:
        # Message was sent by me (bot); do not respond.
        return "OK"

    else:
        # Message was sent by someone else; parse message and respond.
        api.messages.create(
            room.id,
            text="Incident reporting Bot:",
        )
        api.messages.create(
            room.id,
            text="If you see this your client cannot render cards",
            attachments=[{
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": CARD_CONTENT
            }],
        )
        return "OK"


# Core bot functionality
# Webex will post to this server when a message is created for the bot
# or when a user clicks on an Action.Submit button in a card posted by this bot
# Your Webex Teams webhook should point to http://<serverip>:<port>/events
@flask_app.route("/events", methods=["POST"])
def webex_teams_webhook_events():
    """Respond to inbound webhook JSON HTTP POST from Webex Teams."""
    # Create a Webhook object from the JSON data
    webhook_obj = Webhook(request.json)

    # Handle a new message event
    if (webhook_obj.resource == MESSAGE_WEBHOOK_RESOURCE
            and webhook_obj.event == MESSAGE_WEBHOOK_EVENT):
        respond_to_message(webhook_obj)

    # Handle an Action.Submit button press event
    elif (webhook_obj.resource == CARDS_WEBHOOK_RESOURCE
          and webhook_obj.event == CARDS_WEBHOOK_EVENT):
        respond_to_button_press(webhook_obj)

    # Ignore anything else (which should never happen
    else:
        print(f"IGNORING UNEXPECTED WEBHOOK:\n{webhook_obj}")

    return "OK"


def main():
    # Delete preexisting webhooks created by this script
    delete_webhooks_with_name()

    create_webhooks(webhook_url)

    try:
        # Start the Flask web server
        flask_app.run(host="0.0.0.0", port=port)

    finally:
        print("Cleaning up webhooks...")
        delete_webhooks_with_name()


if __name__ == "__main__":
    main()
