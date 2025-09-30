from aiogram import Router, types
from aiogram.filters import Command
from database.models import User
from database.db import async_session
from bot.keyboards.inline import main_menu_kb

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username

    async with async_session() as session:
        # Проверяем, существует ли пользователь
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        existing_user = result.scalar_one_or_none()

        if not existing_user:
            # Создаём нового
            new_user = User(
                telegram_id=user_id,
                username=username,
                rating=1000
            )
            session.add(new_user)
            await session.commit()
            await message.answer("Добро пожаловать в Зону, сталкер. Ты зарегистрирован.")
        else:
            await message.answer("С возвращением в Зону.")

    await message.answer("Выбери действие:", reply_markup=main_menu_kb())
