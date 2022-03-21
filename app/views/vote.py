from flask import Blueprint
from flask import request
from flask import session
from flask import redirect
from flask import url_for
from flask import render_template

from app.const import VOTE_ADMIN
from app.const import VOTE_USER

bp = Blueprint("vote", __name__, url_prefix="/vote")


@bp.get("")
def create():
    return render_template(
        "vote/create.html"
    )


@bp.post("")
def create_post():
    from os import urandom
    vote_id = urandom(8).hex()

    session[vote_id] = VOTE_ADMIN

    {
        "title": request.form.get("title"),
        "max": request.form.get("max"),
        "votes": [],
        "vote_session": [],
        "vote_options": [],
    }.update({})

    return redirect(
        url_for("vote.panel", vote_id=vote_id)
    )


@bp.get("/panel/<string:vote_id>")
def panel(vote_id: str):
    if not session.get(vote_id, -1) == VOTE_ADMIN:
        return "403"

    return f"panel of {vote_id}"
