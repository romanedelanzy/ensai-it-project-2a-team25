from decimal import Decimal
from unittest.mock import MagicMock, patch

import psycopg2
import pytest

from business_object.station import Station
from dao.StationDAO import StationDao


@pytest.fixture(autouse=True)
def mock_cursor():
    """Remplace DBConnection par un faux : aucune vraie base n'est utilisée.
    Retourne le faux curseur, que chaque test configure (rowcount, fetchone...).
    """
    cursor = MagicMock()

    connection = MagicMock()
    connection.__enter__.return_value = connection 
    connection.cursor.return_value.__enter__.return_value = cursor

    with patch("dao.StationDAO.DBConnection") as db_connection:
        db_connection.return_value.connection = connection
        yield cursor


def ligne_station(**champs):
    """Ligne telle que la renvoie PostgreSQL (latitude/longitude en Decimal)."""
    ligne = {
        "station_id": "TEST_001",
        "reseau_id": 999,
        "name": "Alpha",
        "adresse": "1 rue Alpha",
        "latitude": Decimal("48.8566"),
        "longitude": Decimal("2.3522"),
        "capacite": 30,
    }
    ligne.update(champs)
    return ligne



def test_find_by_id_ok(mock_cursor):
    """Find a station by its id"""

    # GIVEN
    mock_cursor.fetchone.return_value = ligne_station()

    # WHEN
    station = StationDao().find_by_id("TEST_001")

    # THEN
    assert station is not None
    assert station.name == "Alpha"
    assert station.reseau_id == 999
    assert station.capacite == 30
    assert isinstance(station.latitude, float)  # Decimal converti en float
    assert mock_cursor.execute.call_args[0][1] == {"station_id": "TEST_001"}


def test_find_by_id_adresse_null(mock_cursor):
    """A station without address has adresse set to None"""

    # GIVEN
    mock_cursor.fetchone.return_value = ligne_station(station_id="TEST_003", adresse=None)

    # WHEN
    station = StationDao().find_by_id("TEST_003")

    # THEN
    assert station is not None
    assert station.adresse is None


def test_find_by_id_inexistant(mock_cursor):
    """Unknown id returns None"""

    # GIVEN
    mock_cursor.fetchone.return_value = None

    # WHEN
    res = StationDao().find_by_id("N_EXISTE_PAS")

    # THEN
    assert res is None


def test_find_by_id_exception(mock_cursor):
    """The database error is propagated"""

    # GIVEN
    mock_cursor.execute.side_effect = Exception("erreur SQL")

    # WHEN / THEN
    with pytest.raises(Exception, match="erreur SQL"):
        StationDao().find_by_id("TEST_001")




def test_list_all_ok(mock_cursor):
    """List all stations"""

    # GIVEN
    mock_cursor.fetchall.return_value = [
        ligne_station(station_id="TEST_001", name="Alpha"),
        ligne_station(station_id="TEST_002", name="Bravo"),
        ligne_station(station_id="TEST_003", name="Charlie"),
    ]

    # WHEN
    stations = StationDao().list_all()

    # THEN
    assert [s.name for s in stations] == ["Alpha", "Bravo", "Charlie"]
    assert all(isinstance(s, Station) for s in stations)
    assert "ORDER BY name" in mock_cursor.execute.call_args[0][0]  # trié par nom


def test_list_all_vide(mock_cursor):
    """No station in the database gives an empty list"""

    # GIVEN
    mock_cursor.fetchall.return_value = []

    # WHEN
    stations = StationDao().list_all()

    # THEN
    assert stations == []



def test_create_ok(mock_cursor):
    """Successfully create a station"""

    # GIVEN
    station = Station("NEW_001", 999, "Nouvelle", 48.85, 2.35, 25, "3 rue Neuve")
    mock_cursor.fetchone.return_value = {"station_id": "NEW_001"}

    # WHEN
    res = StationDao().create(station)

    # THEN
    assert res is True
    mock_cursor.execute.assert_called_once()
    assert "INSERT INTO station" in mock_cursor.execute.call_args[0][0]
    assert mock_cursor.execute.call_args[0][1] == station.to_dict()


def test_create_fail(mock_cursor):
    """Fail to create a station because no row was returned"""

    # GIVEN
    station = Station("NEW_001", 999, "Nouvelle", 48.85, 2.35, 25)
    mock_cursor.fetchone.return_value = None

    # WHEN
    res = StationDao().create(station)

    # THEN
    assert res is False


def test_create_doublon(mock_cursor):
    """The duplicate error is propagated"""

    # GIVEN
    station = Station("TEST_001", 999, "Doublon", 48.85, 2.35, 10)
    mock_cursor.execute.side_effect = psycopg2.errors.UniqueViolation("doublon")

    # WHEN / THEN
    with pytest.raises(psycopg2.errors.UniqueViolation):
        StationDao().create(station)


def test_create_reseau_inexistant(mock_cursor):
    """The unknown network error is propagated"""

    # GIVEN
    station = Station("NEW_002", 12345, "Sans réseau", 48.85, 2.35, 10)
    mock_cursor.execute.side_effect = psycopg2.errors.ForeignKeyViolation("réseau inconnu")

    # WHEN / THEN
    with pytest.raises(psycopg2.errors.ForeignKeyViolation):
        StationDao().create(station)




def test_create_or_update_modification(mock_cursor):
    """Update an existing station"""

    # GIVEN
    station = Station("TEST_002", 999, "Bravo modifiée", 48.8443, 2.3736, 99)
    mock_cursor.fetchone.return_value = {"station_id": "TEST_002"}

    # WHEN
    res = StationDao().create_or_update(station)

    # THEN
    assert res is True
    assert "ON CONFLICT (station_id) DO UPDATE" in mock_cursor.execute.call_args[0][0]
    assert mock_cursor.execute.call_args[0][1] == station.to_dict()


def test_create_or_update_insertion(mock_cursor):
    """Insert a station that does not exist yet"""

    # GIVEN
    station = Station("NEW_003", 998, "Insérée", 48.86, 2.36, 15)
    mock_cursor.fetchone.return_value = {"station_id": "NEW_003"}

    # WHEN
    res = StationDao().create_or_update(station)

    # THEN
    assert res is True
    assert mock_cursor.execute.call_args[0][1]["station_id"] == "NEW_003"



def test_delete_ok(mock_cursor):
    """Successfully delete a station"""

    # GIVEN
    station = Station("TEST_001", 999, "Alpha", 48.85, 2.35, 30)
    mock_cursor.rowcount = 1

    # WHEN
    res = StationDao().delete(station)

    # THEN
    assert res is True
    mock_cursor.execute.assert_called_once()
    assert "DELETE FROM station" in mock_cursor.execute.call_args[0][0]
    assert mock_cursor.execute.call_args[0][1] == {"station_id": "TEST_001"}


def test_delete_fail(mock_cursor):
    """Fail to delete a station because it does not exist"""

    # GIVEN
    station = Station("N_EXISTE_PAS", 999, "Fantôme", 48.85, 2.35, 10)
    mock_cursor.rowcount = 0

    # WHEN
    res = StationDao().delete(station)

    # THEN
    assert res is False


def test_delete_exception(mock_cursor):
    """The database error is propagated"""

    # GIVEN
    station = Station("TEST_001", 999, "Alpha", 48.85, 2.35, 30)
    mock_cursor.execute.side_effect = Exception("erreur SQL")

    # WHEN / THEN
    with pytest.raises(Exception, match="erreur SQL"):
        StationDao().delete(station)


if __name__ == "__main__":
    pytest.main([__file__])