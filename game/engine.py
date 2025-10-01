class BattleEngine:
    @staticmethod
    def attack_card(attacker: dict, target: dict):
        target["health"] -= attacker["attack"]
        if target["health"] <= 0:
            target["status"] = "destroyed"
        return target

    @staticmethod
    def check_win_condition(board: list):
        return all(card.get("health", 0) <= 0 for card in board)

    @staticmethod
    def format_board(board: list):
        """Форматирует доску для вывода игроку"""
        if not board:
            return "Поле пусто."
        result = "Карты на поле:\n"
        for i, card in enumerate(board):
            status = " [УНИЧТОЖЕНА]" if card.get("status") == "destroyed" else ""
            result += f"{i}. {card['name']} (HP: {card['health']}, ATK: {card['attack']}){status}\n"
        return result
