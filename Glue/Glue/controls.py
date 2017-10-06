from Glue.models import User
from flask import request
from Glue.models import User
from hashlib import sha512

#def update_user(id, name = None, email = None, 
#               password_hash = None):



def get_user(id):
    return User.query.get(id)

def check_session_token():
    token = request.args.get('token', None)
    if token is None: # no token at all is given
        return None
    return User.get_by_token(token)

def gen_password_hash(pwd):
    pwd_digest = sha512()
    pwd_digest.update(pwd.encode('utf-8'))
    pwd_hash = pwd_digest.digest()

    return pwd_hash



