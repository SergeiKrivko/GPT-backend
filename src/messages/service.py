import asyncio
import uuid
from datetime import datetime

from loguru import logger

from src.chats.schemas import ChatRead
from src.chats.service import ChatService
from src.gpt import gpt
from src.messages.repository import MessageRepository
from src.messages.schemas import MessageRead, MessageCreate
from src.replys.repository import ReplyRepository
from src.replys.schemas import ReplyCreate, ReplyRead
from src.sockets.manager import SocketManager
from src.utils.unitofwork import IUnitOfWork, UnitOfWork


class MessageService:
    def __init__(self, message_repository: MessageRepository, chat_service: ChatService,
                 reply_repository: ReplyRepository,
                 socket_manager: SocketManager):
        self.message_repository = message_repository
        self.chat_service = chat_service
        self.reply_repository = reply_repository
        self.socket_manager = socket_manager

    async def get_messages(self, uow: IUnitOfWork, chat_uuid: uuid.UUID = None, user: str = None,
                           created_after=None, deleted_after=None) -> list[MessageRead]:
        filters = dict()
        if user is not None:
            filters['user'] = user
        if chat_uuid is not None:
            filters['chat_uuid'] = chat_uuid
        async with uow:
            if created_after is not None:
                messages_list = await self.message_repository.get_all_created_after(uow.session, created_after,
                                                                                    **filters)
            elif deleted_after is not None:
                messages_list = await self.message_repository.get_all_deleted_after(uow.session, deleted_after,
                                                                                    **filters)
            else:
                messages_list = await self.message_repository.get_all(uow.session, **filters)
            res = []
            for message in messages_list:
                message_model = self.__message_dict_to_read_model(message)
                reply_list = await self.__get_reply(uow, message_model)
                message_model.reply = reply_list
                res.append(message_model)
            return res

    async def get_message(self, uow: IUnitOfWork, message_uuid: uuid.UUID):
        async with uow:
            message_dict = await self.message_repository.get(uow.session, uuid=message_uuid)
            if not message_dict:
                return None
            message_model = self.__message_dict_to_read_model(message_dict)
            reply_list = await self.__get_reply(uow, message_model)
            message_model.reply = reply_list
            return message_model

    async def __get_reply(self, uow: IUnitOfWork, message: MessageRead) -> list[ReplyRead]:
        reply_list = await self.reply_repository.get_all(uow.session, from_uuid=message.uuid)
        return [ReplyRead(
            uuid=r['uuid'],
            message_uuid=r['from_uuid'],
            reply_to=r['to_uuid'],
            type=r['type']) for r in reply_list]

    async def add_message(self, uow: IUnitOfWork, chat: ChatRead, model: MessageCreate, user, prompt=False):
        async with uow:
            message_dict = self.__message_create_model_to_dict(model)
            message_dict['user'] = user
            message_dict['model'] = chat.model
            message_dict['temperature'] = chat.temperature

            await self.message_repository.add(uow.session, message_dict)

            new_id = message_dict['uuid']
            for item in model.reply:
                await self.reply_repository.add(uow.session, {
                    'uuid': uuid.uuid4(),
                    'from_uuid': new_id,
                    'to_uuid': item.reply_to,
                    'type': item.type,
                })

            await uow.commit()
            message = self.__message_dict_to_read_model(message_dict)
            await self.socket_manager.emit_to_user(user, 'new_messages', [message])

            if prompt:
                asyncio.create_task(self.run_gpt(UnitOfWork(), chat, message, user)).done()

            return message_dict['uuid']

    async def mark_message_deleted(self, uow: IUnitOfWork, message_uuid: uuid.UUID, user):
        async with uow:
            await self.message_repository.edit(uow.session, message_uuid, {'deleted_at': datetime.now(tz=None)})
            await uow.commit()
            await self.socket_manager.emit_to_user(user, 'delete_messages', [message_uuid])
            return message_uuid

    async def run_gpt(self, uow: IUnitOfWork, chat: ChatRead, message: MessageRead, user):
        async with uow:
            res = []
            write_message = None
            logger.info(f"Request to GPT for {user}")
            try:
                context_messages = await self.message_repository.get_context(uow.session, chat.uuid, message.created_at,
                                                                             chat.context_size)
                prompt = [
                    *[{'role': m['role'], 'content': m['content']} for m in reversed(context_messages)],
                    {'role': message.role, 'content': message.content}
                ]
                logger.debug(f"GPT prompt (from {user}): {prompt}")
                async for el in gpt.async_stream_response(prompt):
                    logger.debug(f"Gpt answer (user {user}) part: {repr(el)}")
                    if write_message is None:
                        message_id = await self.add_message(uow, chat, MessageCreate(
                            chat_uuid=chat.uuid,
                            role='assistant',
                            content=el,
                            reply=[
                                ReplyCreate(reply_to=message.uuid, type='prompt'),
                                *[ReplyCreate(reply_to=m['uuid'], type='context') for m in context_messages]
                            ]
                        ), user, prompt=False)

                        write_message = await self.get_message(uow, message_id)
                    else:
                        await self.socket_manager.emit_to_user(user, 'message_add_content', {
                            'uuid': str(write_message.uuid),
                            'chat': str(chat.uuid),
                            'content': el,
                        })
                    res.append(el)
            except Exception as ex:
                logger.error(f"{ex.__class__.__name__}: {ex}")
                await self.socket_manager.emit_to_user(user, 'gpt_error', f"{ex.__class__.__name__}: {ex}")
            else:
                await self.socket_manager.emit_to_user(user, 'message_finish', str(write_message.uuid))
                logger.info(f"GPT finished for {user}: {repr(''.join(res))}")
            await self.message_repository.edit(uow.session, write_message.uuid, {
                'content': ''.join(res),
            })
            await uow.commit()

    @staticmethod
    def __message_dict_to_read_model(message_dict: dict) -> MessageRead:
        return MessageRead(
            uuid=message_dict['uuid'],
            chat_uuid=message_dict['chat_uuid'],
            created_at=message_dict['created_at'],
            deleted_at=message_dict['deleted_at'],
            role=message_dict['role'],
            content=message_dict['content'],
            model=message_dict['model'],
            temperature=message_dict['temperature'],
        )

    @staticmethod
    def __message_create_model_to_dict(create_model: MessageCreate) -> dict:
        return {
            'uuid': uuid.uuid4(),
            'chat_uuid': create_model.chat_uuid,
            'created_at': datetime.now(tz=None),
            'deleted_at': None,
            'role': create_model.role,
            'content': create_model.content,
            'model': None,
            'temperature': 0.5,
        }
