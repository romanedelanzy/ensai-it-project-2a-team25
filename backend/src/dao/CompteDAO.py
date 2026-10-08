from business_object.compte import Compte
from dao.db_connection import DBConnection
from utils.log_utils import get_logger, log
from utils.singleton import Singleton
import psycopg2

logger = get_logger(__name__)


class CompteDAO(metaclass=Singleton):
    """Classe qui gère l'accès aux données des comptes utilisateurs."""

    @log
    def trouver_par_id(self, user_id: int) -> Compte | None:
        """Récupère un compte à partir de son identifiant unique."""
        res = None
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT user_id, username, is_admin, password_hash, email FROM compte WHERE user_id = %(user_id)s;",
                        {"user_id": user_id}
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        compte = None
        if res:
            compte = Compte(
                user_id=res["user_id"],
                username=res["username"],
                is_admin=res["is_admin"],
                password=res["password_hash"],
                email=res["email"]
            )
        return compte

    @log
    def trouver_par_username(self, username: str) -> Compte | None:
        """Récupère un compte à partir de son username."""
        res = None
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT user_id, username, is_admin, password_hash, email FROM compte WHERE username = %(username)s;",
                        {"username": username}
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        compte = None
        if res:
            compte = Compte(
                user_id=res["user_id"],
                username=res["username"],
                is_admin=res["is_admin"],
                password=res["password_hash"],
                email=res["email"]
            )
        return compte

    @log
    def creer(self, compte: Compte) -> int | None:  # Change le type de retour si tu veux
        res = None
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO compte (username, is_admin, password_hash, email)
                        VALUES (%(username)s, %(is_admin)s, %(password_hash)s, %(email)s)
                        RETURNING user_id;
                        """,
                        {
                            "username": compte.username,
                            "is_admin": compte.is_admin,
                            "password_hash": compte.password_hash,
                            "email": compte.email,
                        },
                    )
                    res = cursor.fetchone()
                    if res:
                        compte.user_id = res["user_id"]
                        return res["user_id"]  # <--- On retourne directement le user_id récupéré
        except Exception as e:
            logger.error(e)
            raise

        return None

    @log
    def update(self, compte: Compte) -> bool:
        """Met à jour les informations d'un compte existant."""
        res = None
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE compte 
                        SET username = %(username)s, 
                            is_admin = %(is_admin)s, 
                            password_hash = %(password_hash)s, 
                            email = %(email)s
                        WHERE user_id = %(user_id)s
                        RETURNING user_id;
                        """,
                        {
                            "user_id": compte.user_id,
                            "username": compte.username,
                            "is_admin": compte.is_admin,
                            "password_hash": compte.password_hash,
                            "email": compte.email,
                        },
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        return res is not None

    @log
    def delete(self, user_id: int) -> bool:
        """Supprime un compte de la base de données par son identifiant."""
        res = None
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM compte WHERE user_id = %(user_id)s RETURNING user_id;",
                        {"user_id": user_id}
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        return res is not None

    @log
    def list_all(self) -> list[Compte]:
        """Récupère la liste de tous les comptes enregistrés."""
        res = None
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT user_id, username, is_admin, password_hash, email FROM compte ORDER BY username;")
                    res = cursor.fetchall()
        except Exception as e:
            logger.error(e)
            raise

        comptes_list = []
        if res:
            for row in res:
                compte = Compte(
                    user_id=row["user_id"],
                    username=row["username"],
                    is_admin=row["is_admin"],
                    password=row["password_hash"],
                    email=row["email"]
                )
                comptes_list.append(compte)

        return comptes_list