from flask import Blueprint
from flask import request
from flask import render_template

bp = Blueprint("create", __name__, url_prefix="/create")


@bp.get("")
def ui():
    title = request.args.get("title", "")

    return render_template(
        "create/ui.html",
        title=title
    )
