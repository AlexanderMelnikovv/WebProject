from .db_session import SqlAlchemyBase
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin


class Games(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'games'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')
    user_moves = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    opponent_moves = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    result = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)