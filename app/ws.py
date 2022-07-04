from asyncio import sleep
from asyncio import wait_for
from asyncio.exceptions import TimeoutError

from fastapi import HTTPException
from starlette.websockets import WebSocket
from starlette.websockets import WebSocketState
from starlette.websockets import WebSocketDisconnect
from websockets.exceptions import ConnectionClosedOK
from websockets.exceptions import ConnectionClosedError

from sql import get_session
from sql.models import Vote
from sql.models import VoteSession
from utils.token import parse_token


async def vote(websocket: WebSocket):
    await websocket.close()

    try:
        token = await wait_for(fut=websocket.receive_text(), timeout=5)
        payload = parse_token(token=token)
    except TimeoutError:
        await websocket.close(reason="인증 토큰을 전달 받지 못했습니다.")
        return
    except HTTPException:
        await websocket.close(reason="인증 토큰이 올바르지 않습니다.")
        return
    except (WebSocketDisconnect, Exception):
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close(reason="알 수 없는 오류가 발생했습니다.")

        return

    try:
        while True:
            session = get_session()

            _vote: Vote = session.query(Vote).filter_by(
                id=payload.vote_id,
                code=payload.code
            ).with_entities(
                Vote.status
            ).first()

            if _vote is None:
                session.close()
                await websocket.close(reason="서버에 등록된 투표가 아닙니다.")
                return

            await websocket.send_text(
                "{vote_id},{status}".format(
                    vote_id=payload.vote_id,
                    status=_vote.status
                )
            )

            session.close()
            await sleep(5)
    except (WebSocketDisconnect, Exception):
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close(reason="알 수 없는 오류가 발생했습니다.")
    finally:
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close()


async def panel(websocket: WebSocket):
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
    except (WebSocketDisconnect, Exception):
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close(reason="알 수 없는 오류가 발생했습니다.")

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
