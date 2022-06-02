from flask import Blueprint
from flask import abort
from flask import redirect
from flask import url_for

from app import db
from app.utils import get_vote_session
from app.models import Vote
from app.models import Session
from app.const import VOTE_ADMIN

bp = Blueprint("restart", __name__, url_prefix="/restart")


@bp.get("/<int:vote_id>")
def panel(vote_id: int):
    vs = get_vote_session(vote_id=vote_id)
    if vs is None or vs.session_id != VOTE_ADMIN:
        return abort(403)

    vote = Vote.query.filter_by(
        id=vote_id
    ).first()

    if vote.started is not None:
        return redirect(url_for("vote.panel", vote_id=vote_id))

    for session in Session.query.filter_by(
        vote_id=vote_id
    ).all():
        session.selected = False
        session.select = None

    vote.started = False

    db.session.commit()

    return redirect(url_for("vote.panel", vote_id=vote_id))
