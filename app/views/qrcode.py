from io import BytesIO

from flask import Blueprint
from flask import request
from flask import url_for
from flask import send_file
from qrcode import make

bp = Blueprint("qrcode", __name__, url_prefix="/qrcode")


def return_none():
    return send_file(
        path_or_file=BytesIO(b""),
        mimetype="text/plain"
    ), 400


@bp.get("join.png")
def join():
    vote_id = request.args.get("vote_id", None)
    if vote_id is None:
        return return_none()

    code = request.args.get("code", "")
    if len(code) != 4:
        return return_none()

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
