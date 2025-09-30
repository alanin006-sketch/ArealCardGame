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

def pass_or_play_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➡️ Пас", callback_data="pass_round")],
        [InlineKeyboardButton(text="🔄 Закончить ход", callback_data="end_turn")]
    ])
