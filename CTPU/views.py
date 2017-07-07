from CTPU import register_user, sendmessage, unregister_user, list_users, get_message, setHeaders
from flask import request


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/listen/', methods=['POST'])
def listener():
    header = setHeaders()
    if request.method == 'POST':
        webhook = request.get_json()
        if webhook['data']['personEmail'] != "CTPU@sparkbot.io":
            roomId = webhook['data']['roomId']
            message = get_message(header, str(webhook['data']['id']))
            if message == 'register':
                register_user(webhook)
                return 'POST'
            elif message == 'unregister':
                unregister_user(webhook)
                return 'POST'
            elif message == 'list registered':
                list_users(webhook)
                return 'POST'
            else:
                sendmessage(header, roomId, "Hi there!  You have found the Tasmanian Partner Update bot... well done.  If you are a Cisco Partner just type 'register' and if your email domain matches a partner you will start getting updates! How exciting is that! ")
                return 'POST'
        else:
            return 'go away bot'
    else:
        return 'error'


@app.route('/sendtest/')
def send_test():
    header = setHeaders()
    sendmessage(header, "sidwyer@cisco.com", "Hey matey")
    return 'sent'