import flask
from flask import redirect
from flask import render_template
from flask import url_for
from flask.views import MethodView
import flask_login
from flask_login import current_user
from flask_login import login_required
import json
import os
import tempfile

from auth import auth
import grading
import models


class ResponseExportView(MethodView):
    decorators = [login_required, auth.permissions_author]

    def get(self, response_id):
        response = models.TaskResponse.query.filter_by(id=response_id).first()
        xml_data = json.loads(response.task.xml_data)
        course = response.task.course
        if course not in current_user.get_courses_where_teacher_or_ta():
            return "Permission Denied", 401
        f = tempfile.TemporaryFile()
        f.write('<?xml version="1.0" encoding="utf-8"?>')
        f.write('\n<decision_matrix name="ResponseMatrix">')
        f.write('\n\t<labels>')
        f.write('\n\t\t<alternatives>')
        for element in xml_data:
            if element['row'] == 0 and element['col'] > 0:
                f.write('\n\t\t\t<alternative>%s</alternative>' % element['text'])
        f.write('\n\t\t</alternatives>')
        f.write('\n\t\t<dimensions>')
        for element in xml_data:
            if element['col'] == 0 and element['row'] > 0:
                f.write('\n\t\t\t<dimension>%s</dimension>' % element['text'])
        f.write('\n\t\t</dimensions>')
        f.write('\n\t</labels>')
        f.write('\n\t<interactions>')
        for interaction in json.loads(response.xml_data):
            for element in xml_data:
                if element.get('id') == interaction['id']:
                    (alternative, dimension) = self.get_alternative_and_dimension(element, xml_data)
                    message = '\n\t\t<info dimension="%s" alternative="%s" timestamp="%.3f" endtime="%.3f" />' % (dimension, alternative, float(interaction['start'])/1000, float(interaction['end'])/1000)
                    f.write(message)
                    break
        f.write('\n\t</interactions>')
        f.write('\n</decision_matrix>')
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(0)
        fn = 'response_%s.xml' % response_id
        response = flask.send_file(f, as_attachment=True, attachment_filename=fn,
                                   add_etags=False)
        return response

    def get_alternative_and_dimension(self, element, xml_data):
        for possible_element in xml_data:
            if possible_element['row'] == element['row'] and possible_element['col'] == 0:
                dimension = possible_element['text']
            elif possible_element['col'] == element['col'] and possible_element['row'] == 0:
                alternative = possible_element['text']
        return (alternative, dimension)


class ResponseView(MethodView):
    decorators = [login_required]

    def get(self, responseID):
        grader = grading.Grader()
        grader.grade_automatic_questions(responseID)
        grader.grade_supplementary_material(responseID)
        task_response = models.TaskResponse.query.filter_by(id=responseID).first()
        course = task_response.task.course
        courses_where_ta = current_user.get_courses_where_ta()
        if task_response.student_id != current_user.id and \
                course not in current_user.get_courses_where_teacher_or_ta():
            return "Permission Denied", 401
        if task_response.student_id == current_user.id and \
                task_response.task.status != "grades published":
            return "Task Not Yet Released"
        formatted_time = task_response.datetime.strftime("%a %b %d %H:%M:%S")
        response = json.loads(task_response.graded_response)
        supplementary = json.loads(task_response.graded_supplementary)
        supplementary_order = json.loads(task_response.supplementary_order)

        return render_template("grading/response.html", response=response,
                               student=task_response.user, task=task_response.task,
                               task_response=task_response, time=formatted_time,
                               supplementary=supplementary,
                               permissions=current_user.permissions,
                               supplementaryOrder=supplementary_order)


class ManualGradingView(MethodView):
    decorators = [login_required, auth.permissions_author]

    def post(self):
        data = flask.request.get_json()
        response_id = data['response_id'].split('?')[0]
        response = models.TaskResponse.query.filter_by(id=response_id).first()
        course = response.task.course
        if course not in current_user.get_courses_where_teacher_or_ta():
            return "Permission Denied", 401
        grader = grading.Grader()
        correctness = grader.grade_manual_question(response_id,
                                                   data['question_id'],
                                                   data['correct'])
        return json.dumps(correctness)


class ManualFeedbackGradingView(MethodView):
    decorators = [login_required, auth.permissions_author]

    def post(self):
        data = flask.request.get_json()
        response_id = data['response_id'].split('?')[0]
        response = models.TaskResponse.query.filter_by(id=response_id).first()
        course = response.task.course
        if course not in current_user.get_courses_where_teacher_or_ta():
            return "Permission Denied", 401
        grader = grading.Grader()
        grader.grade_manual_question(response_id,
                                     data['question_id'],
                                     data['feedback'],
                                     category="feedback")
        models.db.session.commit()
        return ""


class ManualCriticalGradingView(MethodView):
    decorators = [login_required, auth.permissions_author]

    def post(self):
        data = flask.request.get_json()
        response_id = data['response_id'].split('?')[0]
        response = models.TaskResponse.query.filter_by(id=response_id).first()
        course = response.task.course
        if course not in current_user.get_courses_where_teacher_or_ta():
            return "Permission Denied", 401
        grader = grading.Grader()
        grader.grade_manual_question(response_id,
                                     data['question_id'],
                                     data['critical'],
                                     category="critical")
        models.db.session.commit()
        return ""