from io import BytesIO
from os import environ
from base64 import b64encode

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPBearer
from qrcode import make

from models.qrcode import QRImage
from utils.token import parse_token

router = APIRouter(tags=['QRcode'])
auth = HTTPBearer()


@router.get(
    "/qrcode",
    description="투표 참여 QR코드를 생성합니다.",
    response_model=QRImage
)
async def get_join_qrcode(token=Depends(auth)):
    payload = parse_token(token=token.credentials)
    if payload.session_id != "admin":
        raise HTTPException(
            status_code=403,
            detail={
                "msg": "투표 생성자만 QR코드를 생성 할 수 있습니다."
            }
        )

    raw = BytesIO()
    img = make(
        data="{host}{path}".format(
            host=environ['HOST'],
            path="/#/join/{vote_id}/{code}".format(
                vote_id=payload.vote_id,
                code=payload.code
            )
        ),
        border=1,
    )

    img.save(raw, "PNG")
    raw.seek(0)

    return QRImage(
        image="data:image/png;base64," + b64encode(raw.read()).decode()
    )
