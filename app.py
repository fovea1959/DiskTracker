import flask
from flask import Flask, render_template, url_for, redirect, abort
from sqlalchemy.orm import sessionmaker

import DiskTrackerDao as Dao
import DiskTrackerEntities as E

Session = sessionmaker(bind=Dao.engine)
app = Flask(__name__)


class G:
    pass


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
    return redirect(url_for('jobs'))


@app.route('/jobs/')
def jobs():
    data = []
    for j in flask.g.session.query(E.Job).all():
        g = G()
        g.job = j
        data.append(g)
    return render_template("jobs.html", job_data=data)


@app.route('/job/<int:job_id>/')
def job(job_id):
    j = Dao.job_by_id(flask.g.session, job_id)
    if j is None:
        abort(404)
    data = G()
    data.job = j
    return render_template("job.html", job_data=data)


@app.route('/volumes/')
def volumes():
    data = []
    for v in flask.g.session.query(E.Volume).all():
        g = G()
        g.volume = v
        data.append(g)
    return render_template('volumes.html', volume_data=data)


@app.route('/volume/<int:volume_id>/')
def volume(volume_id):
    data = flask.g.session.query(E.Volume).all()
    return render_template('volume.html', volumes=data)


if __name__ == '__main__':
    app.run(debug=True)
