import sys
from datetime import datetime
import logging

import flask
from flask import Flask, render_template, url_for, redirect, request, flash
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.datastructures import MultiDict

from wtforms import Form, validators
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import PasswordField, BooleanField, StringField, HiddenField
from wtforms_alchemy import ModelForm
from wtforms_components import DateTimeField, DateRange

import DiskTrackerDao as Dao
import DiskTrackerEntities
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


def get_db_session():
    # https://flask.palletsprojects.com/en/stable/appcontext/#storing-data
    if 'db' not in flask.g:
        flask.g.db = Session()
        logging.info("Made session %s %s", flask.g.db, type(flask.g.db))

    return flask.g.db


@app.teardown_appcontext
def shutdown_session(response_or_exc):
    db = flask.g.pop('db', None)

    if db is not None:
        logging.info("Commiting session %s %s", db, type(db))
        db.commit()


@app.errorhandler(NoResultFound)
def no_result_found_handler(error):
    return render_template('404.html'), 404


@app.route('/')
def index():
    return redirect(url_for('volumes'))


@app.route('/jobs/')
def jobs():
    data = []
    for j in get_db_session().query(E.Job).all():
        g = G(job=j)
        data.append(g)
    return render_template("jobs.html", job_data=data)


@app.route('/job/<int:job_id>/')
def job(job_id):
    j = Dao.job_by_id(get_db_session(), job_id)
    data = G(job=j)
    return render_template("job.html", job_data=data)


@app.route('/destinations/')
def destinations():
    data = []
    for v in get_db_session().query(E.Destination).all():
        g = G(destination=v)
        data.append(g)
    return render_template('destinations.html', destination_data=data)


@app.route('/destination/<int:destination_id>/')
def destination(destination_id):
    data = G(destination=Dao.destination_by_id(get_db_session(), destination_id))
    return render_template('destination.html', destination_data=data)


@app.route('/sources/')
def sources():
    data = []
    for v in get_db_session().query(E.Source).all():
        g = G(source=v)
        data.append(g)
    return render_template('sources.html', source_data=data)


@app.route('/source/<int:source_id>/')
def source(source_id):
    data = G(source=Dao.source_by_id(get_db_session(), source_id))
    return render_template('source.html', source_data=data)


@app.route('/volumes/')
def volumes():
    data = []
    for v in get_db_session().query(E.Volume).all():
        g = G(volume=v)
        data.append(g)
    return render_template('volumes.html', volume_data=data)


@app.route('/volume/<int:volume_id>/')
def volume(volume_id):
    data = G(volume=Dao.volume_by_id(get_db_session(), volume_id))
    return render_template('volume.html', volume_data=data)


class MyModelForm(ModelForm):
    # https://stackoverflow.com/a/22354293
    def get_session():
        return get_db_session()


class VolumeForm(MyModelForm):
    class Meta:
        model = DiskTrackerEntities.Volume


@app.route('/volume_edit/<int:volume_id>/', methods=['GET', 'POST'])
def volume_edit_test(volume_id):
    s = get_db_session()
    v = Dao.volume_by_id(s, volume_id)
    if request.method == 'POST':
        # https://wtforms-alchemy.readthedocs.io/en/latest/validators.html#using-unique-validator-with-existing-objects
        form = VolumeForm(request.form, obj=v)
        if form.validate():
            form.populate_obj(v)
            flash('Saved!')
            return redirect(url_for('volumes'))
        else:
            pass
    else:  # GET
        form = VolumeForm(obj=v)
        logging.info("made Volume form: %r", form)
    return render_template('volume_edit.html', form=form)


def main():
    app.secret_key = 'super secret key'
    app.run(debug=True)


class CustomLogFormatter(logging.Formatter):
    # derived from https://stackoverflow.com/a/71336115
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name_cache = {}

    def format(self, record):
        saved_name = record.name  # save and restore for other formatters if desired
        abbrev = self.name_cache.get(saved_name, None)
        if abbrev is None:
            parts = saved_name.split('.')
            if len(parts) > 1:
                abbrev = '.'.join(p[0] for p in parts[:-1])
                abbrev = '.'.join((abbrev, parts[-1]))
            else:
                abbrev = saved_name
            self.name_cache[saved_name] = abbrev
        record.name = abbrev
        result = super().format(record)
        return result


if __name__ == '__main__':
    h = logging.StreamHandler(stream=sys.stderr)
    f = CustomLogFormatter("%(asctime)s %(levelname)-8s %(name)-20s %(message)s")
    h.setFormatter(f)
    root = logging.getLogger()
    root.addHandler(h)
    root.setLevel(logging.INFO)
    # need to look at https://stackoverflow.com/a/73094988 to handle access logs

    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.INFO)
    main()
