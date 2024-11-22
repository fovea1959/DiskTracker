import datetime
import typing

import sqlalchemy.orm.exc

from typing import List

from sqlalchemy import Integer, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship
from sqlalchemy.orm.base import Mapped


class Base(DeclarativeBase):
    def _repr(self, **fields: typing.Dict[str, typing.Any]) -> str:
        # Helper for __repr__
        field_strings = []
        at_least_one_attached_attribute = False
        for key, field in fields.items():
            try:
                field_strings.append(f'{key}={field!r}')
            except sqlalchemy.orm.exc.DetachedInstanceError:
                field_strings.append(f'{key}=DetachedInstanceError')
            else:
                at_least_one_attached_attribute = True
        if at_least_one_attached_attribute:
            return f"<{self.__class__.__name__}({','.join(field_strings)})>"
        return f"<{self.__class__.__name__} {id(self)}>"


class Volume(Base):
    __tablename__ = 'volumes'

    volume_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    volume_name: Mapped[str] = mapped_column(Text, unique=True)


class Destination(Base):
    __tablename__ = 'destinations'

    destination_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    destination_volume_id: Mapped[int] = mapped_column(ForeignKey("volumes.volume_id"))
    destination_directory: Mapped[str] = mapped_column(Text)

    destination_volume: Mapped["Volume"] = relationship()

    __table_args__ = (
        UniqueConstraint('destination_volume_id', 'destination_directory', name='_destination_uc'),
    )

    def __repr__(self):
        return self._repr(
            destination_id=self.destination_id,
            path=self.destination_volume.volume_name + self.destination_directory
        )


class SourceHistoryAssociation(Base):
    __tablename__ = "history_sources"
    history_id: Mapped[int] = mapped_column(ForeignKey("history.history_id"), primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.source_id"), primary_key=True)


class Source(Base):
    __tablename__ = 'sources'

    source_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_volume_id: Mapped[int] = mapped_column(ForeignKey("volumes.volume_id"))
    source_directory: Mapped[str] = mapped_column(Text)

    source_volume: Mapped["Volume"] = relationship()

    __table_args__ = (
        UniqueConstraint('source_volume_id', 'source_directory'
                                             '', name='_source_uc'),
    )

    def __repr__(self):
        return self._repr(
            source_id=self.source_id,
            path=self.source_volume.volume_name + self.source_directory
        )

    # many-to-many relationship to Job, bypassing the `JobSourceAssociation` class
    jobs: Mapped[List["Job"]] = relationship(
        secondary="job_sources", back_populates="sources"
    )

    # many-to-many relationship to History, bypassing the `SourceHistoryAssociation` class
    history: Mapped[List["History"]] = relationship(
        secondary="history_sources", back_populates="sources"
    )


class JobSourceAssociation(Base):
    __tablename__ = "job_sources"
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.job_id"), primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.source_id"), primary_key=True)


class Job(Base):
    __tablename__ = 'jobs'

    job_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_tool: Mapped[str] = mapped_column(Text, nullable=False)
    job_description: Mapped[str] = mapped_column(Text)

    destination_id: Mapped[int] = mapped_column(ForeignKey("destinations.destination_id"))
    destination: Mapped["Destination"] = relationship()

    # many-to-many relationship to Sources, bypassing the `JobSourceAssociation` class
    sources: Mapped[List["Source"]] = relationship(
        secondary="job_sources", back_populates="jobs"
    )

    def __repr__(self):
        return self._repr(job_id=self.job_id, job_description=self.job_description)


class History(Base):
    __tablename__ = 'history'

    history_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.job_id"))
    job: Mapped["Job"] = relationship()

    job_tool: Mapped[str] = mapped_column(Text, nullable=False)
    job_description: Mapped[str] = mapped_column(Text)
    when: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    operation: Mapped[str] = mapped_column(Text)

    destination_id: Mapped[int] = mapped_column(ForeignKey("destinations.destination_id"))
    destination: Mapped["Destination"] = relationship()

    # many-to-many relationship to Sources, bypassing the `JobSourceAssociation` class
    sources: Mapped[List["Source"]] = relationship(
        secondary="history_sources", back_populates="history"
    )

    def __repr__(self):
        return self._repr(
            history_id=self.history_id,
            job_id=self.job_id,
            tool=self.job_tool,
            when=str(self.when),
            operation=self.operation)
