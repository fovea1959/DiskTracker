from datetime import datetime

import flask
from flask import Flask, render_template, url_for, redirect, request, flash
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.datastructures import MultiDict

from wtforms import Form, validators
from wtforms.fields.simple import PasswordField, BooleanField
from wtforms_components import DateTimeField, DateRange, StringField

import DiskTrackerDao as Dao
import DiskTrackerEntities as E

Session = sessionmaker(bind=Dao.engine)
app = Flask(__name__)


class G:
    def __init__(self, *initial_data, **kwargs):
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])


@app.before_request
def create_session():
    flask.g.session = Session()
    print("Made session", flask.g.session)


@app.teardown_appcontext
def shutdown_session(response_or_exc):
    print("Shutdown session", flask.g.session, type(flask.g.session))
    flask.g.session.commit()


@app.errorhandler(NoResultFound)
def no_result_found_handler(error):
    return render_template('404.html'), 404


@app.route('/')
def index():
    return redirect(url_for('jobs'))


@app.route('/jobs/')
def jobs():
    data = []
    for j in flask.g.session.query(E.Job).all():
        g = G(job=j)
        data.append(g)
    return render_template("jobs.html", job_data=data)


@app.route('/job/<int:job_id>/')
def job(job_id):
    j = Dao.job_by_id(flask.g.session, job_id)
    data = G(job=j)
    return render_template("job.html", job_data=data)


@app.route('/volumes/')
def volumes():
    data = []
    for v in flask.g.session.query(E.Volume).all():
        g = G(volume=v)
        data.append(g)
    return render_template('volumes.html', volume_data=data)


@app.route('/volume/<int:volume_id>/')
def volume(volume_id):
    data = G(volume=Dao.volume_by_id(flask.g.session, volume_id))
    return render_template('volume.html', volume_data=data)


class TestForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])
    date_field = DateTimeField(
        'Date',
        validators=[DateRange(
            min=datetime(2000, 1, 1),
            max=datetime(2000, 10, 10)
        )]
    )


@app.route('/form_test/', methods=['GET', 'POST'])
def form_test():
    form = TestForm(request.form)
    if request.method == 'POST' and form.validate():
        flash('Thanks for registering')
        return redirect(url_for('form_test'))
    return render_template('form_test.html', form=form)



if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug=True)
