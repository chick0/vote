from io import BytesIO

from flask import Blueprint
from flask import request
from flask import url_for
from flask import send_file
from qrcode import make

from app.models import Vote
from app.const import VOTE_ADMIN
from app.utils import get_vote_session

bp = Blueprint("qrcode", __name__, url_prefix="/qrcode")


def fail(message: str = "undefined error"):
    return send_file(
        path_or_file=BytesIO(message.encode("utf-8")),
        mimetype="text/plain"
    ), 400


@bp.get("join.png")
def join():
    try:
        vote_id = int(request.args.get("vote_id"))
    except (ValueError, TypeError):
        return fail(message="vote_id is invalid")

    vs = get_vote_session(vote_id=vote_id)
    if vs is None:
        return fail(message="vote session is missing")

    if vs.session_id != VOTE_ADMIN:
        return fail(message="only admin can check qrcode image")

    vote = Vote.query.filter_by(
        id=vs.vote_id,
    ).filter(
        Vote.started != None,
    ).with_entities(
        Vote.code
    ).first()

    if vote is None:
        return fail(message="deleted vote")

    raw_img = BytesIO()

    img = make(
        data="{scheme}://{host}{path}".format(
            scheme=request.scheme,
            host=request.host,
            path=url_for(
                "join.vote",
                code=vote.code
            )
        ),
        border=1,
    )

    img.save(raw_img, "PNG")

    raw_img.seek(0)

    return send_file(
        path_or_file=raw_img,
        mimetype="image/png"
    )
