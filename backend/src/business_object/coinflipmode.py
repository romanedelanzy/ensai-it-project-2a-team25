import secrets
from datetime import datetime

from business_object_object.game import Game
from business_object_object.game_mode import GameMode
from business_object_object.player import Player


class CoinFlipMode(GameMode):

    def play(self, p1: Player, p2: Player, choice="heads"):
        if (choice not in ["heads", "tails"]):
            raise TypeError("Mauvais choix de synthaxe")

        choice = choice.lower()
        result = secrets.choice(["heads", "tails"])
        winner = p1 if result == choice else p2
        return Game(
            p1,
            p2,
            "coin_flip",
            winner,
            f"Coin flip game : {result}",
            datetime.now())
