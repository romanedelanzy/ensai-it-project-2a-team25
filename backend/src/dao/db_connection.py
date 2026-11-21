import os

import psycopg2
from psycopg2.extras import RealDictCursor

from utils.singleton import Singleton


class DBConnection(metaclass=Singleton):

    def __init__(self):
        self.__connection = self._create_connection()

    def _create_connection(self):
        """Crée et retourne une nouvelle connexion PostgreSQL."""
        return psycopg2.connect(
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
        Si la connexion est fermée ou inutilisable, la recrée.
        """
        if self.__connection.closed:
            self.__connection = self._create_connection()
        else:
            try:
                with self.__connection.cursor() as cur:
                    cur.execute("SELECT 1")

                self.__connection.rollback()

            except psycopg2.Error:
                try:
                    self.__connection.rollback()
                except psycopg2.Error:
                    pass

                self.__connection = self._create_connection()

        return self.__connection

    def close(self):
        """Ferme proprement la connexion PostgreSQL."""
        if self.__connection and not self.__connection.closed:
            self.__connection.close()
