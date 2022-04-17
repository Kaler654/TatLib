import sqlalchemy
import datetime
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False, unique=True)
    email = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False, unique=True)
    telegram_id = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False, unique=False)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    status = sqlalchemy.Column(sqlalchemy.VARCHAR, default='user')
    level_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("levels.level_id"))
    words = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)

    level = orm.relation("Level")

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)