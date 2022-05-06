import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Word(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "words"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    word = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
    word_ru = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
