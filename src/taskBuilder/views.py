import flask
from flask import redirect
from flask import render_template
from flask import url_for
from flask.views import MethodView
from flask_login import current_user
from flask_login import login_required
from flask_login import current_user
import traceback
import tempfile
import os
from StringIO import StringIO
from werkzeug import secure_filename
import xlsxwriter

import datetime
import time
import json
import os
import re

import auth
from auth import auth
import config
from grading import grading
import helper_functions
import logs
import models


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS


def get_thumbnail(extension):
    if extension == "pdf":
        return models.Thumbnail.query.filter_by(id=1).first()
    elif extension == "txt":
        return models.Thumbnail.query.filter_by(id=2).first()
    elif extension == "mp3":
        return models.Thumbnail.query.filter_by(id=4).first()
    else:
        return models.Thumbnail.query.filter_by(id=3).first()


def store_task(taskID):
    if taskID == -1:
        task = models.Task("")
    else:
        task = models.Task.query.filter_by(id=int(taskID)).first()
    pattern = r"<script.*?</script>"
    data = flask.request.get_json()
    content = data.get('html')
    courseID = data.get('course_id')
    course = models.Course.query.filter_by(id=courseID).first()
    if course.teacher_id != current_user.id and current_user.permissions < 100:
        return "Permission Denied", 401
    taskTitle = data.get('taskTitle')
    taskDueDate = data.get('taskDue')
    task.title = taskTitle
    task.content = re.sub(pattern, "", content, flags=re.DOTALL)
    task.questions = json.dumps(data.get('questions'))
    task.course = models.Course.query.filter_by(id=courseID).first()
    task.duedate = datetime.datetime.fromtimestamp(taskDueDate/1000.0)
    task.supplementary = json.dumps(data.get('supplementary'))
    task.xml_data = json.dumps(data['xmlData']);
    models.db.session.add(task)
    models.db.session.commit()
    print "Stored task " + str(task.id) + " into db."
    return "Stored task " + str(task.id) + " into db."


class UploadView(MethodView):
    decorators = [login_required, auth.permissions_author]

    def get(self):
        return render_template('upload.html')

    def post(self, userid):
        f = flask.request.files.get('file_path')
        print f
        print f.filename
        print userid
        uploadDir = "src/static/uploads/" + userid
        if not os.path.exists(uploadDir):
            os.makedirs(uploadDir)
        if f and allowed_file(f.filename):
            f.save(os.path.join(uploadDir, f.filename))
            return "Success"
        return "Failed"


class UploadedFileView(MethodView):
    decorators = [login_required]

    def get(self, filename):
        return flask.send_file("static/uploads/" + filename)


class TaskBuilderView(MethodView):
    decorators = [login_required, auth.permissions_author]

    def get(self):
        elements = helper_functions.get_elements()
        return render_template("tasks/taskBuilder.html", elements=elements)

    def post(self):
        print "Creating a new task"
        return store_task(-1)


class TaskBuilderEditView(MethodView):
    decorators = [login_required, auth.permissions_author]

    def get(self, taskID):
        elements = helper_functions.get_elements()
        task = models.Task.query.filter_by(id=int(taskID)).first()
        if task.course.teacher_id != current_user.id and current_user.permissions < 100:
            return "Permission Denied", 401
        return render_template("tasks/taskBuilder.html",
                               elements=elements,
                               old_content=task.content.strip(),
                               supplementary=task.supplementary,
                               task_id=taskID,
                               correct_options=task.questions)

    def post(self, taskID):
        task = models.Task.query.filter_by(id=int(taskID)).first()
        if task.course.teacher_id != current_user.id and current_user.permissions < 100:
            return "Permission Denied", 401
        print "Updating task " + str(taskID)
        return store_task(taskID)


class TaskBuilderCopyView(MethodView):
    decorators = [login_required, auth.permissions_author]

    def get(self, taskID):
        elements = helper_functions.get_elements()
        task = models.Task.query.filter_by(id=int(taskID)).first()
        if task.course.teacher_id != current_user.id and current_user.permissions < 100:
            return "Permission Denied", 401
        return render_template("tasks/taskBuilder.html",
                               elements=elements,
                               old_content=task.content.strip(),
                               supplementary=task.supplementary,
                               correct_options=task.questions)


class TaskTransitionView(MethodView):
    decorators = [login_required, auth.permissions_author]

    def post(self):
        data = flask.request.get_json()
        task = models.Task.query.filter_by(id=data['task_id']).first()
        if task.course.teacher_id != current_user.id and current_user.permissions < 100:
            return "Permission Denied", 401
        task.status = data['status']
        models.db.session.commit()
        return "success"


class TaskView(MethodView):
    decorators = [login_required]

    def get(self, taskID):
        task = models.Task.query.filter_by(id=int(taskID)).first()
        course = models.Course.query.filter_by(id=task.course_id).first()
        html_content = task.content.strip().replace('\n', '')
        secondary_teachers = [t.strip() for t in course.secondaryTeachers.split(",")] if course.secondaryTeachers else []
        if current_user.id == course.teacher_id or str(current_user.id) in secondary_teachers or current_user.permissions >= 100:
            return render_template("tasks/taskAuthorView.html", task=task, course=course)
        elif course.id not in [c.id for c in current_user.courses]:
            return "You are not allowed to see this task", 401
        elif task.status == "available":
            return render_template("tasks/taskStudentView.html", content=html_content)
        else:
            return "This task is no longer available"

    def post(self, taskID):
        try:
            data = flask.request.get_json()
            task_response = models.TaskResponse(json.dumps(data))
            task_response.datetime = datetime.datetime.now()
            task_response.task_id = int(taskID)
            task_response.student_id = current_user.id
            task_response.supplementary = json.dumps(data.get('supplementary'))
            task_response.supplementary_order = json.dumps(data.get('supplementaryOrder'))
            start_time = data.get('startTaskTime')
            end_time = data.get('endTaskTime')
            date_format = "%m/%d/%Y %I:%M:%S %p"
            formatted_s_time = datetime.datetime.strptime(start_time.encode('ascii', 'ignore'), date_format)
            formatted_e_time = datetime.datetime.strptime(end_time.encode('ascii', 'ignore'), date_format)
            task_response.start_time = formatted_s_time
            task_response.end_time = formatted_e_time
            task_response.xml_data = json.dumps(data.get('xmlData'))
            models.db.session.add(task_response)
            models.db.session.commit()
            id = models.TaskResponse.query.order_by(models.TaskResponse.id.desc()).first().id
            grader = grading.Grader()
            grader.grade_automatic_questions(id)
            return "success"
        except:
            logger.critical(traceback.format_exc())
            raise


class TaskExportView(MethodView):
    decorators = [login_required, auth.permissions_author]

    def get(self, taskID):
        task = models.Task.query.filter_by(id=int(taskID)).first()
        supp = json.loads(task.supplementary)
        first_response = models.TaskResponse.query.filter(models.TaskResponse.task_id == taskID,
                                                          models.TaskResponse.graded_response != None).first()
        course = models.Course.query.filter_by(id=task.course_id).first()
        if course.teacher_id != current_user.id and current_user.permissions < 100:
            return "Permission Denied", 401
        date_format = "%m/%d/%Y %I:%M:%S %p"

        output = StringIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        worksheet.write(0, 0, "Student ID")
        worksheet.set_column('A:A', 11)
        worksheet.write(0, 1, "Student Email")
        worksheet.set_column('B:B', 25)
        worksheet.write(0, 2, "Response ID")
        worksheet.set_column('C:C', 11)
        worksheet.write(0, 3, "Response Date")
        worksheet.set_column('D:D', 22)
        worksheet.write(0, 4, "Correctness Grade")
        worksheet.set_column('E:E', 18)
        worksheet.write(0, 5, "Cognitive Grade")
        worksheet.set_column('F:F', 18)
        if first_response:
            response = json.loads(first_response.graded_response)
            for i, manual_question in enumerate(response['manual_questions']):
                worksheet.write(0, 6 + (i * 3), "Manual Question:%s - Response" % manual_question['questionID'])
                worksheet.set_column(6 + (i * 3), 6 + (i * 3), 35)
                worksheet.write(0, 7 + (i * 3), "Manual Question:%s - Correctness" % manual_question['questionID'])
                worksheet.set_column(7 + (i * 3), 7 + (i * 3), 35)
                worksheet.write(0, 8 + (i * 3), "Manual Question:%s - Critical?" % manual_question['questionID'])
                worksheet.set_column(8 + (i * 3), 8 + (i * 3), 35)
            for i, automatic_question in enumerate(response['automatic_questions']):
                worksheet.write(0, 9 + (i * 2), "Automatic Question:%s - Response" % automatic_question['questionID'])
                worksheet.set_column(9 + (i * 2), 9 + (i * 2), 35)
                worksheet.write(0, 10 + (i * 2), "Automatic Question:%s - Correctness" % automatic_question['questionID'])
                worksheet.set_column(10 + (i * 2), 10 + (i * 2), 35)
            for i, key in enumerate(supp.keys()):
                worksheet.write(0, 11 + (i * 4), "Supplementary:%s - Title" % key)
                worksheet.set_column(11 + (i * 4), 11 + (i * 4), 40)
                worksheet.write(0, 12 + (i * 4), "Supplementary:%s - Min Time" % key)
                worksheet.set_column(12 + (i * 4), 12 + (i * 4), 40)
                worksheet.write(0, 13 + (i * 4), "Supplementary:%s - Actual Time" % key)
                worksheet.set_column(13 + (i * 4), 13 + (i * 4), 42)
                worksheet.write(0, 14 + (i * 4), "Supplementary:%s - Sufficient" % key)
                worksheet.set_column(14 + (i * 4), 14 + (i * 4), 42)

        for i, u in enumerate(course.users):
            response = models.TaskResponse.query.filter(
                models.TaskResponse.task_id == taskID,
                models.TaskResponse.student_id == u.id).order_by(
                models.TaskResponse.datetime.desc()).first()
            worksheet.write(i + 1, 0, u.id)
            worksheet.write(i + 1, 1, u.email)
            if response:
                time = response.datetime
                formatted_time = time.strftime(date_format)
                if response.graded_response:
                    response_data = json.loads(response.graded_response)
                else:
                    response_data = {
                        'manual_questions': [],
                        'automatic_questions': []
                    }

                worksheet.write(i + 1, 2, response.id)
                worksheet.write(i + 1, 3, formatted_time)
                worksheet.write(i + 1, 4, response.correctness_grade)
                worksheet.write(i + 1, 5, response.cognitive_grade)
                for j, question in enumerate(response_data['manual_questions']):
                    worksheet.write(i + 1, 6 + (j * 3), question['response'])
                    worksheet.write(i + 1, 7 + (j * 3), question['correctness'])
                    worksheet.write(i + 1, 8 + (j * 3), question['critical'])
                for j, question in enumerate(response_data['automatic_questions']):
                    worksheet.write(i + 1, 9 + (j * 2), question['selectedOptionText'])
                    worksheet.write(i + 1, 10 + (j * 2), question['correct'])
                for j, key in enumerate(supp.keys()):
                    worksheet.write(i + 1, 11 + (j * 4), supp[key]['title'])
                    worksheet.write(i + 1, 12 + (j * 4), supp[key]['time'])
                    if response_data['supplementary'].get(key):
                        sufficient = response_data['supplementary'].get(key) >= supp[key]['time']
                        worksheet.write(i + 1, 13 + (j * 4), response_data['supplementary'].get(key))
                        worksheet.write(i + 1, 14 + (j * 4), sufficient)
                    else:
                        worksheet.write(i + 1, 13 + (j * 4), 0)
                        worksheet.write(i + 1, 14 + (j * 4), False)

        workbook.close()
        xlsx_data = output.getvalue()
        f = tempfile.TemporaryFile()
        f.write(xlsx_data)
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(0)
        fn = 'task_%s.xlsx' % taskID
        response = flask.send_file(f, as_attachment=True, attachment_filename=fn,
                                   add_etags=False)
        return response


class MultipleChoiceView(MethodView):
    decorators = [login_required, auth.permissions_author]

    def get(self):
        return render_template("tasks/elements/multipleChoice.html")


class TrueFalseView(MethodView):
    decorators = [login_required, auth.permissions_author]

    def get(self):
        return render_template("tasks/elements/trueFalse.html")


class FreeResponseView(MethodView):
    decorators = [login_required, auth.permissions_author]

    def get(self):
        return render_template("tasks/elements/freeResponse.html")


class SupplementaryView(MethodView):
    decorators = [login_required, auth.permissions_author]

    def get(self):
        return render_template("tasks/elements/supplementary.html")


class TextContentView(MethodView):
    decorators = [login_required, auth.permissions_author]

    def get(self):
        return render_template("tasks/elements/textContent.html")


class ProblemStatementView(MethodView):
    decorators = [login_required, auth.permissions_author]

    def get(self):
        return render_template("tasks/elements/problemStatement.html")


class CoursesTeachingView(MethodView):

    def get(self):
        courses = current_user.get_courses_where_teacher_or_ta()
        courses = [c.serialize for c in courses]
        return flask.json.dumps(courses)

logger = logs.get_logger()
