from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game import Game
    from player import Player


class GameMode(ABC):
    """Classe abstraite représentant le mode de jeu"""

    @abstractmethod
    def play(self, p1: "Player", p2: "Player", **kwargs) -> "Game":
        pass
