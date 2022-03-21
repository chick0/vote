from flask import Blueprint

bp = Blueprint("join", __name__, url_prefix="/join")


@bp.get("/<string:vote_id>")
def vote(vote_id: str):
    # create session
    # move to vote page

    return f"vote_id={vote_id}"
