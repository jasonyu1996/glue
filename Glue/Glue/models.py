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

# user_brief_list_fields = fields.List(fields.Nested(user_brief_fields))

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String(10))
    email = db.Column(db.String(100), unique = True)
    password_hash = db.Column(db.String(100))

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
