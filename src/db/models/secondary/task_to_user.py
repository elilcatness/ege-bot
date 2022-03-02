from sqlalchemy import Table, Column, Integer, ForeignKey

from src.db.db_session import SqlAlchemyBase

task_to_user = Table('task_to_user', SqlAlchemyBase.metadata,
                     Column('task', Integer, ForeignKey('tasks.id')),
                     Column('user', Integer, ForeignKey('users.id')))