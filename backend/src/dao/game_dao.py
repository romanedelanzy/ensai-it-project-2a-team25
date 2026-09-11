from business_object.game import Game
from business_object.player import Player
from dao import PlayerDao
from dao.db_connection import DBConnection
from utils.log_utils import get_logger, log
from utils.singleton import Singleton

logger = get_logger(__name__)


class GameDao(metaclass=Singleton):
    """Class containing methods to access games in the database."""

    @log
    def create(self, game) -> bool:
        """Create a game in the database.
        Args:
            Game to create
        Returns:
            True if creation is successful, False otherwise
        """
        res = None

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO game(id_game, id_player1, id_player2, game_mode, id_winner, detail, timestamp) VALUES "
                        "(%(id_game)s, %(id_player1)s, %(id_player2)s, %(game_mode)s, %(id_winner)s, %(detail)s, %(timestamp)s) "
                        "RETURNING id_game;",
                        {
                            "id_game": game.id_game,
                            "id_player1": game.player1.id_player1,
                            "id_player2": game.player2.id_player2,
                            "game_mode": game.game_mode,
                            "id_winner": game.winner.id_winner,
                            "detail": game.description,
                            "timestamp": game.timestamp
                        },
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        created = False
        if res:
            game.id_game = res["id_game"]
            created = True

        return created

    @log
    def find_by_id(self, id_game: int) -> Game:
        """Find a game by their id.
        Args:
            id_game (int): The ID of the game to find
        Returns:
            Game matching the given id
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT *                            "
                        "  FROM game                       "
                        " WHERE id_game = %(id_game)s;   ",
                        {"id_game": id_game},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        game = None
        if res:
            p1 = PlayerDao().find_by_id(res["id_player1"])
            p2 = PlayerDao().find_by_id(res["id_player2"])
            winner = PlayerDao().find_by_id(res["winner"])
            game = Game(
                id_game=res["id_game"],
                player1=p1,
                player2=p2,
                game_mode=res["game_mode"],
                winner=winner,
                description=res["detail"],
                timestamp=res["timestamp"],
            )

        return game

    @log
    def find_all(self) -> list[Game]:
        """List all games in the database.
        Returns:
            list[Game] sorted by id
        """

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT *                                "
                        "  FROM game                           "
                        " ORDER BY id_game;                     "
                    )
                    res = cursor.fetchall()
        except Exception as e:
            logger.error(e)
            raise

        games_list = []

        if res:
            for row in res:
                p1 = PlayerDao().find_by_id(row["id_player1"])
                p2 = PlayerDao().find_by_id(row["id_player2"])
                winner = PlayerDao().find_by_id(row["id_winner"])
                game = Game(
                            id_game=row["id_game"],
                            game_mode=row["game_mode"],
                            player1=p1,
                            player2=p2,
                            winner=winner,
                            description=row["detail"],
                            timestamp=res["timestamp"]
                            )

                games_list.append(game)

        return games_list