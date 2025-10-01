# bot/keyboards/inline.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Найти игру", callback_data="find_match")],
        [InlineKeyboardButton(text="🃏 Мои колоды", callback_data="decks")],
        [InlineKeyboardButton(text="📊 Рейтинг", callback_data="rating")]
    ])

def confirm_play_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Готов играть", callback_data="confirm_play")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
    ])

def battle_board_kb(has_cards_on_board: bool = False):
    if has_cards_on_board:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Атаковать", callback_data="choose_attack")]
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Выложить карту", callback_data="choose_card")]
        ])

def select_card_kb(board: list):
    keyboard = []
    for i, card in enumerate(board):
        if card.get("status") != "destroyed":
            keyboard.append([InlineKeyboardButton(
                text=f"{card['name']} (HP: {card['health']})",
                callback_data=f"select_card_for_attack_{i}"
            )])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def select_target_kb(target_board: list, field_cards: list, attacker_idx: int):
    keyboard = []
    # Цели: карты противника
    for i, card in enumerate(target_board):
        if card.get("status") != "destroyed":
            keyboard.append([InlineKeyboardButton(
                text=f"🎯 {card['name']} (HP: {card['health']})",
                callback_data=f"attack_{attacker_idx}_enemy_{i}"
            )])
    # Цели: свои карты (опционально)
    for i, card in enumerate(target_board):
        if card.get("status") != "destroyed":
            keyboard.append([InlineKeyboardButton(
                text=f"🛡️ {card['name']} (HP: {card['health']})",
                callback_data=f"attack_{attacker_idx}_ally_{i}"
            )])
    # Цели: карты с поля
    for i, card in enumerate(field_cards):
        if card.get("status") != "destroyed":
            keyboard.append([InlineKeyboardButton(
                text=f"🌟 {card['name']} (HP: {card['health']})",
                callback_data=f"attack_{attacker_idx}_field_{i}"
            )])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
