from flask import Flask, request
import re
import os
import requests
from CTPU.models import db, Person, Partner

app = Flask(__name__, instance_relative_config=True)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['BOTTOKEN'] = os.environ['BOTTOKEN']
app.config['TUNNEL'] = os.environ['TUNNEL']
app.config['ADMIN'] = os.environ['ADMIN']
app.config.from_pyfile('config.py')
db.init_app(app)


def setHeaders():
    accessHdr = 'Bearer ' + app.config['BOTTOKEN']
    headers = {'Authorization': accessHdr, 'Content-Type': 'application/json; charset=utf-8'}
    return(headers)


def sendmessage(header, toPersonEmail, text):
    messageUrl = "https://api.ciscospark.com/v1/messages"
    message = {"roomId": toPersonEmail, "text": text}
    r = requests.post(messageUrl, headers=header, json=message)
    print(r.json)


def get_message(header, messageId):
    url = "https://api.ciscospark.com/v1/messages/"
    r = requests.get(url + messageId, headers=header)
    r = r.json()
    return r['text']


def register_user(webhook):
    header = setHeaders()
    email = webhook['data']['personEmail']
    roomId = webhook['data']['roomId']
    print(email)
    user = Person.query.filter_by(email=email).first()
    print(user)
    if user is None:
        domain = re.search('@.+', email).group()
        print(domain)
        partner = Partner.query.filter_by(domain=domain).first()
        print(partner.domain)
        u = Person(str(webhook['data']['personEmail']), partner)
        db.session.add(u)
        db.session.commit()
        sendmessage(header, roomId, "You have been registered")
    else:
        sendmessage(header, roomId, "You are already registered... eager beaver!")


def unregister_user(webhook):
    header = setHeaders()
    email = webhook['data']['personEmail']
    roomId = webhook['data']['roomId']
    user = Person.query.filter_by(email=email).first()
    if user is not None:
        db.session.delete(user)
        db.session.commit()
        sendmessage(header, roomId, "You have been unregistered")
    else:
        sendmessage(header, roomId, "You are not registered... maybe you meant to register instead?")
    return


def createWebook(header):
    webhookUrl = "https://api.ciscospark.com/v1/webhooks"
    lwebhook = requests.get("https://api.ciscospark.com/v1/webhooks", headers=header)
    lwebhook = lwebhook.json()
    for webhook in lwebhook['items']:
        requests.delete("https://api.ciscospark.com/v1/webhooks/" + webhook['id'], headers=header)
    message = {"name": "All the messages", "targetUrl": app.config['TUNNEL'], "resource": "messages", "event": "created"}
    r = requests.post(webhookUrl, headers=header, json=message)


def list_users(webhook):
    header = setHeaders()
    email = webhook['data']['personEmail']
    roomId = webhook['data']['roomId']
    if email == app.config['ADMIN']:
        allusers = Person.query.all()
        for person in allusers:
            sendmessage(header, roomId, person.email)
    else:
        domain = re.search('@.+', email).group()
        company = Partner.query.filter_by(domain=domain).first()
        for person in company.people.all():
            sendmessage(header, roomId, person.email)

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