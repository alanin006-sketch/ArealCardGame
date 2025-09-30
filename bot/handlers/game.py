# bot/handlers/game.py
from aiogram import Router, types
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from database.models import User, Match
from database.db import async_session
from game.matchmaker import Matchmaker
from game.ai_player import SimpleAI
from bot.keyboards.inline import confirm_play_kb, pass_or_play_kb
from main import bot

router = Router()
matchmaker = Matchmaker()

# Заглушка: простая "колода" для MVP
DUMMY_DECK = [
    {"id": 1, "name": "Сталкер-одиночка", "power": 4},
    {"id": 2, "name": "Артефакт 'Пустышка'", "power": 0},
    {"id": 3, "name": "Военный патруль", "power": 6},
    {"id": 4, "name": "Компас Зоны", "power": 2},
    {"id": 5, "name": "Скала", "power": 8},
]

@router.callback_query(lambda c: c.data == "find_match")
async def find_match(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id

    # Проверим, нет ли уже активного матча
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

    match_id = await matchmaker.add_player(user_id)
    if match_id:
        # Матч с живым игроком — пока не реализован полностью, пропустим
        await callback.message.edit_text("Матч найден! (PvP — в разработке)")
    else:
        await callback.message.edit_text(
            "Ищем соперника...\n"
            "Если не найдём — в бой вступит БОТ-сталкер через 10 секунд.",
            reply_markup=confirm_play_kb()
        )

@router.callback_query(lambda c: c.data == "confirm_play")
async def confirm_play(callback: CallbackQuery):
    await callback.answer()
    # Просто повторно вызываем поиск — Matchmaker сам решит, дать бота или нет
    await find_match(callback, FSMContext())

# =============== ОБРАБОТКА ИГРЫ ПРОТИВ БОТА ===============

@router.message(lambda message: message.text and message.text.startswith("/play_"))
async def handle_card_play(message: Message):
    """
    Игрок отправляет команду вида: /play_0, /play_1 и т.д.
    Это временный способ выбора карты (пока нет Mini App или кнопок под каждую карту).
    """
    user_id = message.from_user.id
    try:
        card_index = int(message.text.split("_")[1])
    except (IndexError, ValueError):
        await message.answer("Неверная команда. Используйте /play_0, /play_1 и т.д.")
        return

    async with async_session() as session:
        # Найти активный матч против бота
        result = await session.execute(
            select(Match).where(
                Match.player1_id == user_id,
                Match.is_ai_match == True,
                Match.status == "active"
            )
        )
        match = result.scalar_one_or_none()
        if not match:
            await message.answer("У вас нет активного матча с ботом.")
            return

        # Проверим, есть ли такая карта в руке
        if card_index < 0 or card_index >= len(match.hand_p1):
            await message.answer("Нет карты с таким номером.")
            return

        # Игрок играет карту
        played_card = match.hand_p1.pop(card_index)
        match.board_p1.append(played_card)

        # Ход бота
        ai = SimpleAI(difficulty="normal")
        ai_card_idx = ai.choose_card(hand=match.hand_p2, opponent_board=match.board_p1)
        if ai_card_idx is not None and ai_card_idx < len(match.hand_p2):
            ai_card = match.hand_p2.pop(ai_card_idx)
            match.board_p2.append(ai_card)
            ai_card_name = ai_card["name"]
        else:
            ai_card_name = "ничего (рука пуста)"

        # Подсчёт силы
        player_power = sum(c.get("power", 0) for c in match.board_p1)
        ai_power = sum(c.get("power", 0) for c in match.board_p2)

        # Завершаем матч (в MVP — 1 раунд = 1 игра)
        match.status = "finished"
        result_text = "Победа!" if player_power > ai_power else "Поражение." if ai_power > player_power else "Ничья."

        await session.commit()

        await message.answer(
            f"Вы разыграли: {played_card['name']} ({played_card['power']} силы)\n"
            f"БОТ разыграл: {ai_card_name}\n\n"
            f"Ваша сила: {player_power}\n"
            f"Сила БОТА: {ai_power}\n\n"
            f"Результат: {result_text}"
        )

@router.callback_query(lambda c: c.data == "start_ai_match")
async def start_ai_match_direct(callback: CallbackQuery):
    """Опционально: прямой запуск тренировки (можно добавить в меню)"""
    await callback.answer()
    user_id = callback.from_user.id

    # Создаём матч против бота мгновенно
    async with async_session() as session:
        new_match = Match(
            player1_id=user_id,
            player2_id=-1,
            status="active",
            is_ai_match=True,
            hand_p1=DUMMY_DECK.copy(),
            hand_p2=DUMMY_DECK.copy(),  # Бот играет той же "колодой"
            board_p1=[],
            board_p2=[],
            scores={"p1": 0, "p2": 0}
        )
        session.add(new_match)
        await session.commit()

    cards_text = "\n".join(f"{i}. {card['name']} ({card['power']})" for i, card in enumerate(DUMMY_DECK))
    await callback.message.edit_text(
        "⚔️ Тренировка с БОТом начата!\n"
        "Выберите карту, отправив команду:\n"
        "/play_0, /play_1, /play_2 и т.д.\n\n"
        f"Ваша рука:\n{cards_text}"
    )
