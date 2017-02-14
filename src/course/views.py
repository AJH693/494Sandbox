import flask
from flask import redirect
from flask import render_template
from flask import url_for
from flask.views import MethodView
import flask_login
from flask_login import current_user
from flask_login import login_required
import json

import models
from auth import auth


class CreateView(MethodView):
    decorators = [login_required, auth.permissions_author]

    def get(self):
        return render_template("courseCreation.html")

    def post(self):
        name = flask.request.form.get('name')
        f = flask.request.files.get('students')
        title = flask.request.form.get('title')
        course = models.Course(name, title)
        course.teacher_id = current_user.id
        models.db.session.add(course)
        models.db.session.commit()
        author = models.User.query.filter_by(id=course.teacher_id).first()
        if f:
            course.set_students(f)
        return render_template("course.html", course=course, author=author)


class CourseMasterView(MethodView):
    decorators = [login_required]

    def get(self, courseID):
        course = models.Course.query.filter_by(id=int(courseID) - 1000).first()
        author = models.User.query.filter_by(id=course.teacher_id).first()
        if course in current_user.get_courses_where_teacher_or_ta() or \
                course in current_user.get_courses_enrolled() or current_user.permissions >= 100:
            return render_template("course.html", course=course, author=author)
        else:
            return "You do not have access to view this course", 401


class CourseTaskListView(MethodView):
    decorators = [login_required]

    def get(self, courseID):
        tasks = {'current': [], 'complete': []}
        course = models.Course.query.filter_by(id=int(courseID) - 1000).first()
        userResponseIDs = [tr.task_id for tr in current_user.task_responses]
        for t in course.tasks:
            if t.status == "created" and current_user.id != t.course.teacher_id and current_user.permissions < 100:
                continue
            if(t.id in userResponseIDs):
                tasks['complete'].append(t.serialize)
            else:
                tasks['current'].append(t.serialize)
        tasks['complete'] = sorted(tasks['complete'], key=lambda k: k['duedate'])
        tasks['current'] = sorted(tasks['current'], key=lambda k: k['duedate'])
        return flask.json.dumps(tasks)


class RegisterForCourseView(MethodView):
    decorators = [login_required]

    def get(self):
        return render_template("registerForCourse.html")


class SearchCourseName(MethodView):
    decorators = [login_required]

    def post(self):
        data = flask.request.get_json()
        courseName = data.get('courseName')
        if courseName:
            courses = models.Course.query.filter(
                models.Course.name.contains(courseName),
                models.Course.isArchived == False).all()
        else:
            courses = []
        course_info = [course.serialize for course in courses]
        return json.dumps(course_info)


class ArchiveCourse(MethodView):
    decorators = [login_required, auth.permissions_author]

    def post(self, courseID):
        course = models.Course.query.filter_by(id=int(courseID)).first()
        if course.teacher_id != current_user.id and current_user.permissions < 100:
            return "Permission Denied", 401
        course.isArchived = True
        models.db.session.add(course)
        models.db.session.commit()
        return ""


class UnarchiveCourse(MethodView):
    decorators = [login_required, auth.permissions_author]

    def post(self, courseID):
        course = models.Course.query.filter_by(id=int(courseID)).first()
        if course.teacher_id != current_user.id and current_user.permissions < 100:
            return "Permission Denied", 401
        course.isArchived = False
        models.db.session.add(course)
        models.db.session.commit()
        return ""


class securityCode(MethodView):
    decorators = [login_required]

    def post(self):
        data = flask.request.get_json()
        securityCode = data.get('securityCode')
        courseId = data.get('courseId')
        course = models.Course.query.filter_by(id=courseId).first()
        user_Courses = current_user.courses
        if securityCode == course.securityCode:
            if course in user_Courses:
                return "Already Registered"
            else:
                current_user.courses.append(course)
                models.db.session.commit()
                author = models.User.query.filter_by(id=course.teacher_id).first()
                return "Redirect to:%s" % (url_for("view_course", courseID=course.id+1000))
        else:
            return "Registration Code Incorrect"


class AddTAView(MethodView):
    decorators = [login_required, auth.permissions_author]

    def post(self):
        data = flask.request.get_json()
        email = data.get('email')
        courseId = data.get('courseID')
        course = models.Course.query.filter_by(id=courseId).first()
        if course.teacher_id != current_user.id and current_user.permissions < 100:
            return "error", 401
        if email:
            user = models.User.query.filter(models.User.email.contains(email)).first()
            if user and user.permissions:
                if user.permissions < 20:
                    user.permissions = 20
                secondary_teachers = [t.strip() for t in course.secondaryTeachers.split(",")] if course.secondaryTeachers else []
                secondary_teachers.append(str(user.id))
                course.secondaryTeachers = ", ".join(secondary_teachers)
                models.db.session.commit()
                return email
            else:
                return "error", 400
        else:
            return "error", 400


class RemoveTAView(MethodView):
    decorators = [login_required, auth.permissions_author]

    def post(self):
        data = flask.request.get_json()
        email = data.get('email')
        courseId = data.get('courseID')
        course = models.Course.query.filter_by(id=courseId).first()
        if course.teacher_id != current_user.id and current_user.permissions < 100:
            return "error", 401
        if email:
            user = models.User.query.filter_by(email=email).first()
            if user and user.permissions:
                courses_where_ta = user.get_courses_where_ta()
                if len(courses_where_ta) <= 1 and user.permissions == 20:
                    user.permissions = 10
                secondary_teachers = [t.strip() for t in course.secondaryTeachers.split(",")] if course.secondaryTeachers else []
                if str(user.id) in secondary_teachers:
                    secondary_teachers.remove(str(user.id))
                    course.secondaryTeachers = ", ".join(secondary_teachers)
                else:
                    return "error", 400
                models.db.session.commit()
                return email
            else:
                return "error", 400
        else:
            return "error", 400
