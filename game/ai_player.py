# game/ai_player.py
import random
from typing import List, Dict

class SimpleAI:
    """Простой AI: играет случайные карты, иногда пасует"""

    def __init__(self, difficulty: str = "normal"):
        self.difficulty = difficulty  # "easy", "normal", "hard"

    def choose_card(self, hand: List[Dict], opponent_board: List[Dict]) -> int | None:
        if not hand:
            return None

        if self.difficulty == "easy":
            # Всегда играет самую слабую карту
            weakest = min(hand, key=lambda c: c.get("power", 0))
            return hand.index(weakest)
        elif self.difficulty == "hard":
            # Играет сильнейшую, если отстаёт — иначе слабую
            total_opp = sum(c.get("power", 0) for c in opponent_board)
            total_self = 0  # AI пока не знает свою доску — упрощаем
            if total_opp > 10:
                strongest = max(hand, key=lambda c: c.get("power", 0))
                return hand.index(strongest)
        # normal: случайная карта
        return random.randint(0, len(hand) - 1)

    def should_pass(self, my_score: int, opp_score: int) -> bool:
        if self.difficulty == "easy":
            return my_score > opp_score + 3
        elif self.difficulty == "hard":
            return my_score > opp_score or len(self.hand) <= 1
        else:
            return my_score > opp_score + random.randint(0, 5)
