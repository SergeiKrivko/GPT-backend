from abc import ABC, abstractmethod, ABCMeta
from datetime import datetime
from uuid import UUID

from sqlalchemy import insert, select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractRepository(ABC):
    @abstractmethod
    async def get(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def get_all(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def add(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def edit(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def delete(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def delete_all(self, *args, **kwargs):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository, metaclass=ABCMeta):
    @property
    @abstractmethod
    def model(self):
        """Model class for SQLAlchemy."""

    async def get(self, session: AsyncSession, filter_dict: dict = None, **filter_by):
        stmt = select(self.model).filter_by(**filter_by).limit(1)
        res = await session.execute(stmt)
        res = res.all()
        if res and res[0]:
            return res[0][0].dict()
        return None

    async def get_all(self, session: AsyncSession, **filter_by):
        stmt = select(self.model).filter_by(**filter_by)

        res = await session.execute(stmt)
        return [row[0].dict() for row in res.all()]

    async def add(self, session: AsyncSession, data: dict) -> int:
        stmt = insert(self.model).values(**data).returning(self.model.uuid)
        res = await session.execute(stmt)
        return res.scalar_one()

    async def edit(self, session: AsyncSession, uuid: UUID, data: dict) -> int:
        stmt = update(self.model).values(**data).filter_by(uuid=uuid).returning(self.model.uuid)
        res = await session.execute(stmt)
        return res.scalar_one()

    async def delete(self, session: AsyncSession, uuid: UUID):
        stmt = delete(self.model).where(self.model.uuid == uuid).returning(self.model.uuid)
        res = await session.execute(stmt)
        return res

    async def delete_all(self, session: AsyncSession, filter_dict: dict = None, **filter_by):
        stmt = delete(self.model).filter_by(**filter_by)
        res = await session.execute(stmt)
        return res


class TimeStampRepository(SQLAlchemyRepository):
    @property
    @abstractmethod
    def model(self):
        """Model class for SQLAlchemy."""

    async def get_all_created_after(self, session: AsyncSession, timestamp: datetime, **filter_by):
        stmt = select(self.model).filter_by(**filter_by).where(self.model.created_at > timestamp)

        res = await session.execute(stmt)
        return [row[0].dict() for row in res.all()]

    async def get_all_deleted_after(self, session: AsyncSession, timestamp: datetime, **filter_by):
        stmt = select(self.model).filter_by(**filter_by).where(self.model.deleted_at > timestamp)

        res = await session.execute(stmt)
        return [row[0].dict() for row in res.all()]
