"""
The resources of the API.
"""

from datetime import datetime
from flask import request, url_for
from flask import render_template
from Glue import app, db
from flask.json import jsonify
from Glue.controls import get_user, gen_password_hash, check_session_token
from Glue.models import db, User, user_brief_fields
from hashlib import sha512

from flask_restful import marshal, Resource, Api, reqparse

api = Api(app)

class UserResource(Resource):
    def get(self, id): 
        # retrieval of user information
        user = get_user(id)
        if not user:
            return '', 404
        return {'user':marshal(user, user_brief_fields)}, 200
    def put(self, id): # modification of user information
        # check whether the request is legal
        user = check_session_token()
        if user is None or user.id != id:
            return '', 403
        else:
            # modify the values for the user
            parser = reqparse.RequestParser()
            parser.add_argument('name')
            parser.add_argument('email')
            args = parser.parse_args()
            if args['name'] is not None:
                user.name = args['name']
            if args['email'] is not None:
                user.email = args['email']
            db.session.commit()
            return {'user' : marshal(user, user_brief_fields)}, 201

api.add_resource(UserResource, '/api/v1.0/user/<int:id>/')

class TokenResource(Resource):
    def get(self): # retrieves the session token
        email = request.args.get('email', '')
        password = request.args.get('password', '')

        user = User.query.filter_by(email=email).first()

        password_hash = gen_password_hash(password)

        print(password_hash)
        print(user.password_hash)

        if user.password_hash == password_hash: # the password matches
            return {'user':marshal(user, user_brief_fields), 'token':\
                    user.get_token(1000).decode('ascii')}
        return '', 403

api.add_resource(TokenResource, '/api/v1.0/token/')

class UserListResource(Resource):
    # TODO: this is only a temporary solution. No pagination has been considered so far.
    def get(self):
        res = User.query.all()
        list = [marshal(user, user_brief_fields) for user in res]
        return {'list': list}

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', required = True, help='The name field is required.')
        parser.add_argument('email', required = True, help='The email field is required.')
        parser.add_argument('password', required = True, help='The password field is required.')
        args = parser.parse_args()

        # create a new user

        name = args['name']
        email = args['email']
        pwd = args['password']

        pwd_hash = gen_password_hash(pwd)

        new_user = User(name, email, pwd_hash)
        try:
            db.session.add(new_user)
            db.session.commit()
        except:
            return '', 400

        return marshal(new_user, user_brief_fields), 201

api.add_resource(UserListResource, '/api/v1.0/user/')