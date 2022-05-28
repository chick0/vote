from datetime import datetime

from flask import Blueprint
from flask import abort
from flask import redirect
from flask import url_for
from flask import render_template

from app import db
from app.models import Vote
from app.models import Session
from app.const import VOTE_ADMIN
from app.utils import error
from app.utils import fetch_result
from app.utils import get_colors
from app.utils import get_vote_session
from app.utils import del_vote_session

bp = Blueprint("result", __name__, url_prefix="/result")


@bp.get("/<int:vote_id>")
def end(vote_id: int):
    vs = get_vote_session(vote_id=vote_id)
    if vs is None or vs.session_id == VOTE_ADMIN:
        return abort(404)

    s = Session.query.filter_by(
        id=vs.session_id,
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
    vs = get_vote_session(vote_id=vote_id)
    if vs is None or vs.session_id != VOTE_ADMIN:
        return error(
            message="권한이 없습니다.",
            code=403
        )

    vote = Vote.query.filter_by(
        id=vote_id
    ).first()

    if vote is None:
        del_vote_session(vote_id=vote_id)
        return redirect(url_for("my.votes", error="해당 투표는 서버에서 삭제되었습니다."))

    if vote.started is False:
        return redirect(url_for("vote.panel", vote_id=vote_id, error="투표가 시작되지 않았습니다."))

    if vote.started is True:
        vote.started = None
        vote.finished_date = datetime.now()
        db.session.commit()

    result = fetch_result(
        vote_id=vote_id
    )

    return render_template(
        "result/panel.html",
        id=vote.id,
        title=vote.title,

        # content p data
        votes=sum([x[1] for x in result[::-1][1:]]),
        drop=result[-1][1],

        # table data
        result=result,
        large_score=max([x[1] for x in result]),

        # chart data
        labels=[x[0] for x in result],
        data=[x[1] for x in result],
        colors=get_colors(length=len(result))
    )
