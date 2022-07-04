from enum import Enum

from pydantic import BaseModel


class Status(Enum):
    WAIT = 0
    VOTE = 1
    FINISH = 2


class VoteData(BaseModel):
    joined: int
    selected: int
    status: int
