from sqlalchemy import Column, Integer, String

from src.db.db_session import SqlAlchemyBase


class Number(SqlAlchemyBase):
    __tablename__ = 'numbers'

    id = Column(Integer, primary_key=True, unique=True)
    title = Column(String, nullable=True)