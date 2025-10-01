import random

class SimpleAI:
    def __init__(self, difficulty="normal"):
        self.difficulty = difficulty

    def choose_target(self, board: list):
        alive = [i for i, c in enumerate(board) if c.get("health", 0) > 0 and c.get("status") != "destroyed"]
        return random.choice(alive) if alive else None

    def take_turn(self, match):
        # AI делает 3 хода
        for _ in range(3):
            attacker_board = match.board_p2
            target_board = match.board_p1

            attacker_idx = random.choice(range(len(attacker_board)))
            target_idx = self.choose_target(target_board)
            if target_idx is None:
                continue

            # Атака
            from game.engine import BattleEngine
            BattleEngine.attack_card(attacker_board[attacker_idx], target_board[target_idx])
            match.moves_left_p2 -= 1
