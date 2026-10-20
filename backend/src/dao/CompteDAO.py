from business_object.compte import Compte
from dao.db_connection import DBConnection
from utils.log_utils import get_logger, log
from utils.singleton import Singleton

logger = get_logger(__name__)


class CompteDAO(metaclass=Singleton):
    """Classe qui gère l'accès aux données des comptes utilisateurs."""

    @log
    def create(self, compte: Compte) -> int | None:
        """Crée un compte dans la base de données et renvoie son id"""
        res = None
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO compte (username, is_admin, password, email, access_token)
                        VALUES (%(username)s, %(is_admin)s, %(password)s, %(email)s, %(access_token)s)
                        RETURNING user_id;
                        """,
                        {
                            "username": compte.username,
                            "is_admin": compte.is_admin,
                            "password": compte.password_hash,
                            "email": compte.email,
                            "access_token": compte.access_token,
                        },
                    )
                    res = cursor.fetchone()
                    if res:
                        compte.user_id = res["user_id"]
                        return res["user_id"]
        except Exception as e:
            logger.error(e)
            raise

        return None

    @log
    def find_by_id(self, user_id: int) -> Compte | None:
        """Récupère un compte à partir de son identifiant unique"""
        res = None
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """SELECT user_id, username, is_admin, password, email,
                         access_token FROM compte WHERE user_id = %(user_id)s;""",
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
                password=res["password"],
                email=res["email"],
                access_token=res["access_token"]
            )
        return compte

    @log
    def find_by_username(self, username: str) -> Compte | None:
        """Récupère un compte à partir de son username"""
        res = None
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """SELECT user_id, username, is_admin, password, email,
                         access_token FROM compte WHERE username = %(username)s;""",
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
                password=res["password"],
                email=res["email"],
                access_token=res["access_token"]
            )
        return compte

    @log
    def list_all(self) -> list[Compte]:
        """Récupère la liste de tous les comptes enregistrés"""
        res = None
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """SELECT user_id, username, is_admin, password,
                        email, access_token FROM compte ORDER BY username;"""
                    )
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
                    password=row["password"],
                    email=row["email"],
                    access_token=row["access_token"]
                )
                comptes_list.append(compte)

        return comptes_list

    @log
    def update(self, compte: Compte) -> bool:
        """Met à jour les informations d'un compte existant."""
        nb_affected_rows = 0
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE compte
                        SET username = %(username)s,
                            is_admin = %(is_admin)s,
                            password = COALESCE(%(password)s, password),
                            email = %(email)s,
                            access_token = COALESCE(%(access_token)s, access_token)
                        WHERE user_id = %(user_id)s;
                        """,
                        {
                            "user_id": compte.user_id,
                            "username": compte.username,
                            "is_admin": compte.is_admin,
                            "password": compte.password_hash,
                            "email": compte.email,
                            "access_token": compte.access_token,
                        },
                    )
                    nb_affected_rows = cursor.rowcount
        except Exception as e:
            logger.error(e)
            raise

        return nb_affected_rows == 1

    @log
    def delete(self, user_id: int) -> bool:
        """Supprime un compte de la base de données par son identifiant"""
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
    def login(self, username: str, password: str) -> Compte | None:
        """Connecte un utilisateur en vérifiant son username et son mot de passe"""
        res = None
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT user_id, username, is_admin, password, email, access_token
                        FROM compte
                        WHERE username = %(username)s
                        AND password = %(password)s;
                        """,
                        {"username": username, "password": password},
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
                password=res["password"],
                email=res["email"],
                access_token=res["access_token"]
            )

        return compte

    @log
    def find_by_token(self, access_token: str) -> Compte | None:
        """Trouve un compte à partir de son access_token"""
        if not access_token:
            return None

        res = None
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT user_id, username, is_admin, password, email, access_token
                        FROM compte
                        WHERE access_token = %(token)s;
                        """,
                        {"token": access_token},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(f"Erreur lors de la recherche par token : {e}")
            raise

        compte = None
        if res:
            compte = Compte(
                user_id=res["user_id"],
                username=res["username"],
                is_admin=res["is_admin"],
                password=res["password"],
                email=res["email"],
                access_token=res["access_token"]
            )

        return compte
