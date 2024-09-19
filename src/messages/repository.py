from sqlalchemy import select

from src.messages.models import Message
from src.utils.repository import TimeStampRepository


class MessageRepository(TimeStampRepository):
    model = Message

    async def get_context(self, session, chat_id, created_before, count):
        stmt = select(self.model).filter_by(chat_uuid=chat_id, deleted_at=None).where(
            self.model.created_at < created_before).order_by(self.model.created_at.desc()).limit(count)

        res = await session.execute(stmt)
        return [row[0].dict() for row in res.all()]
