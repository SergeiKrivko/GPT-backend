from datetime import datetime
from typing import Callable, Any
from inspect import iscoroutinefunction
from uuid import UUID

import socketio
from pydantic import BaseModel

from src.authentication.schemas import UserRead
from src.authentication.service import AuthenticationService
from src.utils.unitofwork import UnitOfWork, IUnitOfWork

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')


class SocketManager:
    def __init__(self, auth_service: AuthenticationService):
        self.__users: dict[UUID: list] = dict()
        self.__sids = dict()
        self.__auth_service = auth_service

        self.__subscribe('connect', self.__connect)
        self.__subscribe('disconnect', self.__disconnect)
        self.__unit_of_work = UnitOfWork()

    def subscribe(self, key, handler: Callable):
        async def func(sid, *args):
            if iscoroutinefunction(handler):
                await handler(self.__sids[sid], self.__unit_of_work, *args)
            else:
                handler(self.__sids[sid], self.__unit_of_work, *args)
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
            print(f"socket '{key}' emitted to", sid)

    async def __connect(self, sid, environ, token=''):
        user = await self.__auth_service.get_authenticated_user(token)
        print(f"Client connected: {sid} (user {user.uid})")
        if user.uid not in self.__users:
            self.__users[user.uid] = []
        self.__users[user.uid].append(sid)
        self.__sids[sid] = user.uid

    async def __disconnect(self, sid):
        print("Client disconnected:", sid)
        uid = self.__sids[sid]
        self.__sids.pop(sid)
        self.__users[uid].remove(sid)
        if not self.__users[uid]:
            self.__users.pop(uid)