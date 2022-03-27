from flask import Blueprint
from flask import session
from flask import request

from app import db
from app.models import Vote
from app.models import Session
from app.models import Option
from app.utils import resp
from app.utils import fetch_vote
from app.utils import vote_filter

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.get("/count")
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
@fetch_vote
def new_option(vote: Vote):
    vf = vote_filter(vote=vote)
    if vf is not None:
        return vf

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
            message="이름없는 선택지는 등록할 수 없습니다.",
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


@bp.post("/opt/<int:option_id>")
@fetch_vote
def edit_option(option_id: int, vote: Vote):
    vf = vote_filter(vote=vote)
    if vf is not None:
        return vf

    name = request.json.get("name", "").strip()[:30]
    if len(name) == 0:
        Option.query.filter_by(
            id=option_id,
            vote_id=vote.id
        ).delete()
        db.session.commit()

        return resp(
            message="해당 선택지를 삭제했습니다.",
            code=400
        )

    o = Option.query.filter_by(
        id=option_id,
        vote_id=vote.id
    ).first()

    o.name = name
    db.session.commit()

    return resp(
        message="해당 선택지를 수정했습니다.",
        code=200
    )


@bp.delete("/opt/<int:option_id>")
@fetch_vote
def delete_option(option_id: int, vote: Vote):
    vf = vote_filter(vote=vote)
    if vf is not None:
        return vf

    Option.query.filter_by(
        id=option_id,
        vote_id=vote.id
    ).delete()
    db.session.commit()

    return resp(
        message="해당 선택지를 삭제했습니다.",
        code=200
    )


@bp.delete("/opt/<int:option_id>")
@fetch_vote
def fetch_option(option_id: int, vote: Vote):
    if session.get(str(vote.id)) is None:
        return resp(
            message="권한이 없습니다.",
            code=403
        )

    o = Option.query.filter_by(
        id=option_id,
        vote_id=vote.id
    ).first()

    if o is None:
        return resp(
            message="등록된 선택지가 아닙니다.",
            code=400
        )

    return resp(
        data={
            "id": o.id,
            "name": o.name,
        },
        code=200
    )
