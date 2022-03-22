from flask import Blueprint
from flask import session
from flask import redirect
from flask import url_for

from app import db
from app.models import Vote
from app.models import Session

bp = Blueprint("join", __name__, url_prefix="/join")


@bp.get("/<int:vote_id>")
def vote(vote_id: int):
    v = Vote.query.filter_by(
        id=vote_id,
    ).first()

    if v is None:
        return "등록된 투표가 아닙니다."

    c = Session.query.filter_by(
        vote_id=vote_id
    ).count()

    if c > v.max:
        return "투표 참여가 마감되었습니다."

    s = Session()
    s.vote_id = v.id
    s.selected = False

    db.session.add(s)
    db.session.commit()

    session[vote_id] = s.id

    return redirect(url_for("vote.do", vote_id=vote_id))
