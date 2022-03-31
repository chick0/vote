from flask import Blueprint
from flask import request
from flask import render_template

bp = Blueprint("index", __name__, url_prefix="/")


@bp.get("")
def index():
    return render_template(
        "index/index.html"
    )


@bp.get("/create")
def create():
    title = request.args.get("title", "")

    return render_template(
        "index/create.html",
        title=title
    )

