from coin_flip_mode import CoinFlipMode
from dice_mode import DiceMode
from game_mode import GameMode


class GameModeFactory:
    @classmethod
    def get_mode(cls, game_mode: str) -> GameMode:
        """
        Returns the corresponding GameMode object.
        Args:
            game_mode (str): The identifier of the game mode (e.g., 'coinflip', 'dice').
        Returns:
            GameMode: An instance of a class implementing GameMode.
        Raises:
            ValueError: If the requested game_mode is not supported.
        """

        if game_mode == "coin_flip":
            return CoinFlipMode()
        elif game_mode == "dice":
            return DiceMode()
        else:
            raise ValueError(f"Unsupported game_mode : {game_mode}")
