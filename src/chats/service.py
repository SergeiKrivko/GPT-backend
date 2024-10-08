import random
import uuid
from datetime import datetime

from src.chats.repository import ChatRepository
from src.chats.schemas import ChatRead, ChatUpdate
from src.sockets.manager import SocketManager
from src.utils.unitofwork import IUnitOfWork


class ChatService:
    def __init__(self, chat_repository: ChatRepository, sockets_manager: SocketManager):
        self.chat_repository = chat_repository
        self.socket_manager = sockets_manager

    async def get_chats(self, uow: IUnitOfWork, user: uuid.UUID, created_after: datetime = None,
                        deleted_after: datetime = None, updated_after: datetime = None) -> list[ChatRead]:
        async with uow:
            if created_after is not None:
                chats_list = await self.chat_repository.get_all_created_after(uow.session, created_after,
                                                                              deleted_at=None, user=user)
            elif updated_after is not None:
                chats_list = await self.chat_repository.get_all_updated_after(uow.session, updated_after,
                                                                              deleted_at=None, user=user)
            elif deleted_after is not None:
                chats_list = await self.chat_repository.get_all_deleted_after(uow.session, deleted_after, user=user)
            else:
                chats_list = await self.chat_repository.get_all(uow.session, user=user, deleted_at=None)
            return [self.chat_dict_to_read_model(chat) for chat in chats_list]

    async def get_chat(self, uow: IUnitOfWork, chat_uuid: uuid.UUID):
        async with uow:
            chat_dict = await self.chat_repository.get(uow.session, uuid=chat_uuid)
            if not chat_dict:
                return None
            return self.chat_dict_to_read_model(chat_dict)

    async def add_chat(self, uow: IUnitOfWork, user: str):
        async with uow:
            chat_dict = self.chat_create_model_to_dict()
            chat_dict['user'] = user

            await self.chat_repository.add(uow.session, chat_dict)
            await uow.commit()
            await self.socket_manager.emit_to_user(user, 'new_chats', [self.chat_dict_to_read_model(chat_dict)])

            return chat_dict['uuid']

    async def update_chat(self, uow: IUnitOfWork, chat_uuid: uuid.UUID, chat: ChatUpdate, user: str):
        async with uow:
            chat_dict = self.chat_update_model_to_dict(chat)
            await self.chat_repository.edit(uow.session, chat_uuid, chat_dict)
            await uow.commit()

            chat_dict = await self.chat_repository.get(uow.session, uuid=chat_uuid)
            await self.socket_manager.emit_to_user(user, 'update_chat', self.chat_dict_to_read_model(chat_dict))
            return chat_uuid

    async def mark_chat_deleted(self, uow: IUnitOfWork, chat_uuid: uuid.UUID, user: str):
        async with uow:
            await self.chat_repository.edit(uow.session, chat_uuid, {'deleted_at': datetime.now(tz=None)})
            await uow.commit()
            await self.socket_manager.emit_to_user(user, 'delete_chats', [str(chat_uuid)])
            return chat_uuid

    @staticmethod
    def chat_dict_to_read_model(chat_dict: dict) -> ChatRead:
        return ChatRead(
            uuid=chat_dict['uuid'],
            created_at=chat_dict['created_at'],
            deleted_at=chat_dict['deleted_at'],
            name=chat_dict['name'],
            model=chat_dict['model'],
            context_size=chat_dict['context_size'],
            temperature=chat_dict['temperature'],
            pinned=chat_dict['pinned'],
            archived=chat_dict['archived'],
            color=chat_dict['color'],
            user=chat_dict['user'],
        )

    @staticmethod
    def chat_create_model_to_dict() -> dict:
        return {
            'uuid': uuid.uuid4(),
            'created_at': datetime.now(tz=None),
            'deleted_at': None,
            'name': '',
            'model': None,
            'context_size': 0,
            'temperature': 0.5,
            'pinned': False,
            'archived': False,
            'color': random.randint(0, 5),
        }

    @staticmethod
    def chat_update_model_to_dict(chat: ChatUpdate) -> dict:
        res = {
            'updated_at': datetime.now(tz=None),
        }
        if chat.name is not None:
            res['name'] = chat.name
        if chat.model is not None:
            res['model'] = chat.model
        if chat.context_size is not None:
            res['context_size'] = chat.context_size
        if chat.temperature is not None:
            res['temperature'] = chat.temperature
        if chat.pinned is not None:
            res['pinned'] = chat.pinned
        if chat.archived is not None:
            res['archived'] = chat.archived
        return res
