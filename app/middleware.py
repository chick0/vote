from typing import Dict

from starlette.types import ASGIApp
from starlette.types import Scope
from starlette.types import Receive
from starlette.types import Send
from starlette.websockets import WebSocket
from starlette.websockets import WebSocketState
from websockets.exceptions import ConnectionClosedOK


class SocketStore:
    def __init__(self):
        self._sockets: Dict[int, list[WebSocket]] = {}

    async def pop_socket(self, vote_id: int, ws: WebSocket):
        try:
            self._sockets[vote_id].remove(ws)
        except (KeyError, ValueError):
            pass

        try:
            if len(self._sockets[vote_id]) == 0:
                del self._sockets[vote_id]
        except KeyError:
            pass

    async def fetch_sockets(self, vote_id: int) -> list[WebSocket]:
        return [
            socket
            for socket in self._sockets.get(vote_id, [])
            if socket.client_state == WebSocketState.CONNECTED
        ]

    async def broadcast(self, vote_id: int):
        for socket in await self.fetch_sockets(vote_id=vote_id):
            try:
                await socket.send_text("200=socket_updated")
            except (ConnectionClosedOK, Exception):
                await self.pop_socket(
                    vote_id=vote_id,
                    ws=socket
                )

    async def push_socket(self, vote_id: int, ws: WebSocket):
        try:
            self._sockets[vote_id].append(ws)
        except KeyError:
            self._sockets[vote_id] = [ws]


class VoteMiddleware:
    def __init__(self, app: ASGIApp):
        self._app = app
        self._sockets = SocketStore()

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] in ("lifespan", "http", "websocket"):
            scope["sockets"] = self._sockets

        await self._app(scope, receive, send)
