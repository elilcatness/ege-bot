from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from src.db.db_session import SqlAlchemyBase


class Attempt(SqlAlchemyBase):
    __tablename__ = 'attempts'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    answer = Column(String)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    task = relationship('Task', foreign_keys=task_id)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', foreign_keys=user_id)
    correct = Column(Boolean)