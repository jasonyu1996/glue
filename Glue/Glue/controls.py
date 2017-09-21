from Glue.models import User
from flask import request
from Glue.models import User

#def update_user(id, name = None, email = None, 
#               password_hash = None):



def get_user(id):
    return User.query.get(id)

def check_session_token():
    token = request.args.get('token', None)
    if token is None: # no token at all is given
        return None
    return User.get_by_token(token)


