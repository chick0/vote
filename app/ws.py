from typing import Any
from asyncio import sleep
from asyncio import wait_for
from asyncio.exceptions import TimeoutError

from fastapi import HTTPException
from starlette.endpoints import WebSocketEndpoint
from starlette.websockets import WebSocket
from starlette.websockets import WebSocketState
from starlette.websockets import WebSocketDisconnect
from websockets.exceptions import ConnectionClosedOK
from websockets.exceptions import ConnectionClosedError

from sql import get_session
from sql.models import VoteSession
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


async def panel_ws_handler(websocket: WebSocket):
    await websocket.accept()

    try:
        token = await wait_for(fut=websocket.receive_text(), timeout=3)
        payload = parse_token(token=token)
    except TimeoutError:
        await websocket.close(reason="인증 토큰을 전달 받지 못했습니다.")
        return
    except HTTPException:
        await websocket.close(reason="인증 토큰이 올바르지 않습니다.")
        return

    try:
        while True:
            session = get_session()

            await websocket.send_text(
                "{joined},{selected}".format(
                    joined=session.query(VoteSession).filter_by(
                        vote_id=payload.vote_id
                    ).count(),
                    selected=session.query(VoteSession).filter_by(
                        vote_id=payload.vote_id,
                        selected=True
                    ).count()
                )
            )

            session.close()
            await sleep(5)
    except (WebSocketDisconnect, ConnectionClosedOK, ConnectionClosedError):
        pass
    finally:
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close()
