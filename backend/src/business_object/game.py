from datetime import datetime

from player import Player


class Game:
    def __init__(
        self,
        player1: Player,
        player2: Player,
        game_mode: str,
        winner: Player | None,
        description: str,
        timestamp: datetime
    ):
        self.player1 = player1
        self.player2 = player2
        self.game_mode = game_mode
        self.winner = winner
        self.description = description
        self.id_game = None

        def __str__(self):
            """Returns a string representation of the game.
        Returns:
            str: A string containing the username and Elo rating.
        """  # ruff: ignore[indentation-with-invalid-multiple]
        winner_name = self.winner.username if self.winner else "Draw"
        return (
            f"{self.game_mode}, between {self.player1.username}"
            f"and {self.player2.username}.\n winner : {winner_name}")
