from os import urandom
from json import dumps
from random import shuffle

from flask import Blueprint
from flask import abort
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Vote
from app.models import Session
from app.models import Option
from app.const import VOTE_ADMIN
from api.utils import resp
from app.utils import set_message
from app.utils import get_message
from app.utils import set_vote_session
from app.utils import get_vote_session
from app.utils import del_vote_session

bp = Blueprint("vote", __name__, url_prefix="/vote")


@bp.get("")
def to_form():
    return redirect(url_for("index.create"))


@bp.post("")
def create():
    def to(message: str):
        message_id = set_message(message=message)
        return redirect(url_for("index.create", title=vote.title, error=message_id))

    vote = Vote()
    vote.title = request.form.get("title", "")[:60]
    if len(vote.title) == 0:
        vote.title = "제목 없는 투표"

    try:
        vote.max = int(request.form.get("max", "undefined"))
    except ValueError:
        return to(message="투표 참여 인원이 숫자가 아닙니다.")

    if vote.max > 50:
        return to(message="최대 50명까지 참여가 가능합니다.")
    elif vote.max <= 2:
        return to(message="투표 참여 인원은 3명이상으로 설정해야 합니다.")
    elif vote.max == 0:
        return to(message="투표에 참가할 수 있는 인원이 없습니다.")

    vote.started = False
    vote.code = urandom(3).hex()

    try:
        db.session.add(vote)
        db.session.commit()
    except IntegrityError:
        return to(message="내부 오류가 발생했습니다. 다시 시도해주세요.")

    set_vote_session(
        vote_id=vote.id,
        session_id=VOTE_ADMIN,
        title=vote.title
    )

    return redirect(
        url_for("vote.panel", vote_id=vote.id)
    )


@bp.get("/panel/<int:vote_id>")
def panel(vote_id: int):
    vs = get_vote_session(vote_id=vote_id)
    if vs is None:
        # 투표 세션 없으면 권한 없음
        return abort(403)
    else:
        # 관리자가 아니라면 선택지로 이동
        if vs.session_id != VOTE_ADMIN:
            return redirect(url_for("vote.do", vote_id=vote_id))

    vote = Vote.query.filter_by(
        id=vote_id,
    ).first()

    if vote is None:
        del_vote_session(vote_id=vote_id)
        return abort(404)

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
        error=get_message(),
        max=vote.max,
        opts=dumps(opts, ensure_ascii=True),
        started=vote.started,
        join_url="{scheme}://{host}{path}".format(
            scheme=request.scheme,
            host=request.host,
            path=url_for(
                "join.click",
                code=vote.code
            )
        )
    )


@bp.post("/panel/<int:vote_id>")
def panel_post(vote_id: int):
    vs = get_vote_session(vote_id=vote_id)
    if vs is None or vs.session_id != VOTE_ADMIN:
        return resp(
            message="권한이 없습니다.",
            code=403
        )

    vote = Vote.query.filter_by(
        id=vote_id,
    ).first()

    if vote is None:
        del_vote_session(vote_id=vote_id)
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
            message="투표를 시작하려면 2개의 선택지를 등록해야 합니다.",
            code=400
        )

    vote.started = True
    db.session.commit()

    return resp(
        message="이제 투표에 참여할 수 있으며 수정 할 수 없습니다.",
        code=200
    )


@bp.get("/<int:vote_id>")
def do(vote_id: int):
    vs = get_vote_session(vote_id=vote_id)
    if vs is None:
        return abort(403)
    else:
        if vs.session_id == VOTE_ADMIN:
            return redirect(url_for("vote.panel", vote_id=vote_id))

    vote = Vote.query.filter_by(
        id=vote_id,
    ).first()

    if vote is None:
        del_vote_session(vote_id=vote_id)
        return abort(404)

    if vote.started is None:
        # 투표가 마감된 경우 결과 페이지로 이동
        return redirect(url_for("result.end", vote_id=vote.id))

    if vote.started is False:
        # 투표가 시작되지 않음
        return render_template(
            "vote/wait.html",
            id=vote_id,
        )

    s = Session.query.filter_by(
        id=vs.session_id,
        vote_id=vote_id,
    ).first()

    if s is None:
        del_vote_session(vote_id=vote_id)
        return abort(403)

    if s.selected:
        # 이미 투표에 참여한 경우 결과 페이지로 이동
        return redirect(url_for("result.end", vote_id=vote.id))

    opts = Option.query.filter_by(
        vote_id=vote.id
    ).all()
    shuffle(opts)

    return render_template(
        "vote/do.html",
        title=vote.title,
        opts=[
            {
                "id": x.id,
                "name": x.name,
            } for x in opts
        ],
        error=get_message()
    )


@bp.post("/<int:vote_id>")
def do_post(vote_id: int):
    def to(message: str):
        message_id = set_message(message=message)
        return redirect(url_for("vote.do", vote_id=vote_id, error=message_id))

    vs = get_vote_session(vote_id=vote_id)
    if vs is None:
        return abort(403)
    else:
        if vs.session_id == VOTE_ADMIN:
            return redirect(url_for("vote.panel", vote_id=vote_id))

    vote = Vote.query.filter_by(
        id=vote_id,
    ).first()

    if vote is None:
        del_vote_session(vote_id=vote_id)
        return abort(404)

    if vote.started is None:
        # 투표가 마감된 경우 결과 페이지로 이동
        return redirect(url_for("result.end", vote_id=vote.id))

    if vote.started is False:
        # 투표가 시작되지 않음
        return redirect(url_for("vote.do", vote_id=vote_id))

    s = Session.query.filter_by(
        id=vs.session_id,
        vote_id=vote_id,
    ).first()

    if s is None:
        del_vote_session(vote_id=vote_id)
        return abort(403)

    if s.selected:
        # 이미 투표에 참여한 경우 결과 페이지로 이동
        return redirect(url_for("result.end", vote_id=vote.id))

    try:
        select = int(request.form.get("select"))
    except (TypeError, ValueError):
        return to(message="선택 정보가 올바르지 않습니다.")

    if select != -1:
        o = Option.query.filter_by(
            id=select,
            vote_id=vote_id
        ).first()

        if o is None:
            return to(message="올바르지 않은 선택지 입니다.")

    s.select = select
    s.selected = True

    db.session.commit()

    return redirect(url_for("result.end", vote_id=vote.id))
