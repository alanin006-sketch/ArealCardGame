from aiogram import Router, types
from aiogram.filters import Command
from database.models import User
from database.db import async_session
from bot.keyboards.inline import main_menu_kb

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    async with async_session() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            new_user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username
            )
            session.add(new_user)
            await session.commit()
            await message.answer("Добро пожаловать в Зону, сталкер. Ты зарегистрирован.")
        else:
            await message.answer("С возвращением в Зону.")

    await message.answer("Выбери действие:", reply_markup=main_menu_kb())
