from datetime import datetime

from player import player


class Game:
    """Business object to store the necessary information after each game is played."""

    def __init__(
        self,
        player1: player,
        player2: player,
        game_mode: str,
        winner: player,
        description: str,
        timestamp: datetime,
    ):
        """Constructor"""
        self.id_game = None
        self.player1 = player1
        self.player2 = player2
        self.game_mode = game_mode
        self.winner = winner
        self.description = description
        self.timestamp = timestamp

    def __str__(self):
        """Returns a string representation of the game.
        Returns:
            str: A string containing the two username of the players, the game type and winner.
        """
        a = (
            f"{self.game_mode} between {self.player1.username} and "
            f"{self.player2.username}. Winner: {self.winner}"
            )
        return a
