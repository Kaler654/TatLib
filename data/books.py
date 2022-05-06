import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Book(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "books"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    author = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    user_author_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=False
    )
    pages = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    title = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
    level_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

    user = orm.relation("User")

    def __str__(self):
        return "id {}, au {}, us_id {}, pg {}, ti {}, lv {}".format(
            self.id,
            self.author,
            self.user_author_id,
            self.pages,
            self.title,
            self.level_id,
        )
