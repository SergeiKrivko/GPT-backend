from abc import abstractmethod

from sqlalchemy.orm import DeclarativeMeta

from src.utils.database import Base


class IModel(Base, metaclass=DeclarativeMeta):
    __abstract__ = True

    @property
    @abstractmethod
    def __tablename__(self):
        """Table Name should be provided due to SQLAlchemy conventions."""

    @abstractmethod
    def dict(self):
        """
        Converts the model to a dictionary.
        """
        pass
