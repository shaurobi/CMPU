from flask import Flask, request
from CTPU.models import db, Person, Partner, Sendmessage
from flask_migrate import Migrate
import re
import os
import requests

app = Flask(__name__, instance_relative_config=True)
try:
    app.config.from_pyfile('config.py')
except FileNotFoundError:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    app.config['BOTTOKEN'] = os.environ['BOTTOKEN']
    app.config['TUNNEL'] = os.environ['TUNNEL']
    app.config['ADMIN'] = os.environ['ADMIN']
    app.config['WEBHOOK_SECRET'] = os.environ['WEBHOOK_SECRET']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['BOTADDRESS'] = os.environ['BOTADDRESS']
db.init_app(app)
migrate = Migrate(app, db)


def setHeaders():
    accessHdr = 'Bearer ' + app.config['BOTTOKEN']
    headers = {'Authorization': accessHdr, 'Content-Type': 'application/json; charset=utf-8'}
    return(headers)


def sendmessage(header, toPersonEmail, text):
    messageUrl = "https://api.ciscospark.com/v1/messages"
    message = {"roomId": toPersonEmail, "text": text}
    r = requests.post(messageUrl, headers=header, json=message)
    print(r.json)


def send_message_email(header, toPersonEmail, text):
    messageUrl = "https://api.ciscospark.com/v1/messages"
    if toPersonEmail == "all":
        allusers = Person.query.all()
        for person in allusers:
            message = {"toPersonEmail": person.email, "markdown": text}
            print("sending to" + person.email)
            requests.post(messageUrl, headers=header, json=message)
    else:
            message = {"toPersonEmail": toPersonEmail, "text": text}
            requests.post(messageUrl, headers=header, json=message)


def send_message(webhook, message):
    header = setHeaders()
    email = webhook['data']['personEmail']
    roomId = webhook['data']['roomId']
    if email == app.config['ADMIN']:
        messageto = re.search('^(?:\S+\s+){2}(\S+\s+)', message).group(1)
        print(messageto)
        messagecontent = re.search('^(?:\S+\s+){3}(.*)', message).group(1)
        print(messagecontent)
        send_message_email(header, messageto, messagecontent)
    else:
        sendmessage(header, roomId, "not allowed, sod off")

def send(webhook, message):
    header = setHeaders()
    email = webhook['data']['personEmail']
    roomId = webhook['data']['roomId']
    if email == app.config['ADMIN']:
        user = Person.query.filter_by(email=email).first()
        print(user)
        print(user.sendmessage)
        dbstate = user.sendmessage
        if dbstate is None:
            print("in inital method")
            dbstate = Sendmessage("inital")
            db.session.add(dbstate)
            user.sendmessage = dbstate
            print("about to add session")
            db.session.add(user)
            db.session.commit()
            sendmessage(header, roomId, "What user would you like to send a message to?")
        elif dbstate.state == "inital":
            dbstate.to = message
            dbstate.state = "emailadded"
            db.session.add(dbstate)
            db.session.commit()
            sendmessage(header, roomId, "What message would you like to send?")
        elif dbstate.state == "emailadded":
            dbstate.message = message
            dbstate.state = "message added"
            send_message_email(header, dbstate.to, dbstate.message)
            sendmessage(header, roomId, "Message has been sent 🤘")
            db.session.delete(dbstate)
            db.session.commit()
    else:
        sendmessage(header, roomId, "not allowed, sod off")


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
    print(lwebhook)
    for webhook in lwebhook['items']:
        print(webhook['id'])
        requests.delete("https://api.ciscospark.com/v1/webhooks/" + webhook['id'], headers=header)
    message = {"name": "All the messages", "targetUrl": app.config['TUNNEL'], "resource": "messages", "event": "created"}
    response = requests.post(webhookUrl, headers=header, json=message)
    response = response.json()
    return response['id']


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


def list_partners(webhook):
    header = setHeaders()
    email = webhook['data']['personEmail']
    roomId = webhook['data']['roomId']
    if email == app.config['ADMIN']:
        allpartners = Partner.query.all()
        for partner in allpartners:
            sendmessage(header, roomId, partner.domain)
    else:
        sendmessage(header, roomId, "You shall not passssssss")


def add_partner(webhook, message):
    header = setHeaders()
    email = webhook['data']['personEmail']
    roomId = webhook['data']['roomId']
    if email == app.config['ADMIN']:
        domain = re.search('@.+', message).group()
        p = Partner(domain, domain)
        db.session.add(p)
        db.session.commit()
        sendmessage(header, roomId, "have added the partner")
    else:
        sendmessage(header, roomId, "You shall not passssssss")

def add_person(webhook, message):
    header = setHeaders()
    email = webhook['data']['personEmail']
    roomId = webhook['data']['roomId']
    if email == app.config['ADMIN']:
        print(message)
        personto = re.search('^(?:\S+\s+){2}(\S+)', message).group(1)
        print(personto)
        domain = re.search('@.+', personto).group()
        print(domain)
        partner = Partner.query.filter_by(domain=domain).first()
        print(partner)
        p = Person(personto, partner)
        db.session.add(p)
        db.session.commit()
        sendmessage(header, roomId, "have added the person")
    else:
        sendmessage(header, roomId, "You shall not passssssss")


header = setHeaders()
createWebook(header)


@app.route('/listen/', methods=['POST'])
def listener():
    header = setHeaders()
    if request.method == 'POST':
        webhooks = request.get_json()
        if webhooks['data']['personEmail'] != app.config['BOTADDRESS']:
            print(webhooks['id'])
            roomId = webhooks['data']['roomId']
            message = get_message(header, str(webhooks['data']['id']))
            command = message.lower()
            email = webhooks['data']['personEmail']
            user = Person.query.filter_by(email=email).first()
            print(message)
            if command.startswith("cisco"):
                command = message.partition(' ')[2]
            if user is not None and user.sendmessage is not None:
                send(webhooks, message)
                return 'POST'
            elif command == 'register':
                register_user(webhooks)
                return 'POST'
            elif command == 'unregister':
                unregister_user(webhooks)
                return 'POST'
            elif command == 'list registered':
                list_users(webhooks)
                return 'POST'
            elif command == 'list partners':
                list_partners(webhooks)
                return 'POST'
            elif command.startswith("add partner"):
                add_partner(webhooks, message)
                return 'POST'
            elif command.startswith("add person"):
                add_person(webhooks, message)
                return 'POST'
            elif command.startswith("send message"):
                send_message(webhooks, message)
                return 'POST'
            elif command.startswith("send"):
                send(webhooks, message)
                return 'POST'
            elif command == 'help':
                sendmessage(header, roomId, "Howdy, \n \n List of commands that may or may not do things: \n\nregister\nunregister\nlist registered\nadd partner\nsend\nsend message\n\nDont break anything ;)")
                return 'POST'
            else:
                sendmessage(header, roomId, "Hi there!  You have found the Tasmanian Partner Update bot... well done.  If you are a Cisco Partner just type 'register' and if your email domain matches a partner you will start getting updates! How exciting is that!🤘 ")
                message = webhooks['data']['personEmail'] + " sent '" + message + "' to CTPU"
                send_message_email(header, "sidwyer@cisco.com", message)
                return 'POST'
        else:
            return 'go away bot'
    else:
        return 'error'
