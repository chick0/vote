from flask import Blueprint
from flask import request
from flask import session
from flask import redirect
from flask import url_for
from flask import render_template

from app import db
from app.models import Vote
from app.const import VOTE_ADMIN

bp = Blueprint("vote", __name__, url_prefix="/vote")


@bp.get("")
def create():
    title = request.args.get("title", "")

    return render_template(
        "vote/create.html",
        title=title
    )


@bp.post("")
def create_post():
    vote = Vote()
    vote.title = request.form.get("title", "제목 없는 투표")[:60]

    try:
        vote.max = int(request.form.get("max", "undefined"))
    except ValueError:
        return redirect(url_for("vote.create",
                                title=vote.title,
                                error="투표 참여 인원이 숫자가 아닙니다."))

    if vote.max > 50:
        return redirect(url_for("vote.create",
                                title=vote.title,
                                error="최대 50명까지 참여가 가능합니다."))

    vote.started = False

    db.session.add(vote)
    db.session.commit()

    session[vote.id] = VOTE_ADMIN

    return redirect(
        url_for("vote.panel", vote_id=vote.id)
    )


@bp.get("/panel/<int:vote_id>")
def panel(vote_id: int):
    if not session.get(vote_id) == VOTE_ADMIN:
        return "권한이 없습니다."

    vote = Vote.query.filter_by(
        id=vote_id,
    ).first()

    if vote is None:
        del session[vote_id]
        return "등록된 투표가 아닙니다!"

    return f"panel of {vote.title}"


@bp.get("/<int:vote_id>")
def do(vote_id: int):
    if session.get(vote_id) == VOTE_ADMIN:
        return "투표 생성자는 투표에 참여 할 수 없습니다."

    vote = Vote.query.filter_by(
        id=vote_id,
    ).first()

    if vote is None:
        del session[vote_id]
        return "등록된 투표가 아닙니다!"

    if not vote.started:
        return "지금은 투표에 참여할 수 없습니다."

    return "개발중"
