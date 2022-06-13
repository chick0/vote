from flask import Blueprint
from flask import request

from app import db
from app.models import Vote
from app.models import Session
from app.models import Option
from api.utils import resp
from api.utils import check_admin
from api.utils import fetch_vote
from api.utils import vote_filter

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.get("/vote")
@fetch_vote
def get_vote_status(vote: Vote):
    return resp(
        data={
            "status": vote.started,
        },
        code=200
    )


@bp.get("/count")
@check_admin
@fetch_vote
def get_session_count(vote: Vote):
    return resp(
        data={
            "max": vote.max,
            "total": Session.query.filter_by(
                vote_id=vote.id
            ).count(),
            "selected": Session.query.filter_by(
                vote_id=vote.id,
                selected=True
            ).count()
        }
    )


@bp.post("/opt")
@check_admin
@fetch_vote
@vote_filter
def new_option(vote: Vote):
    c = Option.query.filter_by(
        vote_id=vote.id
    ).count()

    if c >= 10:
        return resp(
            message="10개 보다 더 많은 선택지를 등록 할 수 없습니다.",
            code=400
        )

    name = request.json.get("name", "").strip()[:30]
    if len(name) == 0:
        return resp(
            message="비어있는 선택지는 등록할 수 없습니다.",
            code=400
        )

    if name == "기권":
        return resp(
            message="기권 선택지는 등록 할 수 없습니다.",
            code=400
        )

    if Option.query.filter_by(
        vote_id=vote.id,
        name=name
    ).first() is not None:
        return resp(
            message="중복된 선택지는 등록 할 수 없습니다.",
            code=400
        )

    o = Option()
    o.vote_id = vote.id
    o.name = name

    db.session.add(o)
    db.session.commit()

    return resp(
        message="새로운 선택지를 등록했습니다.",
        data={
            "option_id": o.id,
        },
        code=201,
    )


@bp.delete("/opt")
@check_admin
@fetch_vote
@vote_filter
def delete_option(vote: Vote):
    try:
        option_id = int(request.args.get("option_id", None))
    except (ValueError, TypeError):
        return resp(
            message="옵션 ID가 잘못되었습니다.",
            code=400
        )

    Option.query.filter_by(
        id=option_id,
        vote_id=vote.id
    ).delete()

    db.session.commit()

    return resp(
        # message="해당 선택지를 삭제했습니다.",
        code=200
    )
