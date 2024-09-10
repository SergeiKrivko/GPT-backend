import uuid
from datetime import datetime

from src.chats.schemas import ChatUpdate
from src.messages.schemas import MessageCreate
from src.utils.dependency import UnitOfWork, chat_service, message_service, socket_manager


async def on_new_chat(uid: str):
    await chat_service.add_chat(UnitOfWork(), uid)


async def on_delete_chat(uid: str, chat_id: uuid.UUID):
    # TODO: добавить проверки
    await chat_service.mark_chat_deleted(UnitOfWork(), chat_id, uid)


async def on_update_chat(uid: str, chat_id=None, chat=None):
    # TODO: добавить проверки
    await chat_service.update_chat(UnitOfWork(), chat_id, ChatUpdate(**chat), uid)


async def on_new_message(uid: str, data: dict, prompt=False):
    # TODO: добавить проверки
    message = MessageCreate(**data)
    chat = await chat_service.get_chat(uow := UnitOfWork(), message.chat_uuid)
    await message_service.add_message(uow, chat, message, uid, prompt)


async def on_delete_message(uid: str, message_id: uuid.UUID):
    # TODO: добавить проверки
    await message_service.mark_message_deleted(UnitOfWork(), message_id, uid)


async def on_request_updates(uid: str, timestamp):
    print(f"Request updates: {timestamp}")
    timestamp = datetime.fromisoformat(timestamp).replace(tzinfo=None)
    print(timestamp, timestamp.__class__)
    uow = UnitOfWork()

    new_chats = await chat_service.get_chats(uow, uid, created_after=timestamp)
    deleted_chats = await chat_service.get_chats(uow, uid, deleted_after=timestamp)

    new_messages = await message_service.get_messages(uow, user=uid, created_after=timestamp)
    deleted_messages = await message_service.get_messages(uow, user=uid, deleted_after=timestamp)

    await socket_manager.emit_to_user(uid, 'updates', {
        'new_chats': new_chats,
        'deleted_chats': deleted_chats,
        'new_messages': new_messages,
        'deleted_messages': deleted_messages
    })


socket_manager.subscribe('new_chat', on_new_chat)
socket_manager.subscribe('update_chat', on_update_chat)
socket_manager.subscribe('delete_chat', on_delete_chat)
socket_manager.subscribe('new_message', on_new_message)
socket_manager.subscribe('request_updates', on_request_updates)
socket_manager.subscribe('delete_message', on_delete_message)
