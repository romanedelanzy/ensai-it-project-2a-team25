from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from business_object.favoris import Favori
from dao.FavoriDAO import FavoriDao


@pytest.fixture(autouse=True)
def mock_cursor():
    """Remplace DBConnection par un faux : aucune vraie base n'est utilisée.

    Retourne le faux curseur, que chaque test configure (rowcount, fetchall...).
    """
    cursor = MagicMock()

    connection = MagicMock()
    connection.__enter__.return_value = connection  # with ... .connection as connection
    connection.cursor.return_value.__enter__.return_value = cursor  # with connection.cursor() as cursor

    with patch("dao.FavoriDAO.DBConnection") as db_connection:
        db_connection.return_value.connection = connection
        yield cursor


# ---------- add_favorite ----------


def test_add_favorite_ok(mock_cursor):
    """Successfully add a favorite"""

    # GIVEN
    mock_cursor.rowcount = 1

    # WHEN
    res = FavoriDao().add_favorite(1, "TEST_001")

    # THEN
    assert res is True
    mock_cursor.execute.assert_called_once()
    assert mock_cursor.execute.call_args[0][1] == {"user_id": 1, "station_id": "TEST_001"}


def test_add_favorite_fail(mock_cursor):
    """Fail to add a favorite because no row was inserted"""

    # GIVEN
    mock_cursor.rowcount = 0

    # WHEN
    res = FavoriDao().add_favorite(1, "TEST_001")

    # THEN
    assert res is False


def test_add_favorite_exception(mock_cursor):
    """The database error (duplicate, unknown station...) is propagated"""

    # GIVEN
    mock_cursor.execute.side_effect = Exception("erreur SQL")

    # WHEN / THEN
    with pytest.raises(Exception, match="erreur SQL"):
        FavoriDao().add_favorite(1, "TEST_001")


# ---------- remove_favorite ----------


def test_remove_favorite_ok(mock_cursor):
    """Successfully remove a favorite"""

    # GIVEN
    mock_cursor.rowcount = 1

    # WHEN
    res = FavoriDao().remove_favorite(1, "TEST_001")

    # THEN
    assert res is True
    mock_cursor.execute.assert_called_once()
    assert mock_cursor.execute.call_args[0][1] == {"user_id": 1, "station_id": "TEST_001"}


def test_remove_favorite_fail(mock_cursor):
    """Fail to remove a favorite because it does not exist"""

    # GIVEN
    mock_cursor.rowcount = 0

    # WHEN
    res = FavoriDao().remove_favorite(1, "N_EXISTE_PAS")

    # THEN
    assert res is False


def test_remove_favorite_exception(mock_cursor):
    """The database error is propagated"""

    # GIVEN
    mock_cursor.execute.side_effect = Exception("erreur SQL")

    # WHEN / THEN
    with pytest.raises(Exception, match="erreur SQL"):
        FavoriDao().remove_favorite(1, "TEST_001")


# ---------- user_favorite ----------


def test_user_favorite_ok(mock_cursor):
    """List the favorites of a user"""

    # GIVEN
    date = datetime(2026, 10, 15, 12, 0)
    mock_cursor.fetchall.return_value = [
        {"station_id": "TEST_001", "user_id": 1, "create_at": date},
        {"station_id": "TEST_002", "user_id": 1, "create_at": date},
    ]

    # WHEN
    res = FavoriDao().user_favorite(1)

    # THEN
    assert len(res) == 2
    assert all(isinstance(f, Favori) for f in res)
    assert [f.station_id for f in res] == ["TEST_001", "TEST_002"]
    assert res[0].utilisateur_id == 1
    assert res[0].cree_a == date
    assert mock_cursor.execute.call_args[0][1] == {"user_id": 1}


def test_user_favorite_empty(mock_cursor):
    """A user without favorites gets an empty list"""

    # GIVEN
    mock_cursor.fetchall.return_value = []

    # WHEN
    res = FavoriDao().user_favorite(3)

    # THEN
    assert res == []


def test_user_favorite_exception(mock_cursor):
    """The database error is propagated"""

    # GIVEN
    mock_cursor.execute.side_effect = Exception("erreur SQL")

    # WHEN / THEN
    with pytest.raises(Exception, match="erreur SQL"):
        FavoriDao().user_favorite(1)


if __name__ == "__main__":
    pytest.main([__file__])