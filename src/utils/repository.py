from abc import ABC, abstractmethod, ABCMeta
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

    async def get(self, session, filter_dict: dict = None, **filter_by):
        stmt = select(self.model).filter_by(**filter_by).limit(1)
        res = await session.execute(stmt)
        res = res.all()
        if res and res[0]:
            return res[0][0].dict()
        return None

    async def get_all(self, session, filter_dict: dict = None, **filter_by):
        stmt = select(self.model).filter_by(**filter_by)

        if filter_dict:
            for key, val in filter_dict.items():
                if key in self.model.__dict__:
                    if val[0] == 'between':
                        stmt = stmt.filter(and_(self.model.__dict__[key] >= val[1],
                                                self.model.__dict__[key] <= val[2]))

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

    async def delete(self, session, uuid: UUID):
        stmt = delete(self.model).where(self.model.uuid == uuid).returning(self.model.uuid)
        res = await session.execute(stmt)
        return res

    async def delete_all(self, session, filter_dict: dict = None, **filter_by):
        stmt = delete(self.model).filter_by(**filter_by)
        res = await session.execute(stmt)
        return res
