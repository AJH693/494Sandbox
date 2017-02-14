ISU Web Portal
===
### Primary Contributors
* Andrew Guibert
* Andrew Hartman
* Jonathan Mielke
* Lucas Rorhet
* Travis Reed 

===
### Resources
* [Trello Board](https://trello.com/b/kPAKvBao/senior-design)
* [Group Website](http://may1518.ece.iastate.edu/)
* [Project Plan](https://drive.google.com/a/iastate.edu/file/d/0B6mbCLySBSQxOUxYQ196eUY5cXc/view?usp=sharing)

### Dev Resources
* [Python Unit Testing](https://docs.python.org/2/library/unittest.html)
* [Python Mocking In Tests](https://docs.python.org/3/library/unittest.mock.html)
* [Flask](http://flask.pocoo.org/)
* [Jinja2](http://jinja.pocoo.org/docs/dev/)
* [Flask-SQLAlchemy](https://pythonhosted.org/Flask-SQLAlchemy/)
* [SQLAlchemy](http://www.sqlalchemy.org/)
* [Bootstrap](http://getbootstrap.com/getting-started/)
* [Jquery](http://api.jquery.com/)

===
### Deplyoment Instructions
Once changes are made in a local development environment, to push changes onto the live server follow these steps:

1.  Run the repackage script which will compress and archive files on your local machine and transfer them to the vrac server<br>
`./repackage.sh build-YYYY-MM-DD <ISU_USERNAME>`<br>

2.  The repackage script will automatically ssh you into the vrac server (once you provide your password) after it moves the new archive onto the server.  Once you are on the vrac server, run the redelploy script on the archive you just created.<br>
`./redeploy.sh build-YYYY-MM-DD`<br>
The redeploy script will tell you which processes to stop if the server is currently running.  Additionally, the script will ask for any DB changes that need to be made in order to deploy the new changes.

===
### Important Files
* models.py: Defines structure of database
* settingslocal.py: Local settings such as passwords
* run_sandbox.py: Starts the application, imports urls and initializes db
* requirements.txt: Lists out dependencies. Can be installed using pip install -Ur requirements.txt
* static/bootstrap3/css/custom-styling.css: Custom CSS

===
### General Structure
Each module has a views.py and a file or folder in templates. Work is done in the view function, then data is passed from the view function to the html, and rendered with jinja.

Decorators exist in auth.auth to restrict access to pages to admins, authors, or students. Additionally, models.py defines functions to get a list of courses a given user can access.

Code that we did not write is stored in the static folder, as are uploads from users.
