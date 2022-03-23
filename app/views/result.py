from flask import Blueprint
from flask import session
from flask import abort
from flask import render_template

bp = Blueprint("result", __name__, url_prefix="/result")


@bp.get("/vote/<int:vote_id>/end")
def end(vote_id: int):
    try:
        del session[str(vote_id)]
    except KeyError:
        return abort(404)

    return render_template(
        "result/end.html",
    )

