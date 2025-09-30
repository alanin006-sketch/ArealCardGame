# Заглушка игрового движка
class GameEngine:
    @staticmethod
    def calculate_round_score(board: list) -> int:
        # В реальной версии: сумма силы + эффекты
        return sum(card.get("power", 0) for card in board)

    @staticmethod
    def resolve_round(match: "Match") -> dict:
        score1 = GameEngine.calculate_round_score(match.board_p1)
        score2 = GameEngine.calculate_round_score(match.board_p2)
        if score1 > score2:
            match.scores["p1"] += 1
        elif score2 > score1:
            match.scores["p2"] += 1
        # Если ничья — никто не получает очко (как в Gwent)
        return match.scores
