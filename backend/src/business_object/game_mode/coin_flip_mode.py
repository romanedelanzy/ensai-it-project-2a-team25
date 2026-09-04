
import secrets
from datetime import datetime
from typing import TYPE_CHECKING

from game import Game
from game_mode import GameMode

if TYPE_CHECKING:
    from player import Player


class CoinFlipMode(GameMode):
    def play(self, p1: Player, p2: Player, **kwargs) -> Game:
        choice = kwargs.get("choice", "Heads")
        result = secrets.choice(["Heads", "Tails"])
        winner = p1 if result == choice else p2
        description = f"Choice was {choice}, {winner} wins !"

        return Game(p1, p2, "coin_flip_mode", winner, description, datetime.now())
