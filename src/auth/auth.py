import hashlib
import flask
from flask_login import LoginManager
from flask_login import login_user

import models


def initialize(app):
    loginmanager = LoginManager()
    loginmanager.init_app(app)
    loginmanager.user_loader(load_user)
    loginmanager.login_view = "login"
    loginmanager.login_message = None


def load_user(user_id):
    return models.User.query.filter_by(id=int(user_id)).first()


def login(email, password):
    user = models.User.query.filter_by(email=email).first()

    if not user:
        return False

    enteredPW = hashlib.sha224(password).hexdigest()
    if enteredPW == user.password:
        flask.session['email'] = user.email
        flask.session['name'] = user.name
        flask.session['permissions'] = user.permissions
        flask.session['userid'] = user.id
        login_user(user)
        return True
    return False


def permissions_student(f):
    def decorated_function(*args, **kwargs):
        if flask.session['permissions'] != 10:
            return "Unauthorized", 401
        return f(*args, **kwargs)
    return decorated_function


def permissions_author(f):
    def decorated_function(*args, **kwargs):
        if flask.session['permissions'] < 20:
            return "Unauthorized", 401
        return f(*args, **kwargs)
    return decorated_function


def permissions_admin(f):
    def decorated_function(*args, **kwargs):
        if flask.session['permissions'] < 100 :
            return "Unauthorized", 401
        return f(*args, **kwargs)
    return decorated_function