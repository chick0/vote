from pydantic import BaseModel


class QRImage(BaseModel):
    image: str = "base64 encoded"
