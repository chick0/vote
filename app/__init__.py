from sys import argv
from subprocess import run

from fastapi import FastAPI

from app.init import init

try:
    version = run("git rev-parse --short HEAD", capture_output=True).stdout.strip().decode()
except:
    version = "fail to fetch version"

app = FastAPI(
    title="Vote API & WS",
    description="QR코드로 참여하는 단순 투표 서비스",
    version=version,
    openapi_url="/openapi.json" if '--dev' in argv else None
)

init(app=app)
