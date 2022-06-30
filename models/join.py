from pydantic import BaseModel


class JoinRequest(BaseModel):
    vote_id: int
    code: str


class JoinResponse(BaseModel):
    vote_id: int
    token: str
