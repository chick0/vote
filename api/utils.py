from functools import wraps

from flask import request
from flask import jsonify

from app.models import Vote
from app.const import VOTE_ADMIN
from app.utils import get_vote_session


def resp(message: str = "", data: dict or list = None, code: int = 200):
    return jsonify({
        "message": message,
        "data": data,
        "code": code,
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
