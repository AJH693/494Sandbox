import json
import unittest

from mock import Mock
from mock import patch

import views

class TestCourseTaskListView(unittest.TestCase): 
    def setUp(self):
        models = patch.object(views, "models")
        self.addCleanup(models.stop)
        self.models = models.start()

        current_user = patch.object(views, 'current_user')
        self.addCleanup(current_user.stop)
        self.current_user = current_user.start()

        flask = patch.object(views, "flask")
        self.addCleanup(flask.stop)
        self.flask = flask.start()

    def test_tasks_has_next_active(self):
        course = Mock(tasks=[])
        tasks = {'current': [], 'complete': []}
        self.models.Course.query.filter_by.return_value.first.return_value = course
        self.current_user.task_responses = []

        ret = views.CourseTaskListView().get(1000)
        self.assertEqual(ret, self.flask.json.dumps(tasks))

    def test_all_clauses_true(self):
        task = self.models.Task
        task.status = ""
        task.id = 1
        task.title = "test"
        task.duedate = "1"
        task.course.name = "test course"
        course = Mock(tasks=[task])
        self.models.Course.query.filter_by.return_value.first.return_value = course
        self.current_user.task_responses = []
        
        tasks = {'current': [], 'complete': []}
        tasks['current'].append(task.serialize)
        ret = views.CourseTaskListView().get(1000)
        self.assertEqual(ret, self.flask.json.dumps(tasks))

    def test_status_as_active(self):
        task = self.models.Task
        task.status = "created"
        task.id = 1
        task.title = "test"
        task.duedate = "1"
        task.course.name = "test course"
        course = Mock(tasks=[task])
        self.models.Course.query.filter_by.return_value.first.return_value = course

        tasks = {'current': [], 'complete': []}
        ret = views.CourseTaskListView().get(1000)
        self.assertEqual(ret, self.flask.json.dumps(tasks))

    def test_id_in_responses_active(self):
        task = self.models.Task
        task.status = ""
        task.id = 1
        task.title = "test"
        task.duedate = "1"
        task.course.name = "test course"
        course = Mock(tasks=[task])
        self.models.Course.query.filter_by.return_value.first.return_value = course
        self.current_user.task_responses = []
        response = Mock(task_id=1)
        self.current_user.task_responses = [response]  

        tasks = {'current': [], 'complete': []}
        tasks['complete'].append(task.serialize)
        ret = views.CourseTaskListView().get(1000)
        self.assertEqual(ret, self.flask.json.dumps(tasks)) 
