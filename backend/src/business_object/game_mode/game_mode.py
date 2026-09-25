from abc import ABC, abstractmethod

from business_object.game import Game

from business_object.player import Player


class GameMode(ABC):
    """Abstract base class for all game modes."""

    @abstractmethod
    def play(self, p1: Player, p2: Player) -> Game:
        """Executes the game logic and returns a Game object."""
        pass
