from sqlalchemy import types, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

connection_string = "postgresql://postgres:Passw0rd@localhost:5432/Pokemon"
engine = create_engine(connection_string, echo=True)
Session = sessionmaker(bind=engine)
sess = Session()

Base = declarative_base()


class Fight(Base):
    __tablename__ = 'fights'
    __fields__ = ['id', 'player_poki', 'bot_poki', 'player_result', 'bot_result']

    id = Column(types.Integer, autoincrement=True, primary_key=True)
    player_poki = Column(types.String(100), nullable=False)
    bot_poki = Column(types.String(100), nullable=False)
    player_result = Column(types.Integer, nullable=False)
    bot_result = Column(types.Integer, nullable=False)

    def __init__(self, player_poki, bot_poki, player_result, bot_result):
        self.player_poki = player_poki
        self.bot_poki = bot_poki
        self.player_result = player_result
        self.bot_result = bot_result

    def __repr__(self):
        return '<Fight: id=%s, player_poki=%s, bot_poki=%s, player_result=%s, bot_result=%s>'\
               % (self.id, self.player_poki, self.bot_poki, self.player_result, self.bot_result)


Base.metadata.create_all(engine)
