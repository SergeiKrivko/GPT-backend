from src.utils.repository import SQLAlchemyRepository
from src.replys.models import Reply


class ReplyRepository(SQLAlchemyRepository):
    model = Reply
