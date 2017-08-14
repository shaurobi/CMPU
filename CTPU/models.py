from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


enrolments = db.Table('enrolments',
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True),
    db.Column('person_id', db.Integer, db.ForeignKey('person.id'), primary_key=True),
    db.Column('attended', db.Boolean, default=False)
)


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    partner_id = db.Column(db.Integer, db.ForeignKey('partner.id'))
    sendmessage_id = db.Column(db.Integer, db.ForeignKey('sendmessage.id'))

    def __init__(self, email, partner):
        self.email = email
        self.partner = partner

    def __repr__(self):
        return '<User %r>' % self.email


class Partner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    domain = db.Column(db.String(50))
    people = db.relationship('Person', backref='partner', lazy='dynamic')
    address = db.Column(db.String(50))

    def __init__(self, name, domain):
        self.name = name
        self.domain = domain

    def __repr__(self):
        return '<Partner %r>' % self.name


class Sendmessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    to = db.Column(db.String(120))
    message = db.Column(db.String(120))
    state = db.Column(db.String(120))
    person = db.relationship('Person', backref='sendmessage', lazy='dynamic')
    conversationType = db.Column(db.String(120))

    def __init__(self, state, conversationType):
        self.state = state
        self.conversationType = conversationType

    def __repr__(self):
        return '<Message %r>' % self.message


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.String(120))
    date = db.Column(db.Date())
    enrolments = db.relationship('Person', secondary=enrolments, lazy='dynamic', backref=db.backref('events', lazy='dynamic'))
    location = db.Column(db.String(120))
    audience = db.Column(db.String(120))
    startTime = db.Column(db.Time())
    finishTime = db.Column(db.Time())

    def __init__(self, name):
        self.name = name

    def __repr__(self):
       return '<Event %r>' % self.name
