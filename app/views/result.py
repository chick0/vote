from flask import Blueprint
from flask import render_template

bp = Blueprint("result", __name__, url_prefix="/result")


@bp.get("/vote/<int:vote_id>/end")
def end(vote_id: int):
    return render_template(
        "result/end.html",
    )

