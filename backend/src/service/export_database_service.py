import os
from pathlib import Path

from psycopg2 import sql

from dao.db_connection import DBConnection
from utils.log_utils import get_logger

logger = get_logger(__name__)


class ExportDatabaseService:

    def __init__(self):
        # Pour avoir le chemin d'accès de pop_db.sql
        self.base_path = Path(__file__).resolve().parent.parent.parent.parent
        self.output_path = self.base_path / "data" / "pop_db.sql"

    def run(self):
        schema = os.environ["POSTGRES_SCHEMA"]

        tables = [
            "compte",
            "reseau",
            "station",
            "station_status",
            "favoris",
        ]
        # 10 lignes par INSERT INTO
        batch_size = 10

        connection = DBConnection().connection

        with connection.cursor() as cursor:
            with open(self.output_path, "w", encoding="utf-8") as file:

                file.write(
                    "-- Export automatique de la base VeloScope\n"
                    f"-- Schema : {schema}\n"
                )

                for table in tables:

                    query = sql.SQL("SELECT * FROM {}.{}").format(
                        sql.Identifier(schema),
                        sql.Identifier(table),
                    )

                    cursor.execute(query)
                    rows = cursor.fetchall()

                    if not rows:
                        continue

                    columns = list(rows[0].keys())

                    file.write(f"\n-- Data for {table}\n")

                    for i in range(0, len(rows), batch_size):

                        batch = rows[i:i + batch_size]

                        values_list = []

                        for row in batch:

                            values = [
                                sql.Literal(row[column]).as_string(connection)
                                for column in columns
                            ]

                            values_tuple = (
                                "(" + ", ".join(values) + ")"
                            )

                            values_list.append(values_tuple)

                        insert_query = sql.SQL(
                            "INSERT INTO {}.{} ({}) VALUES\n{}\n;\n"
                        ).format(
                            sql.Identifier(schema),
                            sql.Identifier(table),
                            sql.SQL(", ").join(
                                sql.Identifier(column)
                                for column in columns
                            ),
                            sql.SQL(",\n").join(
                                sql.SQL(value)
                                for value in values_list
                            ),
                        )

                        file.write(insert_query.as_string(connection))

        logger.info("Export SQL terminé : %s", self.output_path)