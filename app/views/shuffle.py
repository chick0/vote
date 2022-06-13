from flask import Blueprint
from flask import abort
from flask import redirect
from flask import url_for

from app import db
from app.models import Vote
from app.const import VOTE_ADMIN
from app.utils import get_vote_session
from app.utils import del_vote_session

bp = Blueprint("shuffle", __name__, url_prefix="/shuffle")


@bp.get("/toggle/<int:vote_id>")
def toggle(vote_id: int):
    vs = get_vote_session(vote_id=vote_id)
    if vs is None:
        # 투표 세션 없으면 권한 없음
        return abort(403)
    else:
        # 관리자가 아니라면 선택지로 이동
        if vs.session_id != VOTE_ADMIN:
            return redirect(url_for("vote.do", vote_id=vote_id))

    vote = Vote.query.filter_by(
        id=vote_id
    ).first()

    if vote is None:
        del_vote_session(vote_id=vote_id)
        return abort(404)

    if vote.shuffle is True:
        vote.shuffle = False
    else:
        vote.shuffle = True

    db.session.commit()
    return redirect(url_for("vote.panel", vote_id=vote_id))
