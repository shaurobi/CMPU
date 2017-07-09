from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


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

    def __init__(self, name, domain):
        self.name = name
        self.domain = domain

    def __repr__(self):
        return '<Partner %r>' % self.name


class Sendmessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    to = db.Column(db.String(120), unique=True)
    message = db.Column(db.String(120), unique=True)
    state = db.Column(db.String(120), unique=True)
    people = db.relationship('Person', backref='sendmessage', lazy='dynamic')

    def __init__(self, state, person):
        self.state = state
        self.people = person

    def __repr__(self):
        return '<Partner %r>' % self.people

