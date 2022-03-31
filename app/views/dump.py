from io import BytesIO
from codecs import BOM_UTF8

from flask import Blueprint
from flask import session
from flask import send_file

from app.models import Vote
from app.const import VOTE_ADMIN
from app.utils import error
from app.utils import fetch_result

bp = Blueprint("dump", __name__, url_prefix="/dump")


@bp.get("/<int:vote_id>/<string:title>.csv")
def to_csv(vote_id: int, title: str):
    if not session.get(str(vote_id)) == VOTE_ADMIN:
        return error(
            message="투표 결과를 확인할 권한이 없습니다.",
            code=403
        )

    vote = Vote.query.filter_by(
        id=vote_id
    ).first()
    if vote is None:
        return error(
            message="해당 투표는 서버에서 삭제되었습니다.",
            code=404
        )

    result = fetch_result(
        vote_id=vote_id
    )

    csv = BOM_UTF8 + \
        "\n".join([f"{r[0]},{r[1]},{r[2]}" for r in [["선택지", "투표수", "득표율"]] + result]).encode("utf-8")

    return send_file(
        BytesIO(csv),
        as_attachment=True,
        attachment_filename=f"{vote.title}.csv",
        mimetype="text/csv; charset=utf-8"
    )
