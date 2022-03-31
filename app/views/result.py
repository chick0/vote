from random import randint
from datetime import datetime

from flask import Blueprint
from flask import session
from flask import abort
from flask import redirect
from flask import url_for
from flask import render_template

from app import db
from app.models import Vote
from app.models import Session
from app.models import Option
from app.const import VOTE_ADMIN
from app.utils import error

bp = Blueprint("result", __name__, url_prefix="/result")


@bp.get("/<int:vote_id>")
def end(vote_id: int):
    session_id = session.get(str(vote_id), None)
    if session_id is None:
        return abort(404)
    elif session_id == VOTE_ADMIN:
        return abort(404)

    s = Session.query.filter_by(
        id=session_id,
        vote_id=vote_id,
    ).first()
    if s is None:
        return abort(404)

    if s.selected is False:
        return redirect(url_for("vote.do", vote_id=vote_id))

    return render_template(
        "result/end.html",
    )


@bp.get("/panel/<int:vote_id>")
def panel(vote_id: int):
    if not session.get(str(vote_id)) == VOTE_ADMIN:
        return error(
            message="권한이 없습니다.",
            code=403
        )

    vote = Vote.query.filter_by(
        id=vote_id
    ).first()

    if vote.started is False:
        return redirect(url_for("vote.panel", vote_id=vote_id, error="투표가 시작되지 않았습니다."))

    if vote.started is True:
        session[f"{vote.id}:vote"] = dict(id=vote.id, title="[마감] " + vote.title)
        vote.started = None
        vote.finished_date = datetime.now()
        db.session.commit()

    opts = Option.query.filter_by(
        vote_id=vote.id
    ).all()

    option = {}
    score = {}
    drop = 0
    for opt in opts:
        option[opt.id] = opt.name
        score[opt.id] = 0

    large_score = 0
    for s in Session.query.filter_by(
        vote_id=vote.id,
    ).all():
        if s.selected:
            score[s.select] += 1
            if score[s.select] > large_score:
                large_score = score[s.select]
        else:
            drop += 1

    def gen_color():
        r = randint(1, 255)
        g = randint(1, 255)
        b = randint(1, 255)

        if r == g == b:
            r = randint(1, 255)
            g = randint(1, 255)
            b = randint(1, 255)

        return f"rgb({r}, {g}, {b})"

    return render_template(
        "result/panel.html",
        title=vote.title,
        option=option,
        score=score,
        large_score=large_score,
        drop=drop,
        votes=Session.query.filter_by(
            vote_id=vote.id
        ).count(),
        colors=[
            gen_color() for i in range(0, len(option))
        ]
    )
