#coding: utf-8
from __future__ import unicode_literals
from app import db
from hashlib import md5

ROLE_USER = 0
ROLE_ADMIN = 1

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(64), unique = True)
    email = db.Column(db.String(120), unique = True)
    role = db.Column(db.SmallInteger, default = ROLE_USER)
    posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')
    gites = db.relationship('Gite', backref = 'owner', lazy = 'dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def avatar(self,size):
        return 'http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() + '?d=mm&s=' + str(size)

    def __repr__(self):
        return '<User %r>' % (self.nickname)



class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)


class Gite(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(140))
    capacity = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    bookings = db.relationship('Booking', backref = 'giteofbooking', lazy = 'dynamic')

    def countbookings(self):
        return Booking.query.filter_by(Booking.gite_id == self.id).count()


    def __repr__(self):
        return '<Gite %r>' % (self.nickname)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    start = db.Column(db.DATE)
    end = db.Column(db.DATE)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    gite_id = db.Column(db.Integer, db.ForeignKey('gite.id'))

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(140))
    user = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __repr__(self):
        return '<Booking %r>' % (self.id)