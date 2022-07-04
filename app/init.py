from os import environ

from fastapi import APIRouter
from fastapi.applications import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import api
from app.ws import vote
from app.ws import panel


def init(app: FastAPI):
    class Version(BaseModel):
        version: str = app.version

    @app.get(
        "/api/version",
        response_model=Version,
        tags=["Version"]
    )
    async def get_version():
        return Version()

    router = APIRouter(prefix="/api")
    for module in [getattr(api, x) for x in api.__all__]:
        router.include_router(module.router)

    app.include_router(router=router)
    app.add_websocket_route("/ws/vote", vote)
    app.add_websocket_route("/ws/panel", panel)

    # setup cors
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[environ['HOST'].strip()],
        allow_methods=["GET", "PATCH", "POST", "DELETE"],
        allow_headers=["Authorization"]
    )
