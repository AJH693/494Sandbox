import json
import unittest

from mock import Mock
from mock import patch

import grading


class TestGradeSupplementaryMaterial(unittest.TestCase):

    def setUp(self):
        self.response = Mock(graded_supplementary=None)
        self.response.supplementary = json.dumps({
            'supp0': 1
        })
        self.response.task.supplementary = json.dumps({
            'supp0': {
                'time': 2,
                'title': "Supplementary 2"
            }

        })
        models = patch.object(grading, "models")
        self.addCleanup(models.stop)
        self.models = models.start()
        self.models.TaskResponse.query.filter_by.return_value.first.return_value = self.response

    def test_insufficient(self):
        grading.Grader().grade_supplementary_material(2)
        exp = json.dumps([{
            'time': 1,
            'expected_time': 2,
            'sufficient': False,
            'id': "supp0",
            'title': "Supplementary 2"
        }])
        self.assertEqual(exp, self.response.graded_supplementary)
        self.assertEqual(self.response.cognitive_grade, 0)


class TestGradeManualQuestion(unittest.TestCase):

    def setUp(self):
        self.question1 = {
            'questionID': 1
        }
        self.question2 = {
            'questionID': 2
        }
        self.response = Mock()
        self.response.graded_response = json.dumps({
            'manual_questions': [
                self.question1,
                self.question2
            ]
        })
        models = patch.object(grading, "models")
        self.addCleanup(models.stop)
        self.models = models.start()
        self.models.TaskResponse.query.filter_by.return_value.first.return_value = self.response

    def test_correctness(self):
        grader = grading.Grader()
        grader.calculate_correctness = Mock()
        grader.calculate_correctness.return_value = "grade"
        grader.grade_manual_question("notused", 2, False)
        exp = {'manual_questions': [
            {'questionID': 1},
            {'questionID': 2, 'correctness': False}
        ]}
        self.assertEqual(self.response.correctness_grade, "grade")
        self.assertEqual(self.response.graded_response, json.dumps(exp))


class TestGradeAutomaticQuestions(unittest.TestCase):

    def setUp(self):
        models = patch.object(grading, "models")
        self.addCleanup(models.stop)
        self.models = models.start()

    def test_ABD(self):
        grader = grading.Grader()
        taskResponse = Mock()
        taskResponse.graded_response = True
        self.models.TaskResponse.query.filter_by.return_value.first.return_value = taskResponse
        ret = grader.grade_automatic_questions(1)
        self.assertEqual(ret, None)

    def test_ABCEFMPSUV(self):
        grader = grading.Grader()
        taskResponse = Mock()
        taskResponse.graded_response = False
        taskResponse.response = json.dumps({
            'automatic_questions': [],
            'manual_questions': []
            })
        taskResponse.correctness_grade = None
        taskResponse.task = Mock()
        taskResponse.task.questions = json.dumps([])
        self.models.TaskResponse.query.filter_by.return_value.first.return_value = taskResponse
        ret = grader.grade_automatic_questions(1)
        self.assertEqual(taskResponse.correctness_grade, 0)
        self.assertEqual(ret, [])

    def test_has_questions(self):
        trquestion1 = {
            'questionID': 1,
            'correctOption': "A",
            'correctOptionText': "text"
        }
        question1 = {
            'questionID': 1,
            'selectedOption': "A",
        }
        taskResponse = Mock()
        taskResponse.graded_response = False
        taskResponse.response = json.dumps({
            'automatic_questions': [question1],
            'manual_questions': []
        })
        taskResponse.correctness_grade = None
        taskResponse.task = Mock()
        taskResponse.task.questions = json.dumps([trquestion1])
        self.models.TaskResponse.query.filter_by.return_value.first.return_value = taskResponse
        grader = grading.Grader()
        grader.calculate_correctness = Mock()
        grader.calculate_correctness.return_value = "grade"

        ret = grader.grade_automatic_questions(1)
        self.assertEqual(taskResponse.correctness_grade, "grade")
        exp = {
            'questionID': 1,
            'selectedOption': "A",
            'correctOption': "A",
            'correct': True,
            'correctOptionText': "text"
        }
        self.assertEqual(ret, [exp])


class TestCalculateCorrectness(unittest.TestCase):

        def setUp(self):
            models = patch.object(grading, "models")
            self.addCleanup(models.stop)
            self.models = models.start()

        def test_ABCDEGBCDFGBHPRS(self):
            grader = grading.Grader()
            taskResponse = Mock()
            self.models.TaskResponse.query.filter_by.return_value.first.return_value = taskResponse
            taskResponse.graded_response = json.dumps({
                'automatic_questions': [{'correct': True}, {'correct': False}],
                'manual_questions': []
            })
            taskResponse.graded = None
            ret = grader.calculate_correctness(1)
            self.assertEqual(taskResponse.graded, True)
            self.assertEqual(ret, 50)

        def test_ABHIJKMOHPRS(self):
            grader = grading.Grader()
            taskResponse = Mock()
            self.models.TaskResponse.query.filter_by.return_value.first.return_value = taskResponse
            taskResponse.graded_response = json.dumps({
                'automatic_questions': [],
                'manual_questions': [{'correctness': 0}]
            })
            taskResponse.graded = None
            ret = grader.calculate_correctness(1)
            self.assertEqual(taskResponse.graded, True)
            self.assertEqual(ret, 0)

        def test_ABHIJKMNHIJKMNHPQS(self):
            grader = grading.Grader()
            taskResponse = Mock()
            self.models.TaskResponse.query.filter_by.return_value.first.return_value = taskResponse
            taskResponse.graded_response = json.dumps({
                'automatic_questions': [],
                'manual_questions': [{}]
            })
            taskResponse.graded = None
            ret = grader.calculate_correctness(1)
            self.assertEqual(taskResponse.graded, False)
            self.assertEqual(ret, 0)

        def test_ABHIJLMOHIJLMOHPRS(self):
            grader = grading.Grader()
            taskResponse = Mock()
            self.models.TaskResponse.query.filter_by.return_value.first.return_value = taskResponse
            taskResponse.graded_response = json.dumps({
                'automatic_questions': [],
                'manual_questions': [{'correctness': 100}, {'correctness': 100}]
            })
            taskResponse.graded = None
            ret = grader.calculate_correctness(1)
            self.assertEqual(taskResponse.graded, True)
            self.assertEqual(ret,100)