from flask import Blueprint
from flask import session
from flask import redirect
from flask import url_for
from flask import render_template

from app.models import Vote

bp = Blueprint("my", __name__, url_prefix="/my")


@bp.get("/votes")
def votes():
    return render_template(
        "my/votes.html",
        votes=[
            {
                "id": x['id'],
                "title": x['title'],
                "url": url_for("my.vote", vote_id=x['id'])
            } for x in [
                session[v] for v in session if v.endswith(":vote")
            ]
        ]
    )


@bp.get("/vote/<int:vote_id>")
def vote(vote_id: int):
    def exp():
        try:
            del session[f"{vote_id}:vote"]
        except KeyError:
            pass

    target = Vote.query.filter_by(
        id=vote_id
    ).first()

    if target is None:
        exp()
        return redirect(url_for("my.votes", error="해당 투표는 서버에서 삭제되었습니다."))

    if target.started is None:
        return redirect(url_for("result.panel", vote_id=vote_id))

    return redirect(url_for("vote.panel", vote_id=vote_id))
