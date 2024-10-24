from datetime import datetime
from typing import Callable
from inspect import iscoroutinefunction
from uuid import UUID

import socketio
from fastapi import HTTPException
from loguru import logger
from pydantic import BaseModel

from src.authentication.service import AuthenticationService
from src.utils.exceptions import AuthenticationError

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')


class SocketManager:
    def __init__(self, auth_service: AuthenticationService):
        self.__users: dict[UUID: list] = dict()
        self.__sids = dict()
        self.__auth_service = auth_service

        self.__subscribe('connect', self.__connect)
        self.__subscribe('disconnect', self.__disconnect)

    def __get_decorator(self, key, handler: Callable):
        async def func(sid, *args):
            if sid not in self.__sids:
                logger.warning(f"Socket '{key}' from {sid} received, but user not found")
                return
            user = self.__sids[sid]
            logger.info(f"Socket '{key}' from {sid} (user {user}) received")
            try:
                if iscoroutinefunction(handler):
                    res = await handler(user, *args)
                else:
                    res = handler(user, *args)
            except Exception as ex:
                logger.error(f"{ex.__class__.__name__}: {ex}")
                res = None
            resp = {
                'data': SocketManager.__data_to_json(res),
                'time': datetime.now().isoformat(),
            }
            if res:
                logger.info(f"Processing '{key}' from {sid} (user {user}) completed. Emitting answer")
            return resp
        return func

    def subscribe(self, key, handler: Callable):
        self.__subscribe(key, self.__get_decorator(key, handler))

    def subscribe_with_response(self, key, handler: Callable, response_key=None):
        dec = self.__get_decorator(key, handler)

        async def func(sid, *args):
            resp = await dec(sid, *args)
            await sio.emit(response_key or key, resp, to=sid)

        self.__subscribe(key, func)

    @staticmethod
    def __subscribe(key, func):
        sio.on(key, func)

    @staticmethod
    def __data_to_json(data):
        if isinstance(data, dict):
            return {key: SocketManager.__data_to_json(item) for key, item in data.items()}
        if isinstance(data, list):
            return [SocketManager.__data_to_json(data) for data in data]
        if isinstance(data, BaseModel):
            return data.model_dump(mode='json')
        return data

    async def emit_to_user(self, uid, key, data=None):
        data = {
            'data': SocketManager.__data_to_json(data),
            'time': datetime.now().isoformat(),
        }
        for sid in self.__users.get(uid, []):
            await sio.emit(key, data, to=sid)
            logger.info(f"Socket '{key}' emitted to {sid} (user {uid})")

    async def __connect(self, sid, environ, token=''):
        try:
            user = await self.__auth_service.get_authenticated_user(token)
        except AuthenticationError:
            logger.error(f"Client {sid} not connected: invalid token")
            return
        except HTTPException:
            logger.error(f"Client {sid} not connected: invalid token")
            return
        logger.info(f"Client connected: {sid} (user {user.uid})")
        if user.uid not in self.__users:
            self.__users[user.uid] = []
        self.__users[user.uid].append(sid)
        self.__sids[sid] = user.uid

    async def __disconnect(self, sid):
        logger.info(f"Client disconnected: {sid}")
        if sid not in self.__sids:
            return
        uid = self.__sids[sid]
        self.__sids.pop(sid)
        self.__users[uid].remove(sid)
        if not self.__users[uid]:
            self.__users.pop(uid)
