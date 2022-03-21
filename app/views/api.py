from flask import Blueprint
from flask import session
from flask import request
from flask import jsonify

bp = Blueprint("api", __name__, url_prefix="/api")


def resp(message: str = "", data: dict = None, code: int = 200):
    return jsonify({
        "message": message,
        "data": data,
    }), code


@bp.post("/opt")
def new_option():
    vote_id = request.args.get("vote_id", None)
    if vote_id is None:
        return resp(
            message="vote_id is missing",
            code=400
        )

    return resp(
        data={
            "option_id": "q"
        },
        code=201,
    )


@bp.delete("/opt/<string:option_id>")
def delete_option(option_id: str):
    return "q"
