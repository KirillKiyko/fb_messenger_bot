# -*- coding: utf-8 -*-
import ast
import requests
import unicodedata

from flask import Flask, request
from pymessenger.bot import Bot
from answers import get_answer

app = Flask(__name__)
ACCESS_TOKEN = ''
VERIFY_TOKEN = ''
bot = Bot(ACCESS_TOKEN)


# We will receive messages that Facebook sends our bot at this endpoint
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook."""
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    # if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    # Facebook Messenger ID for user so we know where to send response back to
                    recipient_id = message['sender']['id']
                    if message['message'].get('text'):
                        print(message['message'].get('text'), message['sender'].get('id'))
                        print message
                        sender = get_sender_name(message['sender'].get('id'))
                        parse_unicode(message['message'].get('text'))
                        print sender
                        response_sent_text = get_answer(sender, message['message'].get('text'))
                        send_message(recipient_id, response_sent_text)
                    # if user sends us a GIF, photo,video, or any other non-text item
                    if message['message'].get('attachments'):
                        sender = get_sender_name(message['sender'].get('id'))
                        response_sent_nontext = get_answer(sender, message['message'].get('attachments'))
                        send_message(recipient_id, response_sent_nontext)
    return "Message Processed"


def verify_fb_token(token_sent):
    # take token sent by facebook and verify it matches the verify token you sent
    # if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


def parse_unicode(text):
    print unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')


def get_sender_name(sender_id):
    sender_id = unicodedata.normalize('NFKD', sender_id).encode('ascii', 'ignore')

    r = requests.get("https://graph.facebook.com/v2.6/{}?fields=first_name,last_name,profile_pic&access_token={}".format(sender_id, ACCESS_TOKEN))
    r = ast.literal_eval(r.text)

    sender = '{first_name} {last_name}'.format(first_name=r.get('first_name'), last_name=r.get('last_name'))

    return sender

# uses PyMessenger to send response to user
def send_message(recipient_id, response):
    # sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"


if __name__ == "__main__":
    app.run()
