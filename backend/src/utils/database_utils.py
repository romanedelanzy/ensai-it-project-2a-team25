
from dao.db_connection import DBConnection


def synchronize_compte_sequence():
    """
    Synchronise la séquence PostgreSQL des identifiants des comptes
    avec les identifiants déjà présents dans la table.
    """
    connection = DBConnection().connection

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT setval(
                    pg_get_serial_sequence('compte', 'user_id'),
                    COALESCE(MAX(user_id), 1),
                    COUNT(*) > 0
                )
                FROM compte;
            """)

        connection.commit()

    except Exception:
        connection.rollback()
        raise
