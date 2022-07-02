from os import environ
from datetime import datetime

from fastapi import HTTPException
from pydantic import BaseModel
from jwt import decode
from jwt import encode
from jwt.exceptions import DecodeError
from jwt.exceptions import ExpiredSignatureError

algorithms = ["HS256"]


class Payload(BaseModel):
    vote_id: int
    session_id: int or str = "\"admin\" or session_id"
    code: str
    exp: int


def parse_token(token: str) -> Payload:
    try:
        return Payload(**decode(
            jwt=token,
            key=environ['JWT_SECRET'],
            algorithms=algorithms
        ))
    except DecodeError:
        raise HTTPException(
            status_code=403,
            detail={
                "msg": "인증 토큰이 올바르지 않습니다."
            }
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail={
                "msg": "만료된 인증 토큰입니다."
            }
        )


def create_token(vote_id: int, session_id: int or str, code: str, exp: datetime) -> str:
    return encode(
        payload=Payload(
            vote_id=vote_id,
            session_id=session_id,
            code=code,
            exp=int(exp.timestamp())
        ).dict(),
        key=environ['JWT_SECRET'],
        algorithm=algorithms[0]
    )
