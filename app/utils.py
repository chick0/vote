from functools import wraps

from flask import request
from flask import session
from flask import jsonify
from flask import render_template

from app.models import Vote
from app.models import Session
from app.models import Option
from app.const import VOTE_ADMIN


def resp(message: str = "", data: dict or list = None, code: int = 200):
    return jsonify({
        "message": message,
        "data": data,
    }), code


def vote_filter(vote: Vote):
    if not session.get(str(vote.id), "") == VOTE_ADMIN:
        return resp(
            message="권한이 없습니다.",
            code=403
        )

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

    return None


def fetch_vote(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        vote_id = request.args.get("vote_id")
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


def error(message: str, code: int):
    return render_template(
        "error.html",
        title="오류",
        message=message,
    ), code


def safe_remove(vote_id: int):
    def do_it(key: str):
        try:
            del session[key]
        except KeyError:
            pass

    for k in [
        str(vote_id),
        str(vote_id) + ":vote",
        str(vote_id) + ":code",
    ]:
        do_it(key=k)


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
