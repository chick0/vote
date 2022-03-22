from functools import wraps

from flask import request
from flask import session
from flask import jsonify

from app.models import Vote
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
