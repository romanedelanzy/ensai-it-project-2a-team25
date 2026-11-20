import os

import psycopg2
from psycopg2.extras import RealDictCursor

from utils.singleton import Singleton


class DBConnection(metaclass=Singleton):

    def __init__(self):
        self.__connection = None
        self.__connect()

    def __connect(self):
        """Établit une nouvelle connexion PostgreSQL."""
        self.__connection = psycopg2.connect(
            host=os.environ["POSTGRES_HOST"],
            port=os.environ["POSTGRES_PORT"],
            database=os.environ["POSTGRES_DATABASE"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            options=f"-c search_path={os.environ['POSTGRES_SCHEMA']}",
            cursor_factory=RealDictCursor,
        )

    @property
    def connection(self):
        """
        Retourne une connexion valide.
        Si la connexion est fermée ou inutilisable, en crée une nouvelle.
        """
        if self.__connection is None or self.__connection.closed != 0:
            self.__connect()
        else:
            try:
                with self.__connection.cursor() as cur:
                    cur.execute("SELECT 1")

            except psycopg2.Error:
                self.__connect()

        return self.__connection

    def close(self):
        """Ferme proprement la connexion PostgreSQL."""
        if self.__connection and self.__connection.closed == 0:
            self.__connection.close()