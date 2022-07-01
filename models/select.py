from pydantic import BaseModel


class SelectRequest(BaseModel):
    option_id: int


class SelectResponse(BaseModel):
    result: bool
