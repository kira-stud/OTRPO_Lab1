from sqlalchemy import types, Column, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from settings import *

connection_string = f"postgresql://{POSTGRESQL_USER}:{POSTGRESQL_PSW}@{POSTGRESQL_HOST}:{POSTGRESQL_PORT}/{POSTGRESQL_DB}"
engine = create_engine(connection_string, echo=False)
Session = sessionmaker(bind=engine)
sess = Session()

Base = declarative_base()


class Fight(Base):
    __tablename__ = 'fights'
    __fields__ = ['id', 'player_poki', 'bot_poki', 'player_result', 'bot_result']

    id = Column(types.Integer, autoincrement=True, primary_key=True)
    date_time = Column(types.DateTime, server_default=func.now(), nullable=False)
    player_id = Column(types.Integer, nullable=False)
    bot_id = Column(types.Integer, nullable=False)
    winner_id = Column(types.Integer, nullable=False)
    rounds_count = Column(types.Integer, nullable=False)

    def __init__(self, player_id, bot_id, winner_id, rounds_count):
        self.player_id = player_id
        self.bot_id = bot_id
        self.winner_id = winner_id
        self.rounds_count = rounds_count

    def __repr__(self):
        return '<Fight: id=%s, player_id=%s, bot_id=%s, winner_id=%s, rounds_count=%s>'\
               % (self.id, self.player_id, self.bot_id, self.winner_id, self.rounds_count)


# Base.metadata.create_all(engine)
