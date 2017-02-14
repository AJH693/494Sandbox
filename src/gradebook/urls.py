from flask import render_template
import views


def setup_urls(app):
    """URLs for the gradebook functions"""
    app.add_url_rule('/gradebook', view_func=views.GradebookScreenView.as_view('Gradebook'))
    app.add_url_rule('/gradebook/courseGrades/<courseID>', view_func=views.CourseGradeView.as_view('author_grades'))
