from flask.ext.sqlalchemy import SQLAlchemy

from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
import random
import hashlib

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
    permissions = db.Column(db.Integer, default=10)
    task_responses = db.relationship('TaskResponse', backref='user',
                                     lazy='dynamic')

    def __init__(self, email, password, name, permissions=10):
        self.email = email
        self.password = hashlib.sha224(password).hexdigest()
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

    def get_courses_where_ta(self):
        courses_where_maybe_ta = Course.query.filter(Course.secondaryTeachers.contains(str(self.id)),
                                                     Course.isArchived==False).all()
        courses_where_ta = []
        for c in courses_where_maybe_ta:
            if str(self.id) in c.secondaryTeachers.split(', '):
                courses_where_ta.append(c)
        return courses_where_ta

    def get_courses_enrolled(self):
        courses = []
        for course in self.courses:
            if not course.isArchived:
                courses.append(course)
        return courses

    def get_courses_where_teacher_or_ta(self):
        courses = []
        if self.permissions >= 100:
            courses = Course.query.all()
        elif self.permissions >= 20:
            courses = Course.query.filter(
                Course.teacher_id==self.id,
                Course.isArchived==False).all()
            courses += self.get_courses_where_ta()
        return courses

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
    isArchived = db.Column(db.Boolean, default=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    secondaryTeachers = db.Column(db.String(255), default="")
    tasks = db.relationship('Task', backref='course', lazy='joined')

    def __init__(self, name, title):
        self.isArchived = False
        self.securityCode = random.randint(100000, 999999)
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

    def set_students(self, student_file):
        try:
            students = []
            lines = student_file.read()
            if "," in lines:
                students = lines.split(",")
            else:
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
    xml_data = db.Column(db.Text())

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
    supplementary_order = db.Column(db.Text)
    graded_supplementary = db.Column(db.Text)
    graded = db.Column(db.Boolean)
    start_time = db.Column(db.DateTime())
    end_time = db.Column(db.DateTime())
    xml_data = db.Column(db.Text())

    def __init__(self, response):
        self.response = response
