import flask
from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
from flask.views import MethodView
from flask_login import login_required
import flask_login
from flask_login import current_user
import models
import re
import json
import datetime as DT
import auth
from auth import auth
import os.path
from settingslocal import ADMIN_PASSWORD


class HomeScreenView(MethodView):
    decorators = [login_required]

    def get(self):
        teaching = current_user.get_courses_where_teacher_or_ta()
        enrolled = current_user.get_courses_enrolled()

        return render_template('home.html',
                               courses_enrolled=enrolled,
                               courses_teaching=teaching)


class ClassListView(MethodView):
    def get(self):
        if current_user.is_authenticated():
            courses = current_user.get_courses_enrolled()
            courses += current_user.get_courses_where_teacher_or_ta()
            courses = [c.serialize for c in courses]
            return flask.json.dumps(courses)
        else:
            return flask.json.dumps([])


class DeleteTaskView(MethodView):
    decorators = [login_required, auth.permissions_author]

    def post(self):
        data = flask.request.get_json()
        task = models.Task.query.filter_by(id=int(data['task_id'])).first()
        course = task.course
        if course.teacher_id != current_user.id and current_user.permissions < 100:
            return "Permission Denied", 401
        models.db.session.delete(task)
        models.db.session.commit()
        print "Deleted task " + str(data['task_id'])
        return ""


class TaskListView(MethodView):
    decorators = [login_required]

    def get(self):
        tasks = {'current': [], 'complete': []}
        userResponseIDs = [tr.task_id for tr in current_user.task_responses]
        week_ago = DT.date.today() - DT.timedelta(days=7)
        for c in current_user.courses:
            if c.isArchived:
                continue
            for t in c.tasks:
                if(t.id in userResponseIDs and t.duedate.date() > week_ago and t.status != "created"):
                    tasks['complete'].append(t.serialize)
                elif(t.duedate.date() > week_ago and t.status != "created"):
                    tasks['current'].append(t.serialize)
        tasks['complete'] = sorted(tasks['complete'], key=lambda k: k['duedate'])
        tasks['current'] = sorted(tasks['current'], key=lambda k: k['duedate'])
        return flask.json.dumps(tasks)


class SettingsScreenView(MethodView):
    decorators = [login_required, auth.permissions_author]

    def get(self):
        return render_template("settings.html", failure=False)


class AddAuthorView(MethodView):
    decorators = [login_required, auth.permissions_admin]

    def get(self):
        return

    def post(self):
        data = flask.request.get_json()
        email = data.get('email')
        if email:
            user = models.User.query.filter(models.User.email.contains(email)).first()
            if user and user.permissions:
                if user.permissions < 50:
                    user.permissions = 50
                    models.db.session.commit()
                    return email
                else:
                    return HttpResponse("error", status=400)
            else:
                return HttpResponse("error", status=400)
        else:
            return HttpResponse("error", status=400)


class AddAdminView(MethodView):
    decorators = [login_required, auth.permissions_admin]

    def get(self):
        return

    def post(self):
        data = flask.request.get_json()
        email = data.get('email')
        securityCode = data.get('securityCode')
        if email:
            user = models.User.query.filter(models.User.email.contains(email)).first()
            if user and user.permissions:
                if securityCode == ADMIN_PASSWORD and user.permissions < 100:
                    user.permissions = 100
                    models.db.session.commit()
                    return email
                else:
                    return HttpResponse("error", status=400)
            else:
                return HttpResponse("error", status=400)
        else:
            return HttpResponse("error", status=400)


class RemoveUserView(MethodView):
    decorators = [login_required, auth.permissions_admin]

    def get(self):
        return

    def post(self):
        data = flask.request.get_json()
        email = data.get('email')
        securityCode = data.get('securityCode')
        if email:
            user = models.User.query.filter(models.User.email.contains(email)).first()
            if user and user.permissions:
                if user.permissions == 100:
                    if securityCode == ADMIN_PASSWORD:
                        user.permissions = 10
                    else:
                        return HttpResponse("error", status=400)
                else:
                    user.permissions = 10
                models.db.session.commit()
                return email
            else:
                return HttpResponse("error", status=400)
        else:
            return HttpResponse("error", status=400)
