from aiogram import Router, types
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from database.models import User, Match, Card
from database.db import async_session
from game.engine import BattleEngine
from game.ai_player import SimpleAI
from bot.keyboards.inline import (
    battle_board_kb,
    select_card_kb,
    select_target_kb
)
from main import bot

router = Router()
    
# Пример заглушка колоды
DUMMY_DECK = [
    {"id": 1, "name": "Сталкер-одиночка", "attack": 4, "health": 10},
    {"id": 2, "name": "Артефакт 'Пустышка'", "attack": 0, "health": 5},
    {"id": 3, "name": "Военный патруль", "attack": 6, "health": 12},
    {"id": 4, "name": "Компас Зоны", "attack": 2, "health": 8},
    {"id": 5, "name": "Скала", "attack": 8, "health": 20},
]

# Глобальная переменная для matchmaker
matchmaker = None

def set_matchmaker(m):
    global matchmaker
    matchmaker = m

@router.callback_query(lambda c: c.data == "find_match")
async def find_match(callback: CallbackQuery):
    user_id = callback.from_user.id
    async with async_session() as session:
        active_match = await session.execute(
            select(Match).where(
                ((Match.player1_id == user_id) | (Match.player2_id == user_id)),
                Match.status == "active"
            )
        )
        if active_match.scalar_one_or_none():
            await callback.message.edit_text("У вас уже есть активный матч!")
            return

    # Создаём матч против AI
    new_match = Match(
        player1_id=user_id,
        player2_id=-1,
        status="active",
        is_ai_match=True,
        hand_p1=DUMMY_DECK.copy(),
        hand_p2=DUMMY_DECK.copy(),
        board_p1=[],
        board_p2=[],
        current_player_id=user_id,
        moves_left_p1=3,
        moves_left_p2=3,
    )
    session.add(new_match)
    await session.commit()

    await callback.message.edit_text(
        "Бой начинается!\n"
        f"Ваши карты:\n{BattleEngine.format_board(new_match.hand_p1)}\n"
        f"Карты противника:\n{BattleEngine.format_board(new_match.hand_p2)}",
        reply_markup=battle_board_kb()
    )

@router.callback_query(lambda c: c.data.startswith("select_card_"))
async def select_card(callback: CallbackQuery):
    user_id = callback.from_user.id
    card_idx = int(callback.data.split("_")[2])

    async with async_session() as session:
        result = await session.execute(
            select(Match).where(
                ((Match.player1_id == user_id) | (Match.player2_id == user_id)),
                Match.status == "active"
            )
        )
        match = result.scalar_one_or_none()
        if not match:
            await callback.answer("Нет активного матча.")
            return

        if match.current_player_id != user_id:
            await callback.answer("Не ваш ход.")
            return

        moves_left = match.moves_left_p1 if user_id == match.player1_id else match.moves_left_p2
        if moves_left <= 0:
            await callback.answer("У вас закончились ходы в этом раунде.")
            return

        # Выбираем карту
        board = match.board_p1 if user_id == match.player1_id else match.board_p2
        if card_idx >= len(board):
            await callback.answer("Неверный индекс карты.")
            return

        # Предлагаем выбрать цель
        target_board = match.board_p2 if user_id == match.player1_id else match.board_p1
        await callback.message.edit_text(
            f"Вы выбрали: {board[card_idx]['name']}\nВыберите цель для атаки:",
            reply_markup=select_target_kb(target_board, card_idx)
        )

@router.callback_query(lambda c: c.data.startswith("attack_"))
async def handle_attack(callback: CallbackQuery):
    user_id = callback.from_user.id
    attacker_idx = int(callback.data.split("_")[1])
    target_idx = int(callback.data.split("_")[2])

    async with async_session() as session:
        result = await session.execute(
            select(Match).where(
                ((Match.player1_id == user_id) | (Match.player2_id == user_id)),
                Match.status == "active"
            )
        )
        match = result.scalar_one_or_none()
        if not match:
            await callback.answer("Нет активного матча.")
            return

        if match.current_player_id != user_id:
            await callback.answer("Не ваш ход.")
            return

        # Определяем доски
        attacker_board = match.board_p1 if user_id == match.player1_id else match.board_p2
        target_board = match.board_p2 if user_id == match.player1_id else match.board_p1

        if attacker_idx >= len(attacker_board) or target_idx >= len(target_board):
            await callback.answer("Неверный индекс.")
            return

        # Атака
        attacker_card = attacker_board[attacker_idx]
        target_card = target_board[target_idx]

        BattleEngine.attack_card(attacker_card, target_card)

        # Обновляем ходы
        if user_id == match.player1_id:
            match.moves_left_p1 -= 1
        else:
            match.moves_left_p2 -= 1

        await session.commit()

        if target_card.get("status") == "destroyed":
            await callback.message.edit_text(f"Карта {target_card['name']} уничтожена!")
        else:
            await callback.message.edit_text(
                f"{attacker_card['name']} атаковал {target_card['name']}!\n"
                f"Здоровье цели: {target_card['health']}"
            )

        # Проверяем конец раунда
        if match.moves_left_p1 == 0 and match.moves_left_p2 == 0:
            if BattleEngine.check_win_condition(match.board_p2):
                await callback.message.edit_text("Вы победили!")
                match.status = "finished"
            elif BattleEngine.check_win_condition(match.board_p1):
                await callback.message.edit_text("Вы проиграли.")
                match.status = "finished"
            else:
                # Следующий раунд
                match.current_round += 1
                match.moves_left_p1 = 3
                match.moves_left_p2 = 3
                await callback.message.edit_text(
                    f"Раунд {match.current_round} начинается!",
                    reply_markup=battle_board_kb()
                )
