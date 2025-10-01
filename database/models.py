from sqlalchemy import Column, Integer, String, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Card(Base):
    __tablename__ = "cards"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    faction = Column(String, nullable=True)  # "monolith", "stalker", "military"
    card_type = Column(String, default="unit")  # unit, spell, anomaly
    attack = Column(Integer, default=0)
    health = Column(Integer, default=10)
    description = Column(String, default="")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String, nullable=True)
    rating = Column(Integer, default=1000)
    current_deck_id = Column(Integer, nullable=True)
    field_cards = Column(JSON, default=[])  # ← добавим поле для "случайных" карт на поле

class Deck(Base):
    __tablename__ = "decks"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, default="Основная")
    faction = Column(String)  # e.g., "monolith"
    card_ids = Column(JSON)   # list of card IDs

class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True)
    player1_id = Column(Integer, ForeignKey("users.id"))
    player2_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String, default="active")  # active, finished
    is_ai_match = Column(Boolean, default=False)

    # Карты на поле (с HP)
    board_p1 = Column(JSON, default=[])  # [{"id": 1, "name": "...", "health": 8, "attack": 5}, ...]
    board_p2 = Column(JSON, default=[])
    hand_p1 = Column(JSON, default=[])
    hand_p2 = Column(JSON, default=[])

    # Состояние раунда
    current_round = Column(Integer, default=1)
    current_player_id = Column(Integer)  # кто ходит
    moves_left_p1 = Column(Integer, default=3)
    moves_left_p2 = Column(Integer, default=3)
    turn_phase = Column(String, default="action")  # "action", "round_end", "game_end"
