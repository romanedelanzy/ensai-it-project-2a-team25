import random
from datetime import datetime
from typing import TYPE_CHECKING

from game import Game
from game_mode import GameMode

if TYPE_CHECKING:
    from player import Player


class DiceMode(GameMode):

    """Implémentation d'un jeu de lancer de dés"""
    def play(self, p1: Player, p2: Player) -> Game:
        roll1 = random.randint(1, 6)
        roll2 = random.randint(1, 6)

        if roll1 > roll2:
            winner = p1
            description = (
                f"{p1.username} rolled {roll1}"
                f"{p2.username} rolled {roll2}, {p1.username} wins !"
            )
        elif roll2 > roll1:
            winner = p2
            description = (
                f"{p1.username} rolled {roll1}"
                f"{p2.username} rolled {roll2}, {p2.username} wins !"
            )
        else:
            winner = "Draw"
            description = (
                f"{p1.username} rolled {roll1}"
                f"{p2.username} rolled {roll2}, it's a draw !"
            )
        return Game(p1, p2, "dice_mode", winner, description, timestamp=datetime.now())
