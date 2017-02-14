import json
import unittest

from mock import Mock
from mock import patch

import views


class TestLogoutView(unittest.TestCase):

    @patch.object(views, "url_for")
    @patch.object(views, "redirect")
    @patch.object(views, "flask")
    @patch.object(views, "flask_login")
    def test_get(self, flask_login, flask, redirect, url_for):
        flask.session = {}
        url_for.return_value = "url"

        views.LogoutView().get()
        exp = {
            'email': None,
            'name': None,
            'permission': None
        }
        self.assertEqual(flask.session, exp)
        self.assertTrue(flask_login.logout_user.called)
        redirect.assert_called_with("url")


class TestRegisterView(unittest.TestCase):

    def setUp(self):
        flask_login = patch.object(views, "flask_login")
        self.addCleanup(flask_login.stop)
        self.flask_login = flask_login.start()

        render_template = patch.object(views, "render_template")
        self.addCleanup(render_template.stop)
        self.render_template = render_template.start()

        flask = patch.object(views, "flask")
        self.addCleanup(flask.stop)
        self.flask = flask.start()

        auth = patch.object(views, "auth")
        self.addCleanup(auth.stop)
        self.auth = auth.start()

        models = patch.object(views, "models")
        self.addCleanup(models.stop)
        self.models = models.start()

        url_for = patch.object(views, "url_for")
        self.addCleanup(url_for.stop)
        self.url_for = url_for.start()
        self.url_for.return_value = "home"

        self.data = {
            'displayName': "name",
            'email': "email",
            'emailConfirm': 'email',
            'password': 'password',
            'passwordConfirm': "password"
        }

    def test_register_user_already_exists(self):
        self.flask.request.get_json.return_value = self.data

        user = Mock()
        user.password = "alreadySet"
        self.models.User.query.filter_by.return_value.first.return_value = user

        ret = views.RegisterView().post()
        self.assertEqual(ret, ("Failure, user already exists", 401))

    def test_temp_user_already_exists(self):
        self.flask.request.get_json.return_value = self.data
        self.flask.request.args = {}
        user = Mock()
        user.password = None
        self.models.User.query.filter_by.return_value.first.return_value = user

        ret = views.RegisterView().post()
        self.assertEqual(user.password, "d63dc919e201d7bc4c825630d2cf25fdc93d4b2f0d46706d29038d01")
        self.assertTrue(self.models.db.session.commit.called)

    def test_new_user(self):
        self.flask.request.get_json.return_value = self.data
        self.flask.request.args = {}
        user = Mock(permissions=0)
        self.models.User.return_value = user
        self.models.User.query.filter_by.return_value.first.return_value = None

        ret = views.RegisterView().post()
        self.assertEqual(user.permissions, 0)
        self.assertTrue(self.models.db.session.commit.called)


class TestLoginView(unittest.TestCase):

    def setUp(self):
        flask_login = patch.object(views, "flask_login")
        self.addCleanup(flask_login.stop)
        self.flask_login = flask_login.start()

        redirect = patch.object(views, "redirect")
        self.addCleanup(redirect.stop)
        self.redirect = redirect.start()

        url_for = patch.object(views, "url_for")
        self.addCleanup(url_for.stop)
        self.url_for = url_for.start()
        self.url_for.return_value = "home"

        render_template = patch.object(views, "render_template")
        self.addCleanup(render_template.stop)
        self.render_template = render_template.start()

        flask = patch.object(views, "flask")
        self.addCleanup(flask.stop)
        self.flask = flask.start()

        auth = patch.object(views, "auth")
        self.addCleanup(auth.stop)
        self.auth = auth.start()

        logger = patch.object(views, "logger")
        self.addCleanup(logger.stop)
        self.logger = logger.start()

    def test_post(self):
        data = {
            'email': "travisreed@iastate.edu",
            'password': "pass"
        }
        self.flask.request.get_json.return_value = data
        self.flask.request.args = {'next': "next_url"}

        ret = views.LoginView().post()

        exp = {'next_url': "next_url"}
        self.assertEqual(ret, json.dumps(exp))
        self.auth.login.assert_called_with("travisreed@iastate.edu", "pass")

    def test_post_not_authenticated(self):
        data = {}
        self.flask_login.current_user.is_authenticated.return_value = False

        ret = views.LoginView().post()
        self.assertEqual(ret, "Failure")

    def test_get(self):
        current_user = Mock()
        current_user.is_authenticated.return_value = True
        self.flask_login.current_user = current_user

        views.LoginView().get()
        self.url_for.assert_called_with("home")
        self.redirect.assert_called_with("home")

    def test_get_not_authenticated(self):
        current_user = Mock()
        current_user.is_authenticated.return_value = False
        self.flask_login.current_user = current_user

        views.LoginView().get()
        self.render_template.assert_called_with("login.html", failure=False)
