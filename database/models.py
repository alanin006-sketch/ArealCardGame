from sqlalchemy import Column, Integer, String, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String, nullable=True)
    rating = Column(Integer, default=1000)
    current_deck_id = Column(Integer, nullable=True)

class Deck(Base):
    __tablename__ = "decks"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, default="Основная")
    faction = Column(String)  # e.g., "monolith"
    card_ids = Column(JSON)   # list of card IDs (stub for now)

class Match(Base):
    __tablename__ = "matches"
    is_ai_match = Column(Boolean, default=False)
    id = Column(Integer, primary_key=True)
    player1_id = Column(Integer, ForeignKey("users.id"))
    player2_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String, default="waiting")  # waiting, active, finished
    round = Column(Integer, default=1)  # 1, 2, 3
    scores = Column(JSON, default={"p1": 0, "p2": 0})  # rounds won
    current_player_id = Column(Integer, nullable=True)
    board_p1 = Column(JSON, default=[])
    board_p2 = Column(JSON, default=[])
    hand_p1 = Column(JSON, default=[])
    hand_p2 = Column(JSON, default=[])
