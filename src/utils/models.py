from abc import ABCMeta, abstractmethod
from src.utils.database import Base


class DeclarativeABCMeta(ABCMeta, type(Base)):
    pass


class IModel(Base, metaclass=DeclarativeABCMeta):
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
