from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.chats.models import Chat
from src.utils.repository import TimeStampRepository


class ChatRepository(TimeStampRepository):
    model = Chat

    async def get_all_updated_after(self, session: AsyncSession, timestamp: datetime, **filter_by):
        stmt = select(self.model).filter_by(**filter_by).where(
            self.model.updated_at > timestamp and self.model.created_at <= timestamp)

        res = await session.execute(stmt)
        return [row[0].dict() for row in res.all()]
