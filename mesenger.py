from flask import Flask, request
from pymessenger.bot import Bot
from answers import get_answer

app = Flask(__name__)
ACCESS_TOKEN = 'EAABZB7rTDwz0BAOLCagyeTz9owJqZB10man7mbtO0TC5PtnTRbaECWq5ISrwvrmp5tJbhLIlCyfrut7zKV2cewwJZCJMP041sDVcVvNpHBWFM8x8IXySzojkJA1OaZCaTRJB9QNRT39QD6TSfZAhTssDSLil4a6cYOaZCdJkXsZA0orL6DoTUFl'
VERIFY_TOKEN = 'secure_token'
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
                        print(type(message['message'].get('text')))
                        print(message['message'].get('text'))
                        response_sent_text = get_answer(message['message'].get('text'))
                        send_message(recipient_id, response_sent_text)
                    # if user sends us a GIF, photo,video, or any other non-text item
                    if message['message'].get('attachments'):
                        response_sent_nontext = get_answer(message['message'].get('text'))
                        send_message(recipient_id, response_sent_nontext)
    return "Message Processed"


def verify_fb_token(token_sent):
    # take token sent by facebook and verify it matches the verify token you sent
    # if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


# uses PyMessenger to send response to user
def send_message(recipient_id, response):
    # sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"


if __name__ == "__main__":
    app.run()