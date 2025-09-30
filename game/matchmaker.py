from database.models import Match
from database.db import async_session
import asyncio

class Matchmaker:
    def __init__(self):
        self.waiting_players = set()

    async def add_player(self, user_id: int):
        self.waiting_players.add(user_id)
        if len(self.waiting_players) >= 2:
            # Берём двух игроков
            p1 = self.waiting_players.pop()
            p2 = self.waiting_players.pop()
            async with async_session() as session:
                new_match = Match(player1_id=p1, player2_id=p2, status="active")
                session.add(new_match)
                await session.commit()
                return new_match.id
        return None
