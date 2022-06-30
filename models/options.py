from pydantic import BaseModel


class Option(BaseModel):
    id: int
    name: str


class Options(BaseModel):
    options: list[Option]


class OptionRequest(BaseModel):
    name: str


class OptionDelete(BaseModel):
    id: int


class OptionDeleteResult(BaseModel):
    result: bool
