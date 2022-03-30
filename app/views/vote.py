from os import urandom
from json import dumps

from flask import Blueprint
from flask import request
from flask import session
from flask import redirect
from flask import url_for
from flask import render_template

from app import db
from app.models import Vote
from app.models import Session
from app.models import Option
from app.const import VOTE_ADMIN
from app.utils import resp
from app.utils import error
from app.utils import safe_remove

bp = Blueprint("vote", __name__, url_prefix="/vote")


@bp.get("")
def create():
    def to_ui(message: str):
        return redirect(url_for("create.ui",
                                title=vote.title,
                                error=message))

    vote = Vote()
    vote.title = request.args.get("title", "")[:60]
    if len(vote.title) == 0:
        vote.title = "제목 없는 투표"

    try:
        vote.max = int(request.args.get("max", "undefined"))
    except ValueError:
        return to_ui(message="투표 참여 인원이 숫자가 아닙니다.")

    if vote.max > 50:
        return to_ui(message="최대 50명까지 참여가 가능합니다.")
    elif vote.max <= 2:
        return to_ui(message="투표 참여 인원은 3명이상으로 설정해야 합니다.")
    elif vote.max == 0:
        return to_ui(message="투표에 참가할 수 있는 인원이 없습니다.")

    vote.started = False
    vote.code = urandom(2).hex()

    db.session.add(vote)
    db.session.commit()

    session[str(vote.id)] = VOTE_ADMIN
    session[f"{vote.id}:vote"] = dict(id=vote.id, title=vote.title)

    return redirect(
        url_for("vote.panel", vote_id=vote.id)
    )


@bp.get("/panel/<int:vote_id>")
def panel(vote_id: int):
    s = session.get(str(vote_id))
    if not s == VOTE_ADMIN:
        if s is not None:
            return redirect(url_for("vote.do", vote_id=vote_id))

        return error(
            message="권한이 없습니다.",
            code=403
        )

    vote = Vote.query.filter_by(
        id=vote_id,
    ).first()

    if vote is None:
        safe_remove(vote_id)
        return error(
            message="등록된 투표가 아닙니다!",
            code=404
        )

    if vote.started is None:
        return redirect(url_for("result.panel", vote_id=vote_id))

    opts = {}
    for x in Option.query.filter_by(
        vote_id=vote.id
    ).all():
        opts[x.id] = x.name

    return render_template(
        "vote/panel.html",
        id=vote.id,
        title=vote.title,
        max=vote.max,
        code=vote.code,
        opts=dumps(opts, ensure_ascii=True)
    )


@bp.post("/panel/<int:vote_id>")
def panel_post(vote_id: int):
    if not session.get(str(vote_id)) == VOTE_ADMIN:
        return resp(
            message="권한이 없습니다.",
            code=403
        )

    vote = Vote.query.filter_by(
        id=vote_id,
    ).first()

    if vote is None:
        safe_remove(vote_id)
        return resp(
            message="등록된 투표가 아닙니다.",
            code=403
        )

    if vote.started:
        return resp(
            message="이미 시작된 투표입니다.",
            code=400
        )

    if vote.started is None:
        return resp(
            message="이미 마감된 투표입니다.",
            code=400
        )

    opts = Option.query.filter_by(
        vote_id=vote_id
    ).count()

    if opts < 2:
        return resp(
            message="투표를 시작하려면 적어도 2개의 선택지를 등록해야 합니다.",
            code=400
        )

    vote.started = True
    db.session.commit()

    session[f"{vote.id}:vote"] = dict(id=vote.id, title="[진행중] "+vote.title)

    return resp(
        message="이제 투표에 참여할 수 있으며 수정 할 수 없습니다.",
        code=200
    )


@bp.get("/<int:vote_id>")
def do(vote_id: int):
    if session.get(str(vote_id)) == VOTE_ADMIN:
        return error(
            message="투표 생성자는 투표에 참여 할 수 없습니다.",
            code=400
        )

    vote = Vote.query.filter_by(
        id=vote_id,
    ).first()

    if vote is None:
        safe_remove(vote_id)
        return error(
            message="등록된 투표가 아닙니다!",
            code=404
        )

    if not vote.started:
        return error(
            message="지금은 투표에 참여할 수 없습니다.",
            code=400
        )

    s = Session.query.filter_by(
        id=session.get(str(vote_id)),
        vote_id=vote_id,
    ).first()

    if s is None:
        return error(
            message="투표에 참여할 권한이 없습니다.",
            code=403
        )

    if s.selected:
        return error(
            message="이미 투표에 참여했습니다.",
            code=400
        )

    opts = Option.query.filter_by(
        vote_id=vote.id
    ).all()

    return render_template(
        "vote/do.html",
        title=vote.title,
        opts=[
            {
                "id": x.id,
                "name": x.name,
            } for x in opts
        ]
    )


@bp.post("/<int:vote_id>")
def do_post(vote_id: int):
    if session.get(str(vote_id)) == VOTE_ADMIN:
        return error(
            message="투표 생성자는 투표에 참여 할 수 없습니다.",
            code=400
        )

    vote = Vote.query.filter_by(
        id=vote_id,
    ).first()

    if vote is None:
        safe_remove(vote_id)
        return error(
            message="등록된 투표가 아닙니다!",
            code=404
        )

    if not vote.started:
        return error(
            message="지금은 투표에 참여할 수 없습니다.",
            code=400
        )

    s = Session.query.filter_by(
        id=session.get(str(vote_id)),
        vote_id=vote_id,
    ).first()

    if s is None:
        return error(
            message="투표에 참여할 권한이 없습니다",
            code=403
        )

    if s.selected:
        return error(
            message="이미 투표에 참여했습니다.",
            code=400
        )

    try:
        select = int(request.form.get("select"))
    except (TypeError, ValueError):
        return error(
            message="선택 정보가 올바르지 않습니다.",
            code=400
        )

    o = Option.query.filter_by(
        id=select,
        vote_id=vote_id
    ).first()

    if o is None:
        return error(
            message="올바르지 않은 선택지 입니다.",
            code=400
        )

    s.select = select
    s.selected = True

    db.session.commit()

    return redirect(url_for("result.end", vote_id=vote.id))
