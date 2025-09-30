# game/matchmaker.py
import asyncio
from database.models import Match
from database.db import async_session

class Matchmaker:
    def __init__(self):
        self.waiting_players = set()
        self.wait_tasks = {}  # user_id → task

    async def _create_ai_match(self, user_id: int):
        """Создаёт матч против AI"""
        async with async_session() as session:
            new_match = Match(
                player1_id=user_id,
                player2_id=-1,  # Специальный ID для AI
                status="active",
                is_ai_match=True  # добавим поле в БД
            )
            session.add(new_match)
            await session.commit()
            match_id = new_match.id

        # Уведомляем игрока
        from main import bot
        try:
            await bot.send_message(
                user_id,
                "Соперник не найден. В бой вступает БОТ-сталкер! 🤖\n"
                "Раунд 1 начинается.",
                reply_markup=pass_or_play_kb()
            )
        except Exception as e:
            print(f"Не удалось отправить сообщение: {e}")

    async def add_player(self, user_id: int):
        self.waiting_players.add(user_id)

        # Отменяем старую задачу, если была
        if user_id in self.wait_tasks:
            self.wait_tasks[user_id].cancel()

        # Если есть хотя бы 2 игрока — матч!
        if len(self.waiting_players) >= 2:
            p1 = self.waiting_players.pop()
            p2 = self.waiting_players.pop()
            if p1 in self.wait_tasks:
                self.wait_tasks[p1].cancel()
            if p2 in self.wait_tasks:
                self.wait_tasks[p2].cancel()

            async with async_session() as session:
                new_match = Match(
                    player1_id=p1,
                    player2_id=p2,
                    status="active",
                    is_ai_match=False
                )
                session.add(new_match)
                await session.commit()
                return new_match.id

        # Иначе — ждём 10 сек, потом даём бота
        async def wait_and_assign_ai(uid):
            await asyncio.sleep(10)
            if uid in self.waiting_players:
                self.waiting_players.discard(uid)
                await self._create_ai_match(uid)

        self.wait_tasks[user_id] = asyncio.create_task(wait_and_assign_ai(user_id))
        return None
