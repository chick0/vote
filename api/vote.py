from os import urandom

from fastapi import APIRouter
from fastapi import Request
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status as _
from fastapi.security import HTTPBearer
from sqlalchemy.exc import IntegrityError

from sql import get_session
from sql.models import Vote
from models.vote import CreateRequest
from models.vote import CreateResponse
from models.vote import VoteInformation
from models.vote import StatusUpdated
from models.status import Status
from utils.token import create_token
from utils.token import parse_token

router = APIRouter(tags=['Vote'])
auth = HTTPBearer()
HTTP_201_CREATED = _.HTTP_201_CREATED


@router.post(
    "/vote",
    description="새로운 투표를 생성합니다.",
    status_code=HTTP_201_CREATED,
    response_model=CreateResponse
)
async def create_vote(request: CreateRequest):
    vote = Vote()
    vote.title = request.title.strip()[:30]
    vote.max = request.max
    vote.status = Status.WAIT.value
    vote.code = urandom(3).hex()

    if len(vote.title) == 0:
        vote.title = "제목 없는 투표"

    if vote.max > 50:
        raise HTTPException(
            status_code=400,
            detail={
                "msg": "최대 50명까지 참여가 가능합니다."
            }
        )
    elif vote.max <= 2:
        raise HTTPException(
            status_code=400,
            detail={
                "msg": "투표 참여 인원은 3명 이상으로 설정해야 합니다."
            }
        )

    session = get_session()

    try:
        session.add(vote)
        session.commit()
    except IntegrityError:
        session.close()

        raise HTTPException(
            status_code=500,
            detail={
                "msg": "투표를 등록하는 과정에서 오류가 발생했습니다. 다시 시도해주세요."
            }
        )

    try:
        return CreateResponse(
            vote_id=vote.id,
            title=vote.title,
            token=create_token(
                vote_id=vote.id,
                session_id="admin",
                code=vote.code,
                exp=vote.deleted_at
            )
        )
    finally:
        session.close()


@router.get(
    "/vote",
    description="투표 정보를 불러옵니다.",
    response_model=VoteInformation
)
async def get_vote_information(token=Depends(auth)):
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

    try:
        return VoteInformation(
            title=vote.title,
            status=vote.status
        )
    finally:
        session.close()


@router.patch(
    "/vote",
    description="투표의 상태를 변경합니다. (대기중 -> 투표중)",
    response_model=StatusUpdated
)
async def update_vote_status(ctx: Request, token=Depends(auth)):
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
        raise HTTPException(
            status_code=404,
            detail={
                "msg": "등록된 투표가 아닙니다."
            }
        )

    if vote.status == Status.VOTE.value:
        raise HTTPException(
            status_code=400,
            detail={
                "msg": "이미 진행중인 투표입니다."
            }
        )

    if vote.status == Status.FINISH.value:
        raise HTTPException(
            status_code=400,
            detail={
                "msg": "마감된 투표는 시작할 수 없습니다."
            }
        )

    vote.status = Status.VOTE.value
    session.commit()
    session.close()

    await ctx.scope['sockets'].broadcast(
        vote_id=payload.vote_id
    )

    return StatusUpdated(
        msg="투표가 시작되었습니다. "
            "이제 선택지를 수정 할 수 없습니다."
    )
