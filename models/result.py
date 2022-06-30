from pydantic import BaseModel


class OptionScore(BaseModel):
    name: str
    score: int
    per: str
    color: str


class VoteResult(BaseModel):
    result: list[OptionScore]
