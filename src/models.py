from flask.ext.sqlalchemy import SQLAlchemy

from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
import random

db = SQLAlchemy()

association_table = db.Table('association', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'))
)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(128))
    courses = db.relationship("Course",
                              secondary=association_table,
                              backref="users")
    coursesTeaching = db.relationship('Course', backref='author',
                                      lazy='dynamic')
    name = db.Column(db.String(255))
    permissions = db.Column(db.Integer, default=1)
    task_responses = db.relationship('TaskResponse', backref='user',
                                     lazy='dynamic')

    def __init__(self, email, password, name, permissions=1):
        self.email = email
        self.password = password
        self.name = name
        self.permissions = permissions
        return

    def get_id(self):
        return str(self.id)

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def is_admin(self):
        return True
    @property
    def serialize(self):
        return {
            'name': self.name
        }


class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    title = db.Column(db.String(255))
    securityCode = db.Column(db.Integer)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tasks = db.relationship('Task', backref='course', lazy='joined')

    def __init__(self, name, title):
        self.securityCode = random.randint(100000,999999)
        self.name = name
        self.title = title
        return

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'teacher_name': self.author.name
        }

    def get_securityCode(self):
        return self.securityCode

    def set_students(self, student_file):
        try:
            students = []
            lines = student_file.read()
            if "," in lines:
                students = lines.split(",")
            elif "\n" in lines:
                students = lines.split("\n")
            elif " " in lines:
                students = lines.split()
            for email in students:
                if "@" not in email:
                    email += "@iastate.edu"
                user = User.query.filter_by(email=email).first()
                if user:
                    if self not in user.courses:
                        user.courses.append(self)
                    else:
                        print "Student already enrolled in course: %s\n" % email
                else:
                    user = User(email, None, None)
                    user.courses.append(self)
                db.session.commit()
        except:
            raise


class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    content = db.Column(db.Text)
    questions = db.Column(db.Text)
    duedate = db.Column(db.DateTime())
    task_responses = db.relationship('TaskResponse', backref='task', lazy='dynamic')
    supplementary = db.Column(db.Text)
    status = db.Column(db.String(20))

    def __init__(self, title):
        self.title = title
        self.status = "created"
        return

    @property
    def serialize(self):
        name = (Course.query.filter_by(id=self.course_id).first()).name if self.course_id else None
        return {
            'id': self.id,
            'title': self.title,
            'duedate': self.duedate,
            'courseName': self.course.name
        }


class TaskResponse(db.Model):
    __tablename__ = "task_response"
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    response = db.Column(db.Text)
    graded_response = db.Column(db.Text)
    datetime = db.Column(db.DateTime())
    correctness_grade = db.Column(db.Float)
    cognitive_grade = db.Column(db.Float)
    supplementary = db.Column(db.Text)
    graded_supplementary = db.Column(db.Text)
    graded = db.Column(db.Boolean)
    start_time = db.Column(db.DateTime())
    end_time = db.Column(db.DateTime())

    def __init__(self, response):
        self.response = response
