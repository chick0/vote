from sys import argv
from os.path import join

from fastapi import FastAPI

from app.init import init

try:
    version = open(join(".git", open(join(".git", "HEAD"), mode="r").read()[5:].strip()), mode="r").read()[:7]
except (FileNotFoundError, Exception):
    version = "*MISSING HEAD*"

app = FastAPI(
    title="Vote API & WS",
    description="QR코드로 참여하는 단순 투표 서비스",
    version=version,
    openapi_url="/openapi.json" if '--dev' in argv else None
)

init(app=app)
