import datetime

import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Question(SqlAlchemyBase):
    __tablename__ = "questions"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    question = sqlalchemy.Column(sqlalchemy.VARCHAR)
    answers = sqlalchemy.Column(sqlalchemy.VARCHAR)
    correct_answer = sqlalchemy.Column(
        sqlalchemy.VARCHAR, sqlalchemy.ForeignKey("words.id")
    )

    cor_ans = orm.relation("Word")
