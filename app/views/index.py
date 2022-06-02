from flask import Blueprint
from flask import request
from flask import render_template

bp = Blueprint("index", __name__, url_prefix="/")


@bp.get("")
def index():
    return render_template(
        "index/index.html",
        error={
            '403': "해당 투표를 확인할 권한이 없습니다.",
            '404': "해당 페이지를 찾을 수 없습니다.",
            '405': "해당 요청이 올바르지 않습니다.",
        }.get(request.args.get("e"), None)
    )


@bp.get("/create")
def create():
    title = request.args.get("title", "")

    return render_template(
        "index/create.html",
        title=title
    )

