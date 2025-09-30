from aiogram import Router, types
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from database.models import User, Match
from database.db import async_session
from game.matchmaker import Matchmaker
from bot.keyboards.inline import confirm_play_kb, pass_or_play_kb

router = Router()
matchmaker = Matchmaker()

@router.callback_query(lambda c: c.data == "find_match")
async def find_match(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    match_id = await matchmaker.add_player(user_id)
    if match_id:
        # Матч найден
        async with async_session() as session:
            match = await session.get(Match, match_id)
            await callback.message.edit_text(
                f"Матч найден! Раунд 1.\n"
                f"Ваш ход. Сила: 0\n"
                f"Выберите действие:",
                reply_markup=pass_or_play_kb()
            )
            # Здесь позже будет логика раздачи карт и ходов
    else:
        await callback.message.edit_text(
            "Ищем соперника... Нажмите, когда будете готовы:",
            reply_markup=confirm_play_kb()
        )

@router.callback_query(lambda c: c.data == "confirm_play")
async def confirm_play(callback: CallbackQuery):
    await callback.answer()
    await find_match(callback, FSMContext())  # рекурсивно пытаемся найти

@router.callback_query(lambda c: c.data in ["pass_round", "end_turn"])
async def handle_turn_action(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text("Ход завершён. Ожидание соперника...")
    # В реальной версии здесь будет логика передачи хода
