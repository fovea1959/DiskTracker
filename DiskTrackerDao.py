import datetime

import DiskTrackerEntities

from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.engine.result import ScalarResult


class DiskTrackerDao:
    def __init__(self, session: Session = None):
        self.session = session

    def volume_by_name(self, name: str = None):
        stmt = select(DiskTrackerEntities.Volume).where(DiskTrackerEntities.Volume.volume_name == name)
        result = self.session.scalars(stmt).first()
        return result

    def sources(self):
        stmt = select(DiskTrackerEntities.Source)
        resources = self.session.scalars(stmt)
        return resources

    def source_by_name_tuple(self, names: tuple = None):
        v_id = self.volume_by_name(names[0]).volume_id
        stmt = select(DiskTrackerEntities.Source).where(
            (DiskTrackerEntities.Source.source_volume_id == v_id)
            &
            (DiskTrackerEntities.Source.source_directory == names[1])
        )
        result = self.session.scalars(stmt).first()
        return result

    def destinations(self):
        stmt = select(DiskTrackerEntities.Destination)
        resources = self.session.scalars(stmt)
        return resources

    def destination_by_name_tuple(self, names: tuple = None):
        v_id = self.volume_by_name(names[0]).volume_id
        stmt = select(DiskTrackerEntities.Destination).where(
            (DiskTrackerEntities.Destination.destination_volume_id == v_id)
            &
            (DiskTrackerEntities.Destination.destination_directory == names[1])
        )
        result = self.session.scalars(stmt).first()
        return result

    def jobs(self) -> ScalarResult[DiskTrackerEntities.Job]:
        stmt = select(DiskTrackerEntities.Job)
        result = self.session.scalars(stmt)
        return result

    def job_by_name(self, name: str = None):
        stmt = select(DiskTrackerEntities.Job).where(DiskTrackerEntities.Job.job_description == name)
        result = self.session.scalars(stmt).first()
        return result

    def record_job(self,
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
        self.session.add(h)
        return h

    def history_for_job(self, job: DiskTrackerEntities.Job = None) -> ScalarResult[DiskTrackerEntities.History]:
        stmt = select(DiskTrackerEntities.History).where(DiskTrackerEntities.History.job_id == job.job_id)
        result = self.session.scalars(stmt)
        return result
