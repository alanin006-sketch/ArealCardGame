# game/matchmaker.py
import asyncio
from database.models import Match
from database.db import async_session
from game.ai_player import SimpleAI

class Matchmaker:
    def __init__(self, bot):
        self.bot = bot  # ← получаем бота извне
        self.waiting_players = set()
        self.wait_tasks = {}

    async def _create_ai_match(self, user_id: int):
        async with async_session() as session:
            new_match = Match(
                player1_id=user_id,
                player2_id=-1,
                status="active",
                is_ai_match=True,
                hand_p1=[
                    {"id": 1, "name": "Сталкер-одиночка", "power": 4},
                    {"id": 2, "name": "Артефакт 'Пустышка'", "power": 0},
                    {"id": 3, "name": "Военный патруль", "power": 6},
                ],
                hand_p2=[
                    {"id": 1, "name": "БОТ-Сталкер", "power": 5},
                    {"id": 2, "name": "Аномалия", "power": 3},
                    {"id": 3, "name": "Монолит-Палач", "power": 7},
                ],
                board_p1=[],
                board_p2=[],
                scores={"p1": 0, "p2": 0}
            )
            session.add(new_match)
            await session.commit()

        # Отправляем сообщение игроку
        try:
            cards_text = "\n".join(f"{i}. {card['name']} ({card['power']})" for i, card in enumerate(new_match.hand_p1))
            await self.bot.send_message(
                user_id,
                "🤖 БОТ-сталкер вступил в бой!\n"
                "Выберите карту: /play_0, /play_1, /play_2\n\n"
                f"Ваша рука:\n{cards_text}"
            )
        except Exception as e:
            print(f"Ошибка отправки сообщения AI-матча: {e}")

    async def add_player(self, user_id: int):
        self.waiting_players.add(user_id)
        if len(self.waiting_players) >= 2:
            # PvP матч (пропускаем)
            p1 = self.waiting_players.pop()
            p2 = self.waiting_players.pop()
            async with async_session() as session:
                match = Match(player1_id=p1, player2_id=p2, status="active", is_ai_match=False)
                session.add(match)
                await session.commit()
            return match.id

        # Запускаем таймер на AI
        async def wait_and_assign_ai(uid):
            await asyncio.sleep(5)  # уменьшил до 5 сек для теста
            if uid in self.waiting_players:
                self.waiting_players.discard(uid)
                await self._create_ai_match(uid)

        if user_id in self.wait_tasks:
            self.wait_tasks[user_id].cancel()
        self.wait_tasks[user_id] = asyncio.create_task(wait_and_assign_ai(user_id))
        return None
