import datetime

import DiskTrackerEntities

from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.engine.result import ScalarResult


def volumes(session: Session = None):
    stmt = select(DiskTrackerEntities.Volume)
    volumes = session.scalars(stmt)
    return volumes


def volume_by_name(session: Session = None, name: str = None):
    stmt = select(DiskTrackerEntities.Volume).where(DiskTrackerEntities.Volume.volume_name == name)
    result = session.scalars(stmt).first()
    return result


def sources(session: Session = None):
    stmt = select(DiskTrackerEntities.Source)
    resources = session.scalars(stmt)
    return resources


def source_by_name_tuple(session: Session = None, names: tuple = None):
    v_id = volume_by_name(session, names[0]).volume_id
    stmt = select(DiskTrackerEntities.Source).where(
        (DiskTrackerEntities.Source.source_volume_id == v_id)
        &
        (DiskTrackerEntities.Source.source_directory == names[1])
    )
    result = session.scalars(stmt).first()
    return result


def destinations(session: Session = None):
    stmt = select(DiskTrackerEntities.Destination)
    resources = session.scalars(stmt)
    return resources


def destination_by_name_tuple(session: Session = None, names: tuple = None):
    v_id = volume_by_name(session, names[0]).volume_id
    stmt = select(DiskTrackerEntities.Destination).where(
        (DiskTrackerEntities.Destination.destination_volume_id == v_id)
        &
        (DiskTrackerEntities.Destination.destination_directory == names[1])
    )
    result = session.scalars(stmt).first()
    return result


def jobs(session: Session = None) -> ScalarResult[DiskTrackerEntities.Job]:
    stmt = select(DiskTrackerEntities.Job)
    result = session.scalars(stmt)
    return result


def job_by_name(session: Session = None, name: str = None):
    stmt = select(DiskTrackerEntities.Job).where(DiskTrackerEntities.Job.job_description == name)
    result = session.scalars(stmt).first()
    return result


def record_job(session: Session = None,
               job: DiskTrackerEntities.Job = None,
               operation: str = None,
               when: datetime.datetime = None
               ) -> DiskTrackerEntities.History:
    h = DiskTrackerEntities.History()
    h.job_id = job.job_id
    h.job_description = job.job_description
    h.job_tool = job.job_tool
    h.operation = operation
    h.destination = job.destination
    h.sources = job.sources
    h.when = when
    session.add(h)
    return h


def history_for_job(session: Session = None, job: DiskTrackerEntities.Job = None) -> ScalarResult[DiskTrackerEntities.History]:
    stmt = select(DiskTrackerEntities.History).where(DiskTrackerEntities.History.job_id == job.job_id)
    result = session.scalars(stmt)
    return result
