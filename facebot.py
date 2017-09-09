from flask import Flask, request
from pymessenger2.bot import Bot
from mytoken import *
import requests
import json
import ssl
import os


# Initialize the messaging wrapper with our secret access token
bot = Bot(AccessToken)

# set path to our certificates
cert_path = "/etc/letsencrypt/live/thebots.ml/"

# IDs of server admins who can execute commands
admins = ["1111111", "22222222"]


app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def services():
    if request.method == 'GET':
        if request.args.get("hub.mode") == "subscribe":
            # facebook New Page Subscription Call
            if request.args.get("hub.verify_token") == "mypersonalsecret":
                # verification complete
                return request.args.get("hub.challenge")
            else:                # if we got the wrong verification token
                return ("Wrong Secret")
        else:
            # this is not a Facebook Challenge request
            return "Hello, I serve GET requests!"
    if request.method == 'POST':
        # Get facebook request as a JSON structured message
        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for x in messaging:
                if x.get('message'):
                    recipient_id = x['sender']['id']
                    if x['message'].get('text'):
                        message = x['message']['text']
                        '''
                        This is the section where we process our text message
                        Feel free to get crazy here
                        Example 1. lookup a word/phrase from urban dictionary
                        '''
                        if "what is" in message.lower():
                            phrase = message.lower().replace("what is ", "")
                            url = "http://api.urbandictionary.com/v0/define"
                            result = requests.get(url, params={"term": phrase})
                            meaning = result.content
                            meaning = json.loads(meaning.decode('utf8'))
                            try:
                                reply = meaning["list"][0]["definition"]
                            except:
                                reply = "I did not find the meaning of "+phrase
                        # Example 2. exec a command and get the shell output
                        elif "command" in message.lower():
                            # restrict recipient_ids with execution privs
                            if recipient_id in admins:
                                cmd = message.lower().replace("command", "")
                                try:
                                    reply = os.popen(cmd).read()
                                except:
                                    reply = "Error executing a your command"
                            else:
                                reply = "Sorry, your account is not Admin"
                        else:
                            # not a lookup message, we echo back the message :)
                            reply = message
                        # reply with the appropriate response
                        bot.send_text_message(recipient_id, reply)
    return "Success"
if __name__ == "__main__":
    context = (cert_path+"fullchain.pem", cert_path+"privkey.pem")
    app.run(host='0.0.0.0', port=443, ssl_context=context, debug=True)
