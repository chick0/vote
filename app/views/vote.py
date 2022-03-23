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

    session[str(vote.id)] = VOTE_ADMIN

    return redirect(
        url_for("vote.panel", vote_id=vote.id)
    )


@bp.get("/panel/<int:vote_id>")
def panel(vote_id: int):
    if not session.get(str(vote_id)) == VOTE_ADMIN:
        return "권한이 없습니다."

    vote = Vote.query.filter_by(
        id=vote_id,
    ).first()

    if vote is None:
        del session[str(vote_id)]
        return "등록된 투표가 아닙니다!"

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
        opts=dumps(opts, ensure_ascii=True)
    )


@bp.post("/panel/<int:vote_id>")
def panel_post(vote_id: int):
    if not session.get(str(vote_id)) == VOTE_ADMIN:
        return resp(
            message="권한이 없습니다.",
            code=403
        )

    v = Vote.query.filter_by(
        id=vote_id,
    ).first()

    if v is None:
        del session[str(vote_id)]
        return resp(
            message="등록된 투표가 아닙니다.",
            code=403
        )

    if v.started:
        return resp(
            message="이미 시작된 투표입니다.",
            code=400
        )

    v.started = True
    db.session.commit()

    return resp(
        message="이제 투표에 참여할 수 있으며 수정 할 수 없습니다.",
        code=200
    )


@bp.get("/<int:vote_id>")
def do(vote_id: int):
    if session.get(str(vote_id)) == VOTE_ADMIN:
        return "투표 생성자는 투표에 참여 할 수 없습니다."

    vote = Vote.query.filter_by(
        id=vote_id,
    ).first()

    if vote is None:
        del session[str(vote_id)]
        return "등록된 투표가 아닙니다!"

    if not vote.started:
        return "지금은 투표에 참여할 수 없습니다."

    s = Session.query.filter_by(
        id=session.get(str(vote_id)),
        vote_id=vote_id,
    ).first()

    if s is None:
        return "투표에 참여할 권한이 없습니다."

    if s.selected:
        return "이미 투표에 참여했습니다."

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
        return "투표 생성자는 투표에 참여 할 수 없습니다."

    vote = Vote.query.filter_by(
        id=vote_id,
    ).first()

    if vote is None:
        del session[str(vote_id)]
        return "등록된 투표가 아닙니다!"

    if not vote.started:
        return "지금은 투표에 참여할 수 없습니다."

    s = Session.query.filter_by(
        id=session.get(str(vote_id)),
        vote_id=vote_id,
    ).first()

    if s is None:
        return "투표에 참여할 권한이 없습니다."

    if s.selected:
        return "이미 투표에 참여했습니다."

    try:
        select = int(request.form.get("select"))
    except TypeError:
        return "올바르지 않은 선택 입니다."
    except ValueError:
        return "잘못된 변수 전달 / 선택지 변수는 숫자 입니다."

    o = Option.query.filter_by(
        id=select,
        vote_id=vote_id
    ).first()

    if o is None:
        return "올바르지 않은 선택지 입니다."

    s.select = select
    s.selected = True

    db.session.commit()

    return redirect(url_for("result.end", vote_id=vote_id))
