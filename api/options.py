from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPBearer

from sql import get_session
from sql.models import VoteOption
from models.options import Option
from models.options import Options
from models.options import OptionRequest
from models.options import OptionDelete
from models.options import OptionDeleteResult
from utils.token import parse_token

router = APIRouter(tags=['Options'])
auth = HTTPBearer()


@router.get(
    "/options",
    description="투표에 등록된 선택지 목록을 불러옵니다.",
    response_model=Options
)
async def get_options(token=Depends(auth)):
    payload = parse_token(token=token.credentials)
    session = get_session()

    try:
        return Options(
            options=[
                Option(
                    id=x.id,
                    name=x.name
                )
                for x in session.query(VoteOption).filter_by(
                    vote_id=payload.vote_id
                ).all()
            ]
        )
    finally:
        session.close()


@router.post(
    "/options",
    description="새로운 선택지를 등록합니다.",
    response_model=Option
)
async def create_new_option(request: OptionRequest, token=Depends(auth)):
    payload = parse_token(token=token.credentials)
    if payload.session_id != "admin":
        raise HTTPException(
            status_code=403,
            detail={
                "msg": "권한이 부족합니다."
            }
        )

    name = request.name.strip()[:30]

    if len(name) == 0:
        raise HTTPException(
            status_code=400,
            detail={
                "msg": "빈 선택지는 만들 수 없습니다."
            }
        )

    session = get_session()

    if session.query(VoteOption).filter_by(
        vote_id=payload.vote_id,
        name=name
    ).count() != 0:
        session.close()
        raise HTTPException(
            status_code=400,
            detail={
                "msg": "중복된 선택지는 등록 할 수 없습니다."
            }
        )

    new_option = VoteOption()
    new_option.vote_id = payload.vote_id
    new_option.name = name

    session.add(new_option)
    session.commit()

    try:
        return Option(
            id=new_option.id,
            name=new_option.name
        )
    finally:
        session.close()


@router.patch(
    "/options",
    description="등록된 선택지를 수정합니다.",
    response_model=Option
)
async def update_option(request: Option, token=Depends(auth)):
    payload = parse_token(token=token.credentials)
    if payload.session_id != "admin":
        raise HTTPException(
            status_code=403,
            detail={
                "msg": "권한이 없습니다."
            }
        )

    name = request.name.strip()[:30]

    if len(name) == 0:
        raise HTTPException(
            status_code=400,
            detail={
                "msg": "빈 선택지는 만들 수 없습니다."
            }
        )

    session = get_session()

    if session.query(VoteOption).filter_by(
        vote_id=payload.vote_id,
        name=name
    ).count() != 0:
        session.close()
        raise HTTPException(
            status_code=400,
            detail={
                "msg": "중복된 선택지는 등록 할 수 없습니다."
            }
        )

    option: VoteOption = session.query(VoteOption).filter_by(
        id=request.id,
        vote_id=payload.vote_id
    ).first()

    option.name = name
    session.commit()

    try:
        return Option(
            id=option.id,
            name=option.name
        )
    finally:
        session.close()


@router.delete(
    "/options",
    description="등록된 선택지를 삭제합니다.",
    response_model=OptionDeleteResult
)
async def update_option(request: OptionDelete, token=Depends(auth)):
    payload = parse_token(token=token.credentials)
    if payload.session_id != "admin":
        raise HTTPException(
            status_code=403,
            detail={
                "msg": "권한이 없습니다."
            }
        )

    session = get_session()
    deleted = session.query(VoteOption).filter_by(
        id=request.id,
        vote_id=payload.vote_id
    ).delete()

    session.commit()
    session.close()

    return OptionDeleteResult(
        result=deleted == 1
    )
