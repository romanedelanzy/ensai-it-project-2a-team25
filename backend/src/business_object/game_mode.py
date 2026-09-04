from abc import ABC, abstractmethod

from business_object.game import Game
from business_object.player import Player


class GameMode(ABC):

    """Abstract class that defines generic game mode."""

    @abstractmethod
    def play(self, player1: Player, player2: Player) -> Game:
        pass
