from sqlalchemy import types, Column, func, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from settings import *

connection_string = f"postgresql://{POSTGRESQL_USER}:{POSTGRESQL_PSW}@{POSTGRESQL_HOST}:{POSTGRESQL_PORT}/{POSTGRESQL_DB}"
engine = create_engine(connection_string, echo=False)
Session = sessionmaker(bind=engine)
sess = Session()

Base = declarative_base()


class Fight(Base):
    __tablename__ = 'fights'
    __fields__ = ['id', 'user_id', 'player_poki', 'bot_poki', 'player_result', 'bot_result']

    id = Column(types.Integer, autoincrement=True, primary_key=True)
    user_id = Column(types.Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    date_time = Column(types.DateTime, server_default=func.now(), nullable=False)
    player_id = Column(types.Integer, nullable=False)
    bot_id = Column(types.Integer, nullable=False)
    winner_id = Column(types.Integer, nullable=False)
    rounds_count = Column(types.Integer, nullable=False)
    user = relationship('User', back_populates='fights')

    def __init__(self, user_id, player_id, bot_id, winner_id, rounds_count):
        self.user_id = user_id
        self.player_id = player_id
        self.bot_id = bot_id
        self.winner_id = winner_id
        self.rounds_count = rounds_count

    def __repr__(self):
        return '<Fight: id=%s, user_id=%s, player_id=%s, bot_id=%s, winner_id=%s, rounds_count=%s>'\
               % (self.id, self.user_id, self.player_id, self.bot_id, self.winner_id, self.rounds_count)


class User(Base):
    __tablename__ = 'users'
    __fields__ = ['id', 'email', 'password']

    id = Column(types.Integer, autoincrement=True, primary_key=True)
    email = Column(types.String, nullable=False)
    password = Column(types.String, nullable=False)
    fights = relationship('Fight', back_populates='user', passive_deletes=True)

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User: id=%s, email=%s, password=%s>' % (self.id, self.email, self.password)


Base.metadata.create_all(engine)
