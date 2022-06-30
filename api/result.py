from random import randint

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPBearer

from sql import get_session
from sql.models import Vote
from sql.models import VoteOption
from sql.models import VoteSession
from models.status import Status
from models.result import OptionScore
from models.result import VoteResult
from utils.token import parse_token

router = APIRouter(tags=['Result'])
auth = HTTPBearer()


def get_random_color() -> str:
    return "rgb({r},{g},{b})".format(
        r=randint(100, 250),
        g=randint(100, 250),
        b=randint(100, 250),
    )


@router.get(
    "/result",
    description="투표 결과를 확인합니다.",
    response_model=VoteResult
)
async def get_vote_result(token=Depends(auth)):
    def calc_percent(t) -> str:
        try:
            per = int(t / vote.max * 100)
            return f"{per} %"
        except ZeroDivisionError:
            return "-"

    payload = parse_token(token=token.credentials)
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

    if vote.status == Status.WAIT.value:
        session.close()
        raise HTTPException(
            status_code=400,
            detail={
                "msg": "마감된 투표가 아닙니다."
            }
        )

    if vote.status == Status.VOTE.value:
        if payload.session_id == "admin":
            vote.status = Status.FINISH.value
            session.commit()
        else:
            session.close()
            raise HTTPException(
                status_code=400,
                detail={
                    "msg": "마감된 투표가 아닙니다."
                }
            )

    options = session.query(VoteOption).filter_by(
        vote_id=vote.id
    ).all()

    score = {
        # option_id: score
    }

    for vote_session in session.query(VoteSession).filter_by(
        vote_id=vote.id
    ).all():
        vote_session: VoteSession = vote_session
        if vote_session.selected:
            if vote_session.select is None:
                # 해당 표는 기권 표 입니다.
                pass
            else:
                try:
                    score[vote_session.select] += 1
                except KeyError:
                    score[vote_session.select] = 1

    dropped = vote.max - sum(score.values())

    result = [
        OptionScore(
            name=option.name,
            score=score.get(option.id, 0),
            per=calc_percent(t=score.get(option.id, 0)),
            color=get_random_color()
        ) for option in options
    ]

    result.append(
        OptionScore(
            name='기권',
            score=dropped,
            per=calc_percent(t=dropped),
            color="rgb(102,102,102)"
        )
    )

    try:
        return VoteResult(
            result=result
        )
    finally:
        session.close()
