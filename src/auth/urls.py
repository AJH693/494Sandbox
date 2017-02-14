import views


def setup_urls(app):
    app.add_url_rule('/login', view_func=views.LoginView.as_view('login'))
    app.add_url_rule('/logout', view_func=views.LogoutView.as_view('logout'))
    app.add_url_rule('/register', view_func=views.RegisterView.as_view('register'))