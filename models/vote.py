from pydantic import BaseModel


class CreateRequest(BaseModel):
    title: str
    max: int


class CreateResponse(BaseModel):
    vote_id: int
    title: str
    token: str


class VoteInformation(BaseModel):
    title: str
    status: int


class StatusUpdated(BaseModel):
    msg: str
