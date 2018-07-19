import uuid
import os
import datetime
from worker import celery
import celery.states as states

from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template
from forms import SignupForm
from models import Signups
from database import db_session

UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/home/deepblack/projects/python/face-docker/api/uploads')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET_KEY')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/add/<int:param1>/<int:param2>')
def add(param1, param2):
    task = celery.send_task('tasks.add', args=[param1, param2], kwargs={})
    response = "<a href='{url}'>check status of {id} </a>".format(id=task.id,
                                                                  url=url_for('check_task', task_id=task.id, external=True))
    return response


@app.route('/check/<string:task_id>')
def check_task(task_id):
    res = celery.AsyncResult(task_id)
    if res.state == states.PENDING:
        return res.state
    else:
        return str(res.result)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[-1].lower() in ALLOWED_EXTENSIONS


def get_filename():
    return '{}.jpg'.format(str(uuid.uuid4()))


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = get_filename()
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            task = celery.send_task('tasks.mark_faces', args=[filename, ], kwargs={})
            return '''
            <!doctype html>
            <a href="{0}">Get result</a>
            '''.format(url_for('check_task', task_id=task.id, external=True))

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route("/signup", methods=('GET', 'POST'))
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        signup = Signups(name=form.name.data, email=form.email.data, date_signed_up=datetime.datetime.now())
        db_session.add(signup)
        db_session.commit()
        return redirect(url_for('success'))
    return render_template('signup.html', form=form)


@app.route("/success")
def success():
    return "Thank you for signing up!"
