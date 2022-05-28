from flask import Blueprint
from flask import session
from flask import redirect
from flask import url_for
from flask import render_template

from app.models import Vote
from app.utils import get_vote_session
from app.utils import del_vote_session

bp = Blueprint("my", __name__, url_prefix="/my")


@bp.get("/votes")
def votes():
    return render_template(
        "my/votes.html",
        votes=[
            get_vote_session(vote_id=vote_id) for vote_id in session.keys()
        ]
    )


@bp.get("/vote/<int:vote_id>")
def vote(vote_id: int):
    target = Vote.query.filter_by(
        id=vote_id
    ).first()

    if target is None:
        del_vote_session(vote_id=vote_id)
        return redirect(url_for("my.votes", error="해당 투표는 서버에서 삭제되었습니다."))

    if target.started is None:
        return redirect(url_for("result.panel", vote_id=vote_id))

    return redirect(url_for("vote.panel", vote_id=vote_id))
