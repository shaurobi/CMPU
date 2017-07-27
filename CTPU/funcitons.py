from CTPU import app, db
import re
from CTPU.models import Person, Partner, Sendmessage
import requests

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
    message = {"toPersonEmail": toPersonEmail, "text": text}
    r = requests.post(messageUrl, headers=header, json=message)
    print(r.json)


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
        dbstate = user.messages.first()
        if dbstate is None:
            dbstate = Sendmessage("inital", user)
            db.session.add(dbstate)
            db.session.commit()
            sendmessage(header, roomId, "What user would you like to send a message to?")
        elif dbstate['state'] == "inital":
            dbstate.emailTo = message
            dbstate.state = "emailadded"
            sendmessage(header, roomId, "What message would you like to send?")
        elif dbstate['state'] == "emailadded":
            dbstate.message = message
            dbstate.state = "message added"
            send_message_email(header, dbstate.emailTo, dbstate.message)
            sendmessage(header, roomId, "Message has been sent?")
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