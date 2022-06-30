from typing import Any

from fastapi import HTTPException
from starlette.endpoints import WebSocketEndpoint
from starlette.websockets import WebSocket

from app.middleware import SocketStore
from utils.token import parse_token


class VoteWebSocketHandler(WebSocketEndpoint):
    encoding = "text"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sockets: SocketStore = args[0]['sockets']
        self.payload = None

    async def on_connect(self, websocket: WebSocket) -> None:
        await websocket.accept()

    async def on_receive(self, websocket: WebSocket, data: Any) -> None:
        if self.payload is None:
            try:
                self.payload = parse_token(token=data)

                await self.sockets.push_socket(
                    vote_id=self.payload.vote_id,
                    ws=websocket
                )
            except HTTPException:
                # fail to parse jwt token
                await websocket.close()

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        if self.payload is None:
            return

        await self.sockets.pop_socket(
            vote_id=self.payload.vote_id,
            ws=websocket
        )
