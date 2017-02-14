import os.path

from flask import Flask
from flask import redirect
from flask import url_for
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import login_required

from auth import auth
from auth import urls as auth_urls
from course import urls as course_urls
from grading import urls as grading_urls
from home import urls as home_urls
from gradebook import urls as gradebook_urls
from taskBuilder import urls as taskBuilder_urls 
from taskBuilder import urls as taskBuilder_urls
import models
from settingslocal import DEBUG_MODE
from settingslocal import RELOADER_BOOL

app = Flask(__name__)
app.debug = DEBUG_MODE
app.config.from_pyfile('settingslocal.py')
toolbar = DebugToolbarExtension(app)

@app.route("/")
#@login_required
def sandbox():
    return redirect(url_for('home'))

auth.initialize(app)
auth_urls.setup_urls(app)
course_urls.setup_urls(app)
grading_urls.setup_urls(app)
home_urls.setup_urls(app)
gradebook_urls.setup_urls(app)
taskBuilder_urls.setup_urls(app)
models.db.init_app(app)

# Initialize sqlite db if necessary (for dev)
with app.test_request_context():
    if not os.path.isfile(app.config['SQLALCHEMY_DATABASE_URI']):
        models.db.create_all()

if __name__ == "__main__":
    app.run(use_reloader=RELOADER_BOOL, host=app.config['SANDBOX_HOST'])
