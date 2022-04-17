import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Word(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'words'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    word = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
    word_ru = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
