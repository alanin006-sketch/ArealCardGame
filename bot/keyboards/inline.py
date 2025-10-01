from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def battle_board_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Выбрать карту", callback_data="choose_card")]
    ])

def select_card_kb(board: list):
    keyboard = []
    for i, card in enumerate(board):
        if card.get("status") != "destroyed":
            keyboard.append([InlineKeyboardButton(
                text=f"{card['name']} (HP: {card['health']})",
                callback_data=f"select_card_{i}"
            )])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def select_target_kb(target_board: list, attacker_idx: int):
    keyboard = []
    for i, card in enumerate(target_board):
        if card.get("status") != "destroyed":
            keyboard.append([InlineKeyboardButton(
                text=f"{card['name']} (HP: {card['health']})",
                callback_data=f"attack_{attacker_idx}_{i}"
            )])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
