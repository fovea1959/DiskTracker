from DiskTrackerEntities import *

from sqlalchemy.orm import Session
from sqlalchemy import select, create_engine
from sqlalchemy.engine.result import ScalarResult

engine = create_engine('sqlite:///DiskTracker.db', echo=False)


def volume_by_id(session: Session = None, volume_id: int = None) -> Volume:
    stmt = select(Volume).where(Volume.volume_id == volume_id)
    result = session.scalars(stmt).one()
    return result


def volume_by_name(session: Session = None, volume_name: str = None) -> Volume:
    stmt = select(Volume).where(Volume.volume_name == volume_name)
    result = session.scalars(stmt).one()
    return result


def source_by_name_tuple(session: Session = None, names: tuple = None) -> Source:
    v_id = volume_by_name(session, names[0]).volume_id
    stmt = select(Source).where(
        (Source.source_volume_id == v_id)
        &
        (Source.source_directory == names[1])
    )
    result = session.scalars(stmt).one()
    return result


def destination_by_name_tuple(session: Session = None, names: tuple = None) -> Destination:
    v_id = volume_by_name(session, names[0]).volume_id
    stmt = select(Destination).where(
        (Destination.destination_volume_id == v_id)
        &
        (Destination.destination_directory == names[1])
    )
    result = session.scalars(stmt).one()
    return result


def job_by_id(session: Session = None, job_id: int = None) -> Job:
    stmt = select(Job).where(Job.job_id == job_id)
    result = session.scalars(stmt).one()
    return result


def job_by_name(session: Session = None, job_name: str = None) -> Job:
    stmt = select(Job).where(Job.job_name == job_name)
    result = session.scalars(stmt).one()
    return result


def record_job(session: Session = None,
               job: Job = None,
               operation: str = None,
               when: datetime.datetime = None,
               comment: str = None
               ) -> History:
    h = History()
    h.job_id = job.job_id
    h.job_name = job.job_name
    h.job_description = job.job_description
    h.job_tool = job.job_tool
    h.operation = operation
    h.destination = job.destination
    h.sources = job.sources
    h.when = when
    h.comment = comment
    session.add(h)
    return h


def history_for_job(session: Session = None, job: Job = None) -> ScalarResult[History]:
    stmt = select(History).where(History.job_id == job.job_id)
    result = session.scalars(stmt)
    return result
