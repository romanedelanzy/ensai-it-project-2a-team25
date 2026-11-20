import os
from pathlib import Path

from psycopg2 import sql

from dao.db_connection import DBConnection
from utils.log_utils import get_logger

logger = get_logger(__name__)


class ExportDatabaseService:

    def __init__(self):
        self.base_path = Path(__file__).resolve().parent.parent.parent.parent
        self.output_path = self.base_path / "data" / "pop_db.sql"

    def run(self):
        schema = os.environ["POSTGRES_SCHEMA"]

        tables = [
            "station",
            "station_status",
            "compte",
            "favoris",
        ]

        connection = DBConnection().connection

        with connection.cursor() as cursor:
            with open(self.output_path, "w", encoding="utf-8") as file:

                file.write(
                    f"-- Export automatique de la base VeloScope\n"
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

                    for row in rows:

                        values = []

                        for column in columns:
                            value = row[column]

                            if value is None:
                                values.append("NULL")

                            elif isinstance(value, str):
                                value = value.replace("'", "''")
                                values.append(f"'{value}'")

                            else:
                                values.append(str(value))

                        file.write(
                            f"INSERT INTO {table} "
                            f"({', '.join(columns)}) "
                            f"VALUES ({', '.join(values)});\n"
                        )

        logger.info("Export SQL terminé : %s", self.output_path)