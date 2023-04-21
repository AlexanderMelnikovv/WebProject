from .db_session import SqlAlchemyBase
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin


class Rating(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'rating'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')
    wins = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    losses = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    points = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)