from pydantic import BaseModel


class RestartResult(BaseModel):
    result: bool
