from flask import render_template
import views


def setup_urls(app):
    """URLs for the Grading functions"""
    app.add_url_rule('/response/<responseID>', view_func=views.ResponseView.as_view('response'))
    app.add_url_rule('/response/<response_id>/export', view_func=views.ResponseExportView.as_view('response_export'))
    app.add_url_rule('/grading/manual', view_func=views.ManualGradingView.as_view('grade_manually'))
    app.add_url_rule('/grading/critical', view_func=views.ManualCriticalGradingView.as_view('grade_manually_critical'))
    app.add_url_rule('/grading/feedback', view_func=views.ManualFeedbackGradingView.as_view('grade_manually_feedback'))