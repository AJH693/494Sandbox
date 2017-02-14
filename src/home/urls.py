from flask import render_template
import views

def setup_urls(app):
    """URLs for the Home functions"""

    app.add_url_rule('/home', view_func=views.HomeScreenView.as_view('home'))
    app.add_url_rule('/home/classlist', view_func=views.ClassListView.as_view('class_list'))
    app.add_url_rule('/home/tasklist', view_func=views.TaskListView.as_view('task_list'))
    app.add_url_rule('/settings', view_func=views.SettingsScreenView.as_view('settings'))
    app.add_url_rule('/home/addAuthor', view_func=views.AddAuthorView.as_view('add_Author'))
    app.add_url_rule('/home/addAdmin', view_func=views.AddAdminView.as_view('add_Admin'))
    app.add_url_rule('/home/removeUser', view_func=views.RemoveUserView.as_view('remove_User'))
    app.add_url_rule('/home/deleteTask', view_func=views.DeleteTaskView.as_view('deleteTask'))
    
