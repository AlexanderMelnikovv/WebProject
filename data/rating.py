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
    easy_level_wins = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    easy_level_losses = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    middle_level_wins = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    middle_level_losses = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    hard_level_wins = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    hard_level_losses = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    wins = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    losses = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    points = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)