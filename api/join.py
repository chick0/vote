from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status as _

from sql import get_session
from sql.models import Vote
from sql.models import VoteSession
from models.join import JoinRequest
from models.join import JoinResponse
from models.status import Status
from utils.token import create_token

router = APIRouter(tags=['Join'])
HTTP_201_CREATED = _.HTTP_201_CREATED


@router.post(
    "/join",
    description="투표 ID와 인증 코드를 이용해 투표에 참여합니다.",
    status_code=HTTP_201_CREATED,
    response_model=JoinResponse
)
async def join_vote(request: JoinRequest):
    session = get_session()
    vote: Vote = session.query(Vote).filter_by(
        id=request.vote_id,
        code=request.code,
    ).first()

    if vote is None:
        session.close()
        raise HTTPException(
            status_code=400,
            detail={
                "msg": "등록된 투표가 아닙니다."
            }
        )

    if vote.status == Status.FINISH.value:
        session.close()
        raise HTTPException(
            status_code=400,
            detail={
                "msg": "마감된 투표 입니다."
            }
        )

    if session.query(VoteSession).filter_by(
        vote_id=vote.id
    ).count() >= vote.max:
        session.close()
        raise HTTPException(
            status_code=400,
            detail={
                "msg": "투표 참여가 마감된 투표입니다."
            }
        )

    vote_session = VoteSession()
    vote_session.vote_id = vote.id
    vote_session.selected = False

    session.add(vote_session)
    session.commit()

    try:
        return JoinResponse(
            vote_id=request.vote_id,
            title=vote.title,
            token=create_token(
                vote_id=vote.id,
                session_id=vote_session.id,
                code=vote.code,
                exp=vote.deleted_at
            )
        )
    finally:
        session.close()
