import uuid
from datetime import datetime

from src.chats.schemas import ChatRead
from src.chats.service import ChatService
from src.messages.repository import MessageRepository
from src.messages.schemas import MessageRead, MessageCreate
from src.replys.service import ReplyService

from src.utils.unitofwork import IUnitOfWork


class MessageService:
    STATUS_PROGRESS = 'progress'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'

    def __init__(self, message_repository: MessageRepository, chat_service: ChatService, reply_service: ReplyService):
        self.message_repository = message_repository
        self.chat_service = chat_service
        self.reply_service = reply_service

    async def get_message(self, uow: IUnitOfWork, message_uuid: uuid.UUID):
        async with uow:
            message_dict = await self.message_repository.get(uow.session, uuid=message_uuid)
            if not message_dict:
                return None
            return self.message_dict_to_read_model(message_dict)

    async def add_message(self, uow: IUnitOfWork, model: MessageCreate):
        async with uow:
            chat = await self.chat_service.get_chat(uow.session, model.chat_id)
            message_dict = self.message_create_model_to_dict(model)
            message_dict['model'] = chat.model
            message_dict['context_size'] = chat.context_size
            message_dict['temperature'] = chat.temperature

            await self.message_repository.add(uow.session, message_dict)
            await uow.commit()
            return message_dict['uuid']

    @staticmethod
    def message_dict_to_read_model(message_dict: dict) -> MessageRead:
        return MessageRead(
            uuid=message_dict['uuid'],
            chat_uuid=message_dict['chat_uuid'],
            created_at=message_dict['created_at'],
            deleted_at=message_dict['deleted_at'],
            role=message_dict['role'],
            content=message_dict['content'],
            model=message_dict['model'],
            context_size=message_dict['context_size'],
            temperature=message_dict['temperature'],
        )

    @staticmethod
    def message_create_model_to_dict(create_model: MessageCreate) -> dict:
        return {
            'uuid': uuid.uuid4(),
            'chat_uuid': create_model.chat_uuid,
            'created_at': datetime.now(tz=None),
            'deleted_at': None,
            'role': create_model.role,
            'content': create_model.content,
            'model': None,
            'context_size': 0,
            'temperature': 0.5,
        }
