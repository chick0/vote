from datetime import datetime
from datetime import timedelta

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import SmallInteger
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Vote(Base):
    __tablename__ = "vote"

    id = Column(
        Integer,
        unique=True,
        primary_key=True,
        nullable=False
    )

    title = Column(
        String(30),
        nullable=False
    )

    max = Column(
        Integer,
        nullable=False
    )

    # 투표 생성 시간
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now()
    )

    # 투표가 마감된 시간
    finished_at = Column(
        DateTime,
        nullable=True,
        default=None,
    )

    # 투표 삭제 시간
    deleted_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now() + timedelta(hours=6)
    )

    # models.status : Status
    status = Column(
        SmallInteger,
        nullable=False,
        default=False
    )

    code = Column(
        String(6),
        unique=True,
        nullable=True
    )

    def __repr__(self):
        return f"<Vote id={self.id} title={self.title!r}>"


class VoteOption(Base):
    __tablename__ = "vote_option"

    id = Column(
        Integer,
        unique=True,
        primary_key=True,
        nullable=False
    )

    vote_id = Column(
        Integer,
        ForeignKey("vote.id")
    )

    name = Column(
        String(30),
        nullable=False
    )

    def __repr__(self):
        return f"<VoteOption id={self.id}, vote_id={self.vote_id}>"


class VoteSession(Base):
    __tablename__ = "vote_session"

    id = Column(
        Integer,
        unique=True,
        primary_key=True,
        nullable=False
    )

    vote_id = Column(
        Integer,
        ForeignKey("vote.id")
    )

    select = Column(
        Integer,
        ForeignKey("vote_option.id")
    )

    selected = Column(
        Boolean,
        nullable=False,
        default=False
    )

    def __repr__(self):
        return f"<VoteSession id={self.id} vote_id={self.vote_id} selected={self.selected!r}>"
