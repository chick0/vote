from flask import Blueprint
from flask import request
from flask import render_template

from app.utils import get_message

bp = Blueprint("index", __name__, url_prefix="/")


@bp.get("")
def index():
    return render_template(
        "index/index.html",
        error=get_message()
    )


@bp.get("/create")
def create():
    return render_template(
        "index/create.html",
        title=request.args.get("title", ""),
        error=get_message()
    )

