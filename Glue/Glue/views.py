"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import request, url_for
from flask import render_template
from Glue import app
from flask.json import jsonify
from Glue.controls import get_user
from Glue.models import db, User

@app.route('/api/v1.0/user/<int:id>', methods = ['GET', 'PUT'])
def api_user(id):
    if request.method == 'GET': # retrieval of user information
        user = get_user(id)
        return jsonify(email = user.email, \
            name = user.name, \
            id = id \
            )
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

@app.route('/api/v1.0/login/', methods = ['GET'])
def api_login(): # retrieves the session token
    email = request.args.get('email', '')
    password_hash = request.args.get('pwd_hash', '')

    user = User.query.filter_by(email=email).first()
    if user.password_hash == password_hash: # the password matches
        return jsonify(token=user.get_token(1000), success=True)
    return jsonify(success=False)


@app.route('/api/v1.0/user/', methods = ['GET'])
def api_user_list(): # retrieves the user list
    # TODO retrieval of the user list
    pass

