"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import request, url_for
from flask import render_template
from Glue import app, db
from flask.json import jsonify
from Glue.controls import get_user, gen_password_hash, check_session_token
from Glue.models import db, User
from hashlib import sha512

@app.route('/api/v1.0/user/<int:id>/', methods = ['GET', 'PUT'])
def api_user(id):
    if request.method == 'GET': # retrieval of user information
        user = get_user(id)
        if not user:
            return jsonify(sucess = False)
        return jsonify(success = True, user = {
            'email' : user.email, \
            'name' : user.name, \
            'id': id \
            })
    elif request.method == 'PUT': # modification of user information
        # check whether the request is legal
        user = check_session_token()
        if user is None:
            return jsonify(success=False)
        else:
            # modify the values for the user
            name = request.args.get('name', None)
            email = request.args.get('email', None)
            if name is not None:
                user.name = name
            if email is not None:
                user.email = email
            db.session.commit()
            return jsonify(success=True)

@app.route('/api/v1.0/token/', methods = ['POST'])
def api_token(): # retrieves the session token
    email = request.args.get('email', '')
    password = request.args.get('password', '')

    user = User.query.filter_by(email=email).first()

    password_hash = gen_password_hash(password)

    print(password_hash)
    print(user.password_hash)

    if user.password_hash == password_hash: # the password matches
        return jsonify(token=user.get_token(1000).decode('ascii'), success=True)
    return jsonify(success=False)


@app.route('/api/v1.0/user/', methods = ['GET', 'POST'])
def api_user_general(): # retrieves the user list
    # TODO: this is only a temporary solution. No pagination has been considered so far.
    if request.method == 'GET':
        res = User.query.all()
        list = [\
                {'id' : user.id,\
                 'name' : user.name, \
                 'email' : user.email} for user in res]
        return jsonify(list = list)
    elif request.method == 'POST':
        # create a new user
        name = request.args.get('name', '')
        email = request.args.get('email', '')
        pwd = request.args.get('password', '') # not hashed yet

        pwd_hash = gen_password_hash(pwd)

        new_user = User(name, email, pwd_hash)
        db.session.add(new_user)
        db.session.commit()


        return jsonify(success = True, user = {
            'name' : new_user.name,\
            'email' : new_user.email,\
            'id' : new_user.id\
            })

@app.route('/api/v1.0/group/', methods = ['GET', 'POST'])
def api_group_general():
    pass

@app.route('/api/v1.0/group/<int:group_id>/', methods = ['GET', 'PUT'])
def api_group(group_id):
    pass

@app.route('/api/v1.0/likes/', methods = ['GET', 'POST'])
def api_likes_general():
    pass

@app.route('/api/v1.0/likes/<int:likes_id>', methods = ['DELETE'])
def api_likes(likes_id):
    pass
