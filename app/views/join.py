from flask import Blueprint
from flask import redirect
from flask import url_for

from app import db
from app.models import Vote
from app.models import Session
from app.const import VOTE_ADMIN
from app.utils import error
from app.utils import set_vote_session
from app.utils import get_vote_session

bp = Blueprint("join", __name__, url_prefix="/j")


@bp.get("/<string:code>")
def vote(code: str):
    v = Vote.query.filter_by(
        code=code
    ).first()

    if v is None:
        return error(
            message="등록된 투표가 아닙니다.",
            code=404
        )

    vs = get_vote_session(vote_id=v.id)
    if vs is not None:
        if vs.session_id == VOTE_ADMIN:
            return error(
                message="투표 관리자는 투표에 참여할 수 없습니다.",
                code=400
            )

        return redirect(url_for("vote.do", vote_id=v.id))

    if v.started is None:
        return error(
            message="마감된 투표입니다.",
            code=400
        )

    c = Session.query.filter_by(
        vote_id=v.id
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

    set_vote_session(
        vote_id=v.id,
        session_id=s.id,
        title=v.title
    )

    return redirect(url_for("vote.do", vote_id=v.id))
