from flask import Blueprint
from flask import session
from flask import redirect
from flask import url_for

from app import db
from app.models import Vote
from app.models import Session
from app.utils import error

bp = Blueprint("join", __name__, url_prefix="/join")


@bp.get("/<int:vote_id>")
def vote(vote_id: int):
    if session.get(str(vote_id)) is not None:
        return error(
            message="이미 투표하셨습니다.",
            code=400
        )

    v = Vote.query.filter_by(
        id=vote_id,
    ).first()

    if v is None:
        return error(
            message="등록된 투표가 아닙니다.",
            code=404
        )

    if v.started is None:
        return error(
            message="마감된 투표입니다.",
            code=400
        )

    c = Session.query.filter_by(
        vote_id=vote_id
    ).count()

    if c >= v.max:
        return error(
            message="마감된 투표입니다.",
            code=400
        )

    s = Session()
    s.vote_id = v.id
    s.selected = False

    db.session.add(s)
    db.session.commit()

    session[str(vote_id)] = s.id

    return redirect(url_for("vote.do", vote_id=vote_id))
