import re
import json
import hashlib
import auth
import logs
import models

import flask
from flask import redirect
from flask import render_template
from flask import url_for
from flask.views import MethodView
import flask_login
from flask_login import login_required


class LoginView(MethodView):

    def get(self):
        if flask_login.current_user is not None and \
                flask_login.current_user.is_authenticated():
            return redirect(url_for('home'))
        return render_template("login.html", failure=False)

    def post(self):
        data = flask.request.get_json()
        email = data.get('email')
        pw = data.get('password')
        auth.login(email, pw)
        if flask_login.current_user.is_authenticated():
            next_url = flask.request.args.get('next', url_for("home"))
            logger.info("User: %s has logged in" % email)
            return json.dumps({"next_url": next_url})
        return "Failure"


class LogoutView(MethodView):

    def get(self):
        flask_login.logout_user()
        flask.session['email'] = None
        flask.session['name'] = None
        flask.session['permission'] = None
        return redirect(url_for("login"))


class RegisterView(MethodView):

    def get(self):
        return render_template('register.html')

    def post(self):
        data = flask.request.get_json()
        name = data.get('displayName')
        email = data.get('email')
        password = data.get('password')

        user = models.User.query.filter_by(email=email).first()
        if user:
            if user.password:
                return "Failure, user already exists", 401
            else:
                user.password = hashlib.sha224(password).hexdigest()
        else:
            user = models.User(email, password, name)
            models.db.session.add(user)

        models.db.session.commit()

        auth.login(email, password)
        if flask_login.current_user.is_authenticated():
            next_url = flask.request.args.get('next', url_for("home"))
            return json.dumps({"next_url": next_url})
        return render_template("register.html", failure=True)

logger = logs.get_logger()