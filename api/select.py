from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPBearer

from sql import get_session
from sql.models import Vote
from sql.models import VoteOption
from sql.models import VoteSession
from models.select import SelectRequest
from models.select import SelectResponse
from models.status import Status
from utils.token import parse_token

router = APIRouter(tags=['Select'])
auth = HTTPBearer()


@router.post(
    "/select",
    description="",
    response_model=SelectResponse
)
async def vote_select(request: SelectRequest, token=Depends(auth)):
    payload = parse_token(token=token.credentials)
    if payload.session_id == "admin":
        raise HTTPException(
            status_code=400,
            detail={
                "msg": "투표 관리자는 투표에 참여 할 수 없습니다."
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

    if vote.status != Status.VOTE.value:
        session.close()
        raise HTTPException(
            status_code=400,
            detail={
                "msg": "지금은 투표에 참여 할 수 없습니다."
            }
        )

    if request.option_id != -1:
        if session.query(VoteOption).filter_by(
            id=request.option_id,
            vote_id=payload.vote_id
        ).count() != 1:
            session.close()
            raise HTTPException(
                status_code=404,
                detail={
                    "msg": "등록된 선택지가 아닙니다."
                }
            )

    vote_session: VoteSession = session.query(VoteSession).filter_by(
        id=payload.session_id,
        vote_id=payload.vote_id
    ).first()

    if vote_session.selected is True:
        session.close()
        raise HTTPException(
            status_code=400,
            detail={
                "msg": "이미 투표하셨습니다."
            }
        )

    if vote_session is None:
        session.close()
        raise HTTPException(
            status_code=400,
            detail={
                "msg": "등록된 세션이 아닙니다."
            }
        )

    vote_session.selected = True
    vote_session.select = request.option_id if request.option_id != -1 else None

    session.commit()
    session.close()

    return SelectResponse(
        result=True
    )
