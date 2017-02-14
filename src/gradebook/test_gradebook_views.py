import json
import unittest

from mock import Mock
from mock import patch

import views

class TestGradebookScreenView(unittest.TestCase):
    def setUp(self):
        models = patch.object(views, "models")
        self.addCleanup(models.stop)
        self.models = models.start()

        current_user = patch.object(views, 'current_user')
        self.addCleanup(current_user.stop)
        self.current_user = current_user.start()

        render_template = patch.object(views, "render_template")
        self.addCleanup(render_template.stop)
        self.render_template = render_template.start()

    def test_student_archived_course_second(self):
        self.current_user.permissions = 10
        task = Mock()
        tasks = [task]
        course = Mock()
        course.isArchived = False
        course.tasks = tasks
        course2 = Mock()
        course2.isArchived = True
        courses = [course,course2]
        self.current_user.courses = courses
        response = Mock()
        self.models.TaskResponse.query.filter.return_value.order_by.return_value.first.return_value = response
        t = {
            'task': task,
            'response': response
        }
        ts = []
        ts.append(t)
        d = {
            'course': course
        }
        d['tasks'] = ts
        data = []
        data.append(d)

        ret = views.GradebookScreenView().get()
        self.assertEqual(courses, self.current_user.courses)
        self.render_template.assert_called_with('studentGradebook.html', courses=courses, tasks=data)

    def test_student_archived_course_first(self):
        self.current_user.permissions = 10
        task = Mock()
        tasks = [task]
        course = Mock()
        course.isArchived = False
        course.tasks = tasks
        course2 = Mock()
        course2.isArchived = True
        courses = [course2,course]
        self.current_user.courses = courses
        response = Mock()
        self.models.TaskResponse.query.filter.return_value.order_by.return_value.first.return_value = response
        t = {
            'task': task,
            'response': response
        }
        ts = []
        ts.append(t)
        d = {
            'course': course
        }
        d['tasks'] = ts
        data = []
        data.append(d)

        ret = views.GradebookScreenView().get()
        self.assertEqual(courses, self.current_user.courses)
        self.render_template.assert_called_with('studentGradebook.html', courses=courses, tasks=data)

    def test_author(self):
        self.current_user.permissions = 20
        t = Mock()
        teaching = [t]
        self.models.Course.query.filter_by.return_value.all.return_value = teaching
        c = Mock()
        courses_where_ta = [c]
        self.current_user.get_courses_where_ta.return_value = courses_where_ta
        teaching += courses_where_ta

        ret = views.GradebookScreenView().get()
        self.render_template.assert_called_with('authorGradebook.html', courses=teaching)

    def test_less_than_student(self):
        self.current_user.permissions = 0

        ret = views.GradebookScreenView().get()
        self.assertEqual(ret, None)



