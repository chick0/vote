from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPBearer

from sql import get_session
from sql.models import Vote
from sql.models import VoteSession
from models.restart import RestartResult
from models.status import Status
from utils.token import parse_token

router = APIRouter(tags=['Restart'])
auth = HTTPBearer()


@router.patch(
    "/restart",
    description="*마감된* 투표를 재시작 합니다.",
    response_model=RestartResult
)
async def vote_restart(token=Depends(auth)):
    payload = parse_token(token=token.credentials)
    if payload.session_id != "admin":
        raise HTTPException(
            status_code=403,
            detail={
                "msg": "권한이 없습니다."
            }
        )

    session = get_session()

    vote: Vote = session.query(Vote).filter_by(
        id=payload.vote_id,
        code=payload.code
    ).first()

    if vote is None:
        session.close()
        raise HTTPException(
            status_code=404,
            detail={
                "msg": "등록된 투표가 아닙니다."
            }
        )

    if vote.status != Status.FINISH.value:
        session.close()
        raise HTTPException(
            status_code=400,
            detail={
                "msg": "마감된 투표만 재시작 할 수 있습니다."
            }
        )

    vote.status = Status.WAIT.value

    for vs in session.query(VoteSession).filter_by(
        vote_id=payload.vote_id
    ).all():
        vs.select = None
        vs.selected = False

    session.commit()
    session.close()

    return RestartResult(
        result=True
    )
