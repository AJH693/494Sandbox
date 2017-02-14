import views


def setup_urls(app):
    app.add_url_rule('/course/create', view_func=views.CreateView.as_view('create_course'))
    app.add_url_rule('/course/view/<courseID>', view_func=views.CourseMasterView.as_view('view_course'))
    app.add_url_rule('/course/coursetasklist/<courseID>', view_func=views.CourseTaskListView.as_view('course_task_list'))
    app.add_url_rule('/course/registerForCourse', view_func=views.RegisterForCourseView.as_view('register_course'))
    app.add_url_rule('/course/searchCourseName', view_func=views.SearchCourseName.as_view('search_course_name'))
    app.add_url_rule('/course/securityCode', view_func=views.securityCode.as_view('security_code'))
    app.add_url_rule('/course/addTA', view_func=views.AddTAView.as_view('add_TA'))
    app.add_url_rule('/course/removeTA', view_func=views.RemoveTAView.as_view('remove_TA'))
    app.add_url_rule('/course/archiveCourse/<courseID>', view_func=views.ArchiveCourse.as_view('archive_course'))
    app.add_url_rule('/course/unarchiveCourse/<courseID>', view_func=views.UnarchiveCourse.as_view('unarchive_course'))
