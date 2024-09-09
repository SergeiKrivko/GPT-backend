import asyncio
import uuid
from datetime import datetime

from src.chats.schemas import ChatRead
from src.chats.service import ChatService
from src.gpt import gpt
from src.messages.repository import MessageRepository
from src.messages.schemas import MessageRead, MessageCreate
from src.replys.service import ReplyService
from src.sockets.manager import SocketManager
from src.utils.unitofwork import IUnitOfWork


class MessageService:
    def __init__(self, message_repository: MessageRepository, chat_service: ChatService, reply_service: ReplyService,
                 socket_manager: SocketManager):
        self.message_repository = message_repository
        self.chat_service = chat_service
        self.reply_service = reply_service
        self.socket_manager = socket_manager

        # self.socket_manager.subscribe('new_message', self.__on_new_message)

    async def get_messages(self, uow: IUnitOfWork, chat_uuid: uuid.UUID,
                           created_after=None, deleted_after=None) -> list[MessageRead]:
        async with uow:
            if created_after is not None:
                messages_list = await self.message_repository.get_all_created_after(uow.session, created_after,
                                                                                    chat_uuid=chat_uuid)
            elif deleted_after is not None:
                messages_list = await self.message_repository.get_all_deleted_after(uow.session, deleted_after,
                                                                                    chat_uuid=chat_uuid)
            else:
                messages_list = await self.message_repository.get_all(uow.session, chat_uuid=chat_uuid)
            res = []
            for message in messages_list:
                message_model = self.__message_dict_to_read_model(message)
                await self.__get_reply(uow, message_model)
                res.append(message_model)
            return res

    async def get_message(self, uow: IUnitOfWork, message_uuid: uuid.UUID):
        async with uow:
            message_dict = await self.message_repository.get(uow.session, uuid=message_uuid)
            if not message_dict:
                return None
            message_model = self.__message_dict_to_read_model(message_dict)
            await self.__get_reply(uow, message_model)
            return message_model

    async def __get_reply(self, uow: IUnitOfWork, message: MessageRead):
        reply_list = await self.reply_service.get_replys(uow, message.uuid)
        replys: dict[str: list[uuid.UUID]] = {}
        for reply in reply_list:
            if reply.type not in replys:
                replys[reply.type] = []
            replys[reply.type].append(reply)
        message.reply = replys

    async def add_message(self, uow: IUnitOfWork, chat: ChatRead, model: MessageCreate, user, prompt=False):
        async with uow:
            message_dict = self.__message_create_model_to_dict(model)
            message_dict['model'] = chat.model
            message_dict['temperature'] = chat.temperature

            new_id = message_dict['uuid']
            for key, item in model.reply:
                for message_id in item:
                    await self.reply_service.add_reply(uow, message_id, new_id, key)

            await self.message_repository.add(uow.session, message_dict)
            await uow.commit()
            message = self.__message_dict_to_read_model(message_dict)
            await self.socket_manager.emit_to_user(user, 'new_messages', [message])

            if prompt:
                asyncio.create_task(self.run_gpt(uow, chat, message, user)).done()

            return message_dict['uuid']

    async def mark_message_deleted(self, uow: IUnitOfWork, message_uuid: uuid.UUID, user):
        async with uow:
            await self.message_repository.edit(uow.session, message_uuid, {'deleted_at': datetime.now(tz=None)})
            await uow.commit()
            await self.socket_manager.emit_to_user(user, 'delete_messages', [message_uuid])
            return message_uuid

    async def run_gpt(self, uow, chat: ChatRead, message: MessageRead, user):
        res = []
        write_message = None
        async for el in gpt.async_stream_response([
            {'role': message.role, 'content': message.content}
        ]):
            print(f"Gpt answer part: {el}")
            if write_message is None:
                message_id = await self.add_message(uow, chat, MessageCreate(
                    chat_uuid=chat.uuid,
                    role='assistant',
                    content=el,
                ), user, prompt=False)
                write_message = await self.get_message(uow, message_id)
            else:
                await self.socket_manager.emit_to_user(user, 'message_add_content', {
                    'uuid': str(write_message.uuid),
                    'chat': str(chat.uuid),
                    'content': el,
                })
            res.append(el)

        await self.socket_manager.emit_to_user(user, 'message_finish', str(write_message.uuid))
        print(''.join(res))
        await self.message_repository.edit(uow.session, write_message.uuid, {
            'content': ''.join(res),
        })
        await uow.commit()


    # async def __on_new_message(self, uow: UOWDep, uid: str, data: dict, prompt=False):
    #     message = MessageCreate(**data)
    #     chat = await self.chat_service.get_chat(uow, message.chat_uuid)
    #     await self.add_message(uow, chat, message, uid, prompt)

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
