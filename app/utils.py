from os import urandom
from random import randint
from collections import namedtuple

from flask import request
from flask import session
from flask import render_template

from app.models import Vote
from app.models import Session
from app.models import Option

VoteSession = namedtuple(
    "VoteSession",
    [
        'vote_id',
        'session_id',
        'title',
    ]
)


def set_message(message: str) -> str:
    for old_id in session:
        if session[old_id] == message:
            return old_id

    message_id = urandom(4).hex()
    session[message_id] = message
    return message_id


def get_message(key: str = "error") -> str or None:
    message_id = request.args.get(key)
    if message_id is None:
        return None

    message = session.get(message_id)

    if message is None:
        return None

    del session[message_id]
    return message


def error(message: str, code: int):
    return render_template(
        "error.html",
        title="오류",
        message=message,
    ), code


def fetch_result(vote_id: int) -> list:
    def calc_percent(t):
        try:
            per = int(t / v.max * 100)
            return f"{per} %"
        except ZeroDivisionError:
            return "-"

    opts = Option.query.filter_by(
        vote_id=vote_id
    ).all()

    score = {}
    for s in Session.query.filter_by(
        vote_id=vote_id,
    ).all():
        if s.selected:
            try:
                score[s.select] += 1
            except KeyError:
                score[s.select] = 1

    v = Vote.query.with_entities(Vote.max).filter_by(
        id=vote_id
    ).first()

    drop = v.max - sum(score.values()) + score.get(-1, 0)
    result = [
        [
            opt.name,
            score.get(opt.id, 0),
            calc_percent(t=score.get(opt.id, 0))
        ] for opt in opts
    ]
    result.append(['기권', drop, calc_percent(t=drop)])
    return result


def get_colors(length: int) -> list:
    colors = []
    for i in range(0, length - 1):
        colors.append(
            "rgb({R},{G},{B})".format(
                R=randint(50, 250),
                G=randint(50, 250),
                B=randint(50, 250),
            )
        )

    # 기권 색깔
    colors.append("#666666")
    return colors


def set_vote_session(vote_id: int, title: str, session_id: int or str):
    session[f'{vote_id}'] = VoteSession(
        vote_id=vote_id,
        session_id=session_id,
        title=title,
    )._asdict()


def get_vote_session(vote_id: int) -> VoteSession or None:
    try:
        return VoteSession(**session[f'{vote_id}'])
    except KeyError:
        return None


def del_vote_session(vote_id: int) -> None:
    try:
        del session[f'{vote_id}']
    except KeyError:
        pass
