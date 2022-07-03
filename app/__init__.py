from sys import argv
from os.path import join
from subprocess import run

from fastapi import FastAPI

from app.init import init

try:
    version = run("git rev-parse --short HEAD", capture_output=True).stdout.strip().decode()
    raise NotImplementedError
except:
    version = None

if version is None:
    try:
        version = open(join(".git", open(join(".git", "HEAD"), mode="r").read()[5:].strip()), mode="r").read()[:7]
    except:
        version = "fail to get version"

app = FastAPI(
    title="Vote API & WS",
    description="QR코드로 참여하는 단순 투표 서비스",
    version=version,
    openapi_url="/openapi.json" if '--dev' in argv else None
)

init(app=app)
