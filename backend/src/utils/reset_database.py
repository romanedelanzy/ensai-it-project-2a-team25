
import os
from pathlib import Path
from unittest import mock

import dotenv

from dao.db_connection import DBConnection
from utils.database_utils import synchronize_compte_sequence
from utils.log_utils import get_logger, log
from utils.singleton import Singleton

logger = get_logger(__name__)


class ResetDatabase(metaclass=Singleton):
    """
    Database reset utility
    """

    def __init__(self):
        self.base_path = Path(__file__).resolve().parent.parent.parent.parent

    @log
    def run(self, test_dao=False):
        """Run the database reset
        If test_dao=True: reset test data
        """
        if test_dao:
            mock.patch.dict(
                os.environ, {"POSTGRES_SCHEMA": "project_test_dao"}
            ).start()
            pop_data_path = self.base_path / "data" / "pop_db_test.sql"
        else:
            pop_data_path = self.base_path / "data" / "pop_db.sql"

        init_db_path = self.base_path / "data" / "init_db.sql"

        dotenv.load_dotenv()

        schema = os.environ["POSTGRES_SCHEMA"]
        create_schema = (
            f"DROP SCHEMA IF EXISTS {schema} CASCADE; "
            f"CREATE SCHEMA {schema};"
        )

        # Lecture des fichiers SQL
        try:
            with open(init_db_path, encoding="utf-8") as init_db_file:
                init_db_as_string = init_db_file.read()

            with open(pop_data_path, encoding="utf-8") as pop_db_file:
                pop_db_as_string = pop_db_file.read()

            logger.info(
                "Taille init_db.sql : %s caractères",
                len(init_db_as_string),
            )
            logger.info(
                "Taille pop_db.sql : %s caractères",
                len(pop_db_as_string),
            )

        except FileNotFoundError as e:
            logger.error(
                "Erreur de chemin : impossible de trouver le fichier %s",
                e.filename,
            )
            raise

        # Exécution des scripts SQL
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:

                    logger.info("Étape 1 : suppression et création du schéma")
                    cursor.execute(create_schema)

                    logger.info("Étape 2 : définition du search_path")
                    cursor.execute(f"SET search_path TO {schema}, public;")

                    logger.info("Étape 3 : exécution de init_db.sql")
                    cursor.execute(init_db_as_string)

                    logger.info("Étape 4 : exécution de pop_db.sql")
                    cursor.execute(pop_db_as_string)

                    logger.info("Toutes les étapes SQL ont été exécutées.")

            # Synchronisation après le chargement des données
            logger.info("Synchronisation de la séquence des comptes.")
            synchronize_compte_sequence()
            logger.info("Séquence des comptes synchronisée.")

        except Exception:
            logger.exception("Échec du reset de la base de données.")
            raise

        return True


if __name__ == "__main__":
    ResetDatabase().run()
    ResetDatabase().run(True)
