from io import BytesIO

from flask import Blueprint
from flask import session
from flask import request
from flask import url_for
from flask import send_file
from qrcode import make

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

    code = request.args.get("code", "")
    if len(code) != 4:
        return fail(message="code is invalid")

    if session.get(f"{vote_id}:code", "") != code:
        return fail(message="fail to verify request")

    path = url_for("join.vote", vote_id=vote_id, code=code)

    raw_img = BytesIO()

    img = make(
        data=f"{request.scheme}://{request.host}{path}",
        border=1,
    )

    img.save(raw_img, "PNG")

    raw_img.seek(0)

    return send_file(
        path_or_file=raw_img,
        mimetype="image/png"
    )
