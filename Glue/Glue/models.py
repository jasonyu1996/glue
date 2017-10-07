from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from Glue import db, app

from flask_restful import fields


user_brief_fields = {\
    'id': fields.Integer,\
    'name': fields.String,\
    'email': fields.String\
   }

group_brief_fields = {\
    'id': fields.Integer,\
    'name': fields.String,\
    'leader': fields.Nested(user_brief_fields)
    }

user_detailed_fields = {\
    'id': fields.Integer, \
    'name': fields.String, \
    'email': fields.String,
    'groups_led': fields.List(fields.Nested(group_brief_fields)),\
    'groups_liked': fields.List(fields.Nested(group_brief_fields))\
    }

group_detailed_fields = {\
    'id': fields.Integer,\
    'name': fields.String,\
    'leader': fields.Nested(user_brief_fields),\
    'users_liking': fields.List(fields.Nested(user_brief_fields))\
    }

# user_brief_list_fields = fields.List(fields.Nested(user_brief_fields))

likes = db.Table('likes', \
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key = True), \
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key = True)\
    )


class Group(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String(50))
    leader_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

    def __init__(self, name, leader_id):
        self.name = name
        self.leader_id = leader_id

    

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String(10))
    email = db.Column(db.String(100), unique = True)
    password_hash = db.Column(db.String(100))

    groups_liked = db.relationship('Group', secondary = likes, \
        backref = db.backref('users_liking', lazy = True))

    groups_led = db.relationship('Group',\
       backref=db.backref('leader', lazy = True))

    def __init__(self, name, email, password_hash):
        self.name = name
        self.email = email
        self.password_hash = password_hash

    
    # generate the session token for this user
    def get_token(self, expiration):
        s = Serializer(app.config['SECRET_KEY'], expiration)
        return s.dumps({'id': str(self.id)})

    @staticmethod
    def get_by_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('ascii'))
        except:
            return None
        id = data['id']

        return User.query.get(id)
