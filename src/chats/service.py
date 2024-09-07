import uuid
from datetime import datetime

from src.chats.repository import ChatRepository
from src.chats.schemas import ChatRead, ChatUpdate
from src.utils.socket_manager import sio

from src.utils.unitofwork import IUnitOfWork


class ChatService:
    STATUS_PROGRESS = 'progress'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'

    def __init__(self, chat_repository: ChatRepository):
        self.chat_repository = chat_repository

    async def get_chats(self, uow: IUnitOfWork, user: uuid.UUID) -> list[ChatRead]:
        async with uow:
            chats_list = await self.chat_repository.get_all(uow.session, user=user)
            res = []
            for chat in chats_list:
                res.append(self.chat_dict_to_read_model(chat))
            return res

    async def get_chat(self, uow: IUnitOfWork, chat_uuid: uuid.UUID):
        async with uow:
            chat_dict = await self.chat_repository.get(uow.session, uuid=chat_uuid)
            if not chat_dict:
                return None
            return self.chat_dict_to_read_model(chat_dict)

    async def add_chat(self, uow: IUnitOfWork, user: uuid.UUID):
        async with uow:
            chat_dict = self.chat_create_model_to_dict()
            chat_dict['user'] = user

            await self.chat_repository.add(uow.session, chat_dict)
            await uow.commit()
            sio.emit('new_chats', [chat_dict])

            return chat_dict['uuid']

    async def update_chat(self, uow: IUnitOfWork, chat_uuid: uuid.UUID, chat: ChatUpdate):
        async with uow:
            chat_dict = self.chat_update_model_to_dict(chat)
            await self.chat_repository.edit(uow.session, chat_uuid, chat_dict)
            await uow.commit()
            sio.emit('update_chats', [chat_dict])
            return chat_uuid

    async def mark_chat_deleted(self, uow: IUnitOfWork, chat_uuid: uuid.UUID):
        async with uow:
            await self.chat_repository.edit(uow.session, chat_uuid, {'deleted_at': datetime.now(tz=None)})
            await uow.commit()
            sio.emit('delete_chats', [chat_uuid])
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
        }

    @staticmethod
    def chat_update_model_to_dict(chat: ChatUpdate) -> dict:
        return {
            'uuid': chat.uuid,
            'name': chat.name,
            'model': chat.model,
            'context_size': chat.context_size,
            'temperature': chat.temperature,
        }
