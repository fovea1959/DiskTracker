import os

import sqlalchemy
import flask
from flask import Flask, render_template, request, url_for, redirect
from sqlalchemy.orm import sessionmaker

import DiskTrackerDao as Dao
from DiskTrackerEntities import Volume

engine = sqlalchemy.create_engine('sqlite:///DiskTracker.db', echo=True)
Session = sessionmaker(bind=engine)
app = Flask(__name__)


@app.before_request
def create_session():
    flask.g.session = Session()
    print("Made session", flask.g.session)


@app.teardown_appcontext
def shutdown_session(response_or_exc):
    print("Shutdown session", flask.g.session, type(flask.g.session))
    flask.g.session.commit()
    # flask.g.session.remove()


@app.route('/')
def index():
    volumes = Dao.volumes(flask.g.session)
    print(volumes)
    return render_template('volumes.html', volumes=volumes)


@app.route('/<int:volume_id>/')
def volume(volume_id):
    volumes = Dao.volumes(flask.g.session)
    print(volumes)
    return render_template('volumes.html', volumes=volumes)


if __name__ == '__main__':
    app.run()
