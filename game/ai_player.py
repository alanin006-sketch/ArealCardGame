# game/ai_player.py
import random
from typing import List, Dict, Optional

class SimpleAI:
    def __init__(self, difficulty: str = "normal"):
        self.difficulty = difficulty

    def choose_card(self, hand: List[Dict], opponent_board: List[Dict]) -> Optional[int]:
        if not hand:
            return None

        if self.difficulty == "easy":
            # Играет самую слабую
            idx = min(range(len(hand)), key=lambda i: hand[i].get("power", 0))
        elif self.difficulty == "hard":
            # Играет самую сильную
            idx = max(range(len(hand)), key=lambda i: hand[i].get("power", 0))
        else:
            # normal — случайная
            idx = random.randint(0, len(hand) - 1)
        return idx
