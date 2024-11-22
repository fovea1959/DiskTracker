import flask
from flask import Flask, render_template, request, url_for, redirect
from sqlalchemy.orm import sessionmaker

import DiskTrackerDao as Dao
import DiskTrackerEntities as E


Session = sessionmaker(bind=Dao.engine)
app = Flask(__name__)


@app.before_request
def create_session():
    flask.g.session = Session()
    print("Made session", flask.g.session)


@app.teardown_appcontext
def shutdown_session(response_or_exc):
    print("Shutdown session", flask.g.session, type(flask.g.session))
    flask.g.session.commit()


@app.route('/')
def index():
    volumes = flask.g.session.query(E.Volume).all()
    print(volumes)
    return render_template('volumes.html', volumes=volumes)


@app.route('/<int:volume_id>/')
def volume(volume_id):
    volumes = flask.g.session.query(E.Volume).all()
    print(volumes)
    return render_template('volumes.html', volumes=volumes)


if __name__ == '__main__':
    app.run(debug=True)
