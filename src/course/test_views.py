import json
import unittest

from mock import Mock
from mock import patch

import views


class TestRemoveTAView(unittest.TestCase):

    @patch.object(views, "current_user")
    @patch.object(views, "models")
    @patch.object(views, "flask")
    def test_post(self, flask, models, current_user, ):
        data = {
            'email': "email",
            'courseID': 12
        }
        flask.request.get_json.return_value = data
        course = Mock(secondaryTeachers="14", teacher_id=3)
        course.id = 12
        user = Mock(permissions=20)
        user.id = 14
        user.get_courses_where_ta.return_value = ["12"]
        models.Course.query.filter_by.return_value.first.return_value = course
        models.User.query.filter_by.return_value.first.return_value = user
        current_user.id = 3

        ret = views.RemoveTAView().post()
        self.assertEqual(ret, "email")
        self.assertEqual(user.permissions, 10)
        self.assertEqual(course.secondaryTeachers, "")

    @patch.object(views, "current_user")
    @patch.object(views, "models")
    @patch.object(views, "flask")
    def test_already_teacher(self, flask, models, current_user, ):
        data = {
            'email': "email",
            'courseID': 12
        }
        flask.request.get_json.return_value = data
        course = Mock(secondaryTeachers="14", teacher_id=3)
        user = Mock(permissions=50)
        user.id = 14
        user.get_courses_where_ta.return_value = []
        models.Course.query.filter_by.return_value.first.return_value = course
        models.User.query.filter_by.return_value.first.return_value = user
        current_user.id = 3

        ret = views.RemoveTAView().post()
        self.assertEqual(ret, "email")
        self.assertEqual(user.permissions, 50)
        self.assertEqual(course.secondaryTeachers, "")

    @patch.object(views, "current_user")
    @patch.object(views, "models")
    @patch.object(views, "flask")
    def test_perms(self, flask, models, current_user, ):
        data = {
            'email': "email",
            'courseID': 12
        }
        flask.request.get_json.return_value = data
        course = Mock(secondaryTeachers="", teacher_id=3)
        user = Mock(permissions=10)
        user.id = 14
        models.Course.query.filter_by.return_value.first.return_value = course
        models.User.query.filter_by.return_value.first.return_value = user
        current_user.id = 4
        current_user.permissions = 50

        ret = views.RemoveTAView().post()
        self.assertEqual(ret, ("error", 401))
        self.assertEqual(user.permissions, 10)
        self.assertEqual(course.secondaryTeachers, "")

    @patch.object(views, "current_user")
    @patch.object(views, "models")
    @patch.object(views, "flask")
    def test_email(self, flask, models, current_user, ):
        data = {
            'email': "",
            'courseID': 12
        }
        flask.request.get_json.return_value = data
        course = Mock(secondaryTeachers="", teacher_id=3)
        user = Mock(permissions=10)
        user.id = 14
        models.Course.query.filter_by.return_value.first.return_value = course
        models.User.query.filter_by.return_value.first.return_value = user
        current_user.id = 3

        ret = views.RemoveTAView().post()
        self.assertEqual(ret, ("error", 400))
        self.assertEqual(user.permissions, 10)
        self.assertEqual(course.secondaryTeachers, "")

    @patch.object(views, "current_user")
    @patch.object(views, "models")
    @patch.object(views, "flask")
    def test_user(self, flask, models, current_user, ):
        data = {
            'email': "email",
            'courseID': 12
        }
        flask.request.get_json.return_value = data
        course = Mock(secondaryTeachers="", teacher_id=3)
        models.Course.query.filter_by.return_value.first.return_value = course
        models.User.query.filter_by.return_value.first.return_value = None
        current_user.id = 3

        ret = views.RemoveTAView().post()
        self.assertEqual(ret, ("error", 400))
        self.assertEqual(course.secondaryTeachers, "")


class TestAddTAView(unittest.TestCase):

    @patch.object(views, "current_user")
    @patch.object(views, "models")
    @patch.object(views, "flask")
    def test_post(self, flask, models, current_user, ):
        data = {
            'email': "email",
            'courseID': 12
        }
        flask.request.get_json.return_value = data
        course = Mock(secondaryTeachers="", teacher_id=3)
        user = Mock(permissions=10)
        user.id = 14
        models.Course.query.filter_by.return_value.first.return_value = course
        models.User.query.filter.return_value.first.return_value = user
        current_user.id = 3

        ret = views.AddTAView().post()
        self.assertEqual(ret, "email")
        self.assertEqual(user.permissions, 20)
        self.assertEqual(course.secondaryTeachers, "14")

    @patch.object(views, "current_user")
    @patch.object(views, "models")
    @patch.object(views, "flask")
    def test_already_teacher(self, flask, models, current_user, ):
        data = {
            'email': "email",
            'courseID': 12
        }
        flask.request.get_json.return_value = data
        course = Mock(secondaryTeachers="", teacher_id=3)
        user = Mock(permissions=50)
        user.id = 14
        models.Course.query.filter_by.return_value.first.return_value = course
        models.User.query.filter.return_value.first.return_value = user
        current_user.id = 3

        ret = views.AddTAView().post()
        self.assertEqual(ret, "email")
        self.assertEqual(user.permissions, 50)
        self.assertEqual(course.secondaryTeachers, "14")

    @patch.object(views, "current_user")
    @patch.object(views, "models")
    @patch.object(views, "flask")
    def test_perms(self, flask, models, current_user, ):
        data = {
            'email': "email",
            'courseID': 12
        }
        flask.request.get_json.return_value = data
        course = Mock(secondaryTeachers="", teacher_id=3)
        user = Mock(permissions=10)
        user.id = 14
        models.Course.query.filter_by.return_value.first.return_value = course
        models.User.query.filter.return_value.first.return_value = user
        current_user.id = 4
        current_user.permissions = 50

        ret = views.AddTAView().post()
        self.assertEqual(ret, ("error", 401))
        self.assertEqual(user.permissions, 10)
        self.assertEqual(course.secondaryTeachers, "")

    @patch.object(views, "current_user")
    @patch.object(views, "models")
    @patch.object(views, "flask")
    def test_email(self, flask, models, current_user, ):
        data = {
            'email': "",
            'courseID': 12
        }
        flask.request.get_json.return_value = data
        course = Mock(secondaryTeachers="", teacher_id=3)
        user = Mock(permissions=10)
        user.id = 14
        models.Course.query.filter_by.return_value.first.return_value = course
        models.User.query.filter.return_value.first.return_value = user
        current_user.id = 3

        ret = views.AddTAView().post()
        self.assertEqual(ret, ("error", 400))
        self.assertEqual(user.permissions, 10)
        self.assertEqual(course.secondaryTeachers, "")

    @patch.object(views, "current_user")
    @patch.object(views, "models")
    @patch.object(views, "flask")
    def test_user(self, flask, models, current_user, ):
        data = {
            'email': "email",
            'courseID': 12
        }
        flask.request.get_json.return_value = data
        course = Mock(secondaryTeachers="", teacher_id=3)
        models.Course.query.filter_by.return_value.first.return_value = course
        models.User.query.filter.return_value.first.return_value = None
        current_user.id = 3

        ret = views.AddTAView().post()
        self.assertEqual(ret, ("error", 400))
        self.assertEqual(course.secondaryTeachers, "")


class TestArchiveCourse(unittest.TestCase):

    @patch.object(views, "current_user")
    @patch.object(views, "models")
    def test_post(self, models, current_user):
        current_user.id = 12
        course = Mock(teacher_id=12)
        models.Course.query.filter_by.return_value.first.return_value = course
        ret = views.ArchiveCourse().post(1)
        self.assertEqual(ret, "")
        self.assertTrue(models.db.session.commit.called)

    @patch.object(views, "current_user")
    @patch.object(views, "models")
    def test_post_perms(self, models, current_user):
        current_user.id = 12
        current_user.permissions = 50
        course = Mock(teacher_id=11)
        models.Course.query.filter_by.return_value.first.return_value = course
        ret = views.ArchiveCourse().post(1)
        self.assertEqual(ret, ("Permission Denied", 401))
        self.assertFalse(models.db.session.commit.called)


class TestUnarchiveCourse(unittest.TestCase):

    @patch.object(views, "current_user")
    @patch.object(views, "models")
    def test_post(self, models, current_user):
        current_user.id = 12
        course = Mock(teacher_id=12)
        models.Course.query.filter_by.return_value.first.return_value = course
        ret = views.UnarchiveCourse().post(1)
        self.assertEqual(ret, "")
        self.assertTrue(models.db.session.commit.called)

    @patch.object(views, "current_user")
    @patch.object(views, "models")
    def test_post_perms(self, models, current_user):
        current_user.id = 12
        current_user.permissions = 50
        course = Mock(teacher_id=11)
        models.Course.query.filter_by.return_value.first.return_value = course
        ret = views.UnarchiveCourse().post(1)
        self.assertEqual(ret, ("Permission Denied", 401))
        self.assertFalse(models.db.session.commit.called)


class TestSecurityCode(unittest.TestCase):

    @patch.object(views, "url_for")
    @patch.object(views, "current_user")
    @patch.object(views, "models")
    @patch.object(views, "flask")
    def test_security(self, flask, models, current_user, url_for):
        data = {
            'securityCode': "code",
            'courseId': 12,
        }
        c1 = Mock(securityCode="code", id=12)
        current_user.courses = []
        flask.request.get_json.return_value = data
        models.Course.query.filter_by.return_value.first.return_value = c1

        views.securityCode().post()
        self.assertEqual(current_user.courses, [c1])

    @patch.object(views, "url_for")
    @patch.object(views, "current_user")
    @patch.object(views, "models")
    @patch.object(views, "flask")
    def test_bad_code(self, flask, models, current_user, url_for):
        data = {
            'securityCode': "code",
            'courseId': 12,
        }
        c1 = Mock(securityCode="asdf", id=12)
        current_user.courses = []
        flask.request.get_json.return_value = data
        models.Course.query.filter_by.return_value.first.return_value = c1

        ret = views.securityCode().post()
        self.assertEqual(current_user.courses, [])
        self.assertEqual(ret, "Registration Code Incorrect")

    @patch.object(views, "url_for")
    @patch.object(views, "current_user")
    @patch.object(views, "models")
    @patch.object(views, "flask")
    def test_already_reg(self, flask, models, current_user, url_for):
        data = {
            'securityCode': "code",
            'courseId': 12,
        }
        c1 = Mock(securityCode="code", id=12)
        current_user.courses = [c1]
        flask.request.get_json.return_value = data
        models.Course.query.filter_by.return_value.first.return_value = c1

        ret = views.securityCode().post()
        self.assertEqual(current_user.courses, [c1])
        self.assertEqual(ret, "Already Registered")


class TestSearchCourseName(unittest.TestCase):

    @patch.object(views, "models")
    @patch.object(views, "flask")
    def test_post(self, flask, models):
        data = {
            'courseName': "name"
        }
        flask.request.get_json.return_value = data
        c1 = Mock(serialize="")
        models.Course.query.filter.return_value.all.return_value = [c1]
        ret = views.SearchCourseName().post()
        self.assertEqual(ret, json.dumps([""]))


class TestCreateView(unittest.TestCase):

    @patch.object(views, "render_template")
    def test_get(self, render_template):
        views.CreateView().get()
        render_template.assert_called_with("courseCreation.html")

    @patch.object(views, "current_user")
    @patch.object(views, "render_template")
    @patch.object(views, "models")
    @patch.object(views, "flask")
    def test_post(self, flask, models, render_template, current_user):
        flask.request.form = {'name': "MATH-100", 'title': "title"}
        flask.request.files = {'students': "f"}
        course = Mock()
        models.Course.return_value = course
        views.CreateView().post()
        models.Course.assert_called_with("MATH-100", "title")
        self.assertTrue(models.db.session.commit.called)
        course.set_students.assert_called_with("f")


class TestCourseMasterView(unittest.TestCase):

    @patch.object(views, "current_user")
    @patch.object(views, "models")
    @patch.object(views, "render_template")
    def test_get(self, render_template, models, current_user):
        c = Mock()
        models.Course.query.filter_by.return_value.first.return_value = c
        current_user.get_courses_where_teacher_or_ta.return_value = [c]
        views.CourseMasterView().get(11)
        self.assertTrue(render_template.called)
