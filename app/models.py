from sqlalchemy import func
from app import db


class Vote(db.Model):
    id = db.Column(
        db.Integer,
        unique=True,
        primary_key=True,
        nullable=False
    )

    title = db.Column(
        db.String(60),
        nullable=False
    )

    max = db.Column(
        db.Integer,
        nullable=False
    )

    creation_date = db.Column(
        db.DateTime,
        nullable=False,
        default=func.now()
    )

    finished_date = db.Column(
        db.DateTime,
        nullable=True,
        default=None,
    )

    # true : 투표 진행중
    # false : 투표가 시작되지 않음
    # none : 투표가 종료됨(마감됨)
    started = db.Column(
        db.Boolean,
        nullable=True,
        default=False
    )

    code = db.Column(
        db.String(6),
        unique=True,
        nullable=True
    )

    def __repr__(self):
        return f"<Vote id={self.id} title={self.title!r}>"


class Session(db.Model):
    id = db.Column(
        db.Integer,
        unique=True,
        primary_key=True,
        nullable=False
    )

    vote_id = db.Column(
        db.Integer,
        nullable=False
    )

    select = db.Column(
        db.Integer,
        nullable=True,
    )

    selected = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    def __repr__(self):
        return f"<Session id={self.id} vote_id={self.vote_id} selected={self.selected!r}>"


class Option(db.Model):
    id = db.Column(
        db.Integer,
        unique=True,
        primary_key=True,
        nullable=False
    )

    vote_id = db.Column(
        db.Integer,
        nullable=False
    )

    name = db.Column(
        db.String(30),
        nullable=False
    )

    def __repr__(self):
        return f"<Option id={self.id}, vote_id={self.vote_id}>"
