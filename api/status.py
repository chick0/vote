from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPBearer

from sql import get_session
from sql.models import Vote
from sql.models import VoteSession
from models.status import VoteData
from utils.token import parse_token

router = APIRouter(tags=['Status'])
auth = HTTPBearer()


@router.get(
    "/status",
    description="투표의 상태를 불러옵니다.",
    response_model=VoteData,
)
async def get_vote_status(token=Depends(auth)):
    payload = parse_token(token=token.credentials)
    session = get_session()

    vote: Vote = session.query(Vote).filter_by(
        id=payload.vote_id,
        code=payload.code   
    ).first()

    if vote is None:
        raise HTTPException(
            status_code=404,
            detail={
                "msg": "등록된 투표가 아닙니다."
            }
        )

    joined = -1
    selected = -1

    if payload.session_id == "admin":
        joined = session.query(VoteSession).filter_by(
            vote_id=payload.vote_id
        ).count()

        selected = session.query(VoteSession).filter_by(
            vote_id=payload.vote_id,
            selected=True
        ).count()

    try:
        return VoteData(
            joined=joined,
            selected=selected,
            status=vote.status,
        )
    finally:
        session.close()
