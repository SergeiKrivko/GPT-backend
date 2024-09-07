import uuid
from typing import Literal
from uuid import UUID, uuid4

from src.replys.repository import ReplyRepository
from src.replys.schemas import ReplyRead
from src.utils.unitofwork import IUnitOfWork


class ReplyService:
    def __init__(self, reply_repository: ReplyRepository):
        self.reply_repository = reply_repository

    async def get_reply(self, uow: IUnitOfWork, reply_uuid: UUID):
        async with uow:
            reply_dict = await self.reply_repository.get(uow.session, uuid=reply_uuid)
            if not reply_dict:
                return None
            return self.reply_dict_to_read_model(reply_dict)

    async def get_replys(self, uow: IUnitOfWork, to_uuid: uuid.UUID) -> list[ReplyRead]:
        async with uow:
            replys_list = await self.reply_repository.get_all(uow.session, to_uuid=to_uuid)
            res = []
            for reply in replys_list:
                res.append(self.reply_dict_to_read_model(reply))
            return res

    async def add_reply(self, uow: IUnitOfWork, from_uuid: UUID, to_uuid: UUID,
                        type: Literal['prompt', 'context', 'explicit', 'implicit']):
        async with uow:
            reply_dict = {
                'uuid': uuid4(),
                'from_uuid': from_uuid,
                'to_uuid': to_uuid,
                'type': type,
            }

            await self.reply_repository.add(uow.session, reply_dict)
            await uow.commit()
            return reply_dict['uuid']

    @staticmethod
    def reply_dict_to_read_model(reply_dict: dict) -> ReplyRead:
        return ReplyRead(
            uuid=reply_dict['uuid'],
            from_uuid=reply_dict['from_uuid'],
            to_uuid=reply_dict['to_uuid'],
            type=reply_dict['type'],
        )
