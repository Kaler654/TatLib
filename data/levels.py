import sqlalchemy
from .db_session import SqlAlchemyBase


class Level(SqlAlchemyBase):
    __tablename__ = 'levels'
    level_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
