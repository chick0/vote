from functools import wraps
from collections import namedtuple

from flask import request
from flask import session
from flask import jsonify
from flask import render_template

from app.models import Vote
from app.models import Session
from app.models import Option
from app.const import VOTE_ADMIN

VoteSession = namedtuple(
    "VoteSession",
    [
        'vote_id',
        'session_id',
        'title',
    ]
)


def resp(message: str = "", data: dict or list = None, code: int = 200):
    return jsonify({
        "message": message,
        "data": data,
    }), code


def fetch_vote(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        vote_id = request.args.get("vote_id", None)
        if vote_id is None:
            return resp(
                message="투표 아이디를 전달받지 못했습니다.",
                code=400
            )

        v: Vote = Vote.query.filter_by(
            id=vote_id
        ).first()

        if v is None:
            return resp(
                message="등록된 투표가 아닙니다.",
                code=404
            )

        kwargs.update({"vote": v})
        return f(*args, **kwargs)

    return decorator


def check_admin(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        vote_id = request.args.get("vote_id", None)
        if vote_id is None:
            return resp(
                message="투표 아이디를 전달받지 못했습니다.",
                code=400
            )

        try:
            vs = get_vote_session(vote_id=int(vote_id))
        except ValueError:
            vs = None

        if vs is not None and vs.session_id != VOTE_ADMIN:
            return resp(
                message="권한이 없습니다.",
                code=403
            )

        return f(*args, **kwargs)

    return decorator


def vote_filter(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        vote = kwargs.get("vote")
        if vote is None:
            raise RuntimeError("검증할 투표가 없습니다.")

        if vote.started:
            return resp(
                message="이미 시작된 투표입니다.",
                code=400
            )

        if vote.started is None:
            return resp(
                message="마감된 투표입니다.",
                code=400
            )

        return f(*args, **kwargs)

    return decorator


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
    # colors from chart.js
    #  * https://github.com/chartjs/Chart.js/blob/master/docs/scripts/utils.js#L127
    colors: list = [
        'rgb(255, 99, 132)',
        'rgb(255, 159, 64)',
        'rgb(255, 205, 86)',
        'rgb(75, 192, 192)',
        'rgb(54, 162, 235)',
        'rgb(153, 102, 255)'
    ]

    index = 0
    while (length - 1) > len(colors):
        colors.append(colors[index])
        index += 1

    return colors[0:length - 1] + ["rgb(201, 203, 207)"]


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
