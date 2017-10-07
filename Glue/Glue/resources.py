"""
The resources of the API.
"""

from datetime import datetime
from flask import request, url_for
from flask import render_template
from Glue import app, db
from flask.json import jsonify
from Glue.controls import get_user, gen_password_hash, check_session_token
from Glue.models import db, User, Group, likes, user_brief_fields, user_detailed_fields,\
    group_brief_fields, group_detailed_fields
from hashlib import sha512

from flask_restful import marshal, Resource, Api, reqparse

api = Api(app)

class UserResource(Resource):
    def get(self, id): 
        # retrieval of user information
        user = get_user(id)
        if not user:
            return '', 404
        return {'user':marshal(user, user_detailed_fields)}, 200
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
        return {'users': list}

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

        return {'user' : marshal(new_user, user_brief_fields)}, 201

api.add_resource(UserListResource, '/api/v1.0/user/')

class GroupResource(Resource):
    def get(self, id):
        group = Group.query.get(id)
        if group is None:
            # not found
            return '', 404
        return {'group' : marshal(group, group_detailed_fields)}

    def put(self, id):
        # authentication needed
        user = check_session_token()
        if user is None:
            return '', 401
        group = Group.query.get(id)
        if(group is None):
            return '', 404
        if group.leader_id != user.id: # the user is not the leader of the group
            return '', 403

        parser = reqparse.RequestParser()
        parser.add_argument('name')
        parser.add_argument('leader_id', type=int)
        args = parser.parse_args()

        try:
            if args['name'] is not None:
                group.name = args['name']
            if args['leader_id'] is not None:
                group.leader_id = args['leader_id']
            db.session.commit()
        except:
            return '', 400
        return {'group' : marshal(group, group_brief_fields)}, 201
        

api.add_resource(GroupResource, '/api/v1.0/group/<int:id>/')

class GroupListResource(Resource):
    def get(self):
        # TODO: pagination should be added
        res = Group.query.all()
        list = [marshal(group, group_brief_fields) for group in res]
        return {'groups' : list}, 200

    def post(self): # create a new group
         # authentication needed
        user = check_session_token()
        if user is None:
            return '', 401
        parser = reqparse.RequestParser()
        parser.add_argument('leader_id', required=True, type=int,\
           help='The leader_id field is required.')
        parser.add_argument('name', required=True, help='The name field is required.')
        args = parser.parse_args()

        if args['leader_id'] != user.id:
            return '', 403 # not the leader

        try:
            new_group = Group(args['name'], args['leader_id'])
            db.session.add(new_group)
            db.session.commit()
        except:
            return '', 400

        return {'group' : marshal(new_group, group_brief_fields)}, 201


api.add_resource(GroupListResource, '/api/v1.0/group/')

class LikesResource(Resource):
    def post(self, user_id, group_id):
        # add a new like
        # authentication required
        user = check_session_token()
        if user is None:
            return '', 401
        '''
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', required=True, help='The user_id field is required.')
        parser.add_argument('group_id', required=True, help='The group_id field is required.')

        args = parser.parse_args()
        '''

        if user_id != user.id:
            # not the same user
            return '', 403

        group = Group.query.get(group_id)
        if group is None:
            return '', 400

        try:
            user.groups_liked.append(group)
            db.session.commit()
        except:
            return '', 400

        return {'likes' : {
            'group': marshal(group, group_brief_fields), 'user': marshal(user, user_brief_fields)}},\
                201

    def delete(self, user_id, group_id):
        # authentication required
        user = check_session_token()
        if user is None:
            return '', 401
        if user_id != user.id:
            # not the same user
            return '', 403
        group = Group.query.get(group_id)
        if group is None:
            return '', 400
        user.groups_liked.remove(group)
        db.session.commit()

        return {'likes' : {
            'group': marshal(group, group_brief_fields), 'user': marshal(user, user_brief_fields)}},\
                200


api.add_resource(LikesResource, '/api/v1.0/user/<int:user_id>/likes/<int:group_id>/')

'''
class LikesResource(Resource):
    def delete(self, id):
        pass

api.add_resource(LikesResource, '/api/v1.0/likes/<int:id>/')
'''
