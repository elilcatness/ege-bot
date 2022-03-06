from sqlalchemy import Column, Integer, Boolean
from sqlalchemy.orm import relationship

from src.db.db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, unique=True)
    completed_tasks = relationship('Task', secondary='task_to_user', back_populates='users')
    show_completed = Column(Boolean, default=False)
    attempts = relationship('Attempt')

    def __str__(self):
        return f'Пользователь: {self.id}. Выполненных заданий: {len(self.completed_tasks)}'