from business_object.favori import Favori
from dao.db_connection import DBConnection
from utils.log_utils import get_logger, log
from utils.singleton import Singleton

logger = get_logger(__name__)


class FavoriDao(metaclass=Singleton):
    """Classe permettant d'accéder aux favoris dans la base de données."""

    @log
    def add_favorite(self, user_id: int, station_id: int) -> bool:
        """Ajoute une station aux favoris d'un utilisateur.

        Args:
            user_id : int
                 Identifiant de l'utilisateur.
            station_id :int
                 Identifiant de la station.

        Returns:
            bool:
                True si le favori a été ajouté, False sinon.
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO favoris(user_id, station_id, create_at)
                        VALUES (
                            %(user_id)s,
                            %(station_id)s,
                            CURRENT_TIMESTAMP
                        );
                        """,
                        {
                            "user_id": user_id,
                            "station_id": station_id,
                        },
                    )

                    res = cursor.rowcount

        except Exception as e:
            logger.error(e)
            raise

        return res == 1

    @log
    def remove_favorite(self, user_id: int, station_id: int) -> bool:
        """Supprime une station des favoris d'un utilisateur.

        Args:
            user_id : int
                Identifiant de l'utilisateur.
            station_id :int
                 Identifiant de la station.

        Returns:
            bool: True si le favori a été supprimé, False sinon.
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        DELETE FROM favoris
                        WHERE user_id = %(user_id)s
                        AND station_id = %(station_id)s;
                        """,
                        {
                            "user_id": user_id,
                            "station_id": station_id,
                        },
                    )

                    res = cursor.rowcount

        except Exception as e:
            logger.error(e)
            raise

        return res == 1

    @log
    def user_favorite(self, user_id: int) -> list[Favori]:
        """Retourne les favoris d'un utilisateur.

        Args:
            user_id :int
                 Identifiant de l'utilisateur.

        Returns:
            list[Favori]: Liste des favoris de l'utilisateur.
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT station_id, user_id, create_at
                        FROM favoris
                        WHERE user_id = %(user_id)s;
                        """,
                        {
                            "user_id": user_id,
                        },
                    )

                    res = cursor.fetchall()

        except Exception as e:
            logger.error(e)
            raise

        favoris = []

        if res:
            for row in res:
                favori = Favori(
                    station_id=row["station_id"],
                    utilisateur_id=row["user_id"],
                    cree_a=row["create_at"],
                )

                favoris.append(favori)

        return favoris