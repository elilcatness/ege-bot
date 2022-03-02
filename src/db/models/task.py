from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.db.db_session import SqlAlchemyBase


class Task(SqlAlchemyBase):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, unique=True)
    number = Column(Integer)
    description = Column(String)
    users = relationship('User', secondary='task_to_user')

    def __str__(self):
        return f'Задание типа {self.number} №{self.id}'