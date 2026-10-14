import psycopg2
import pytest

from business_object.station import Station
from dao.StationDAO import StationDao
from utils.reset_database import ResetDatabase  # adapte au nom réel dans utils/


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Réinitialise le schéma de test une fois pour toute la session."""
    ResetDatabase().run(True)
    yield


def test_find_by_id_ok():
    station = StationDao().find_by_id("TEST_001")

    assert station is not None
    assert station.name == "Alpha"
    assert station.reseau_id == 999
    assert station.capacite == 30


def test_find_by_id_adresse_null():
    station = StationDao().find_by_id("TEST_003")

    assert station is not None
    assert station.adresse is None


def test_find_by_id_inexistant():
    assert StationDao().find_by_id("N_EXISTE_PAS") is None


def test_list_all():
    stations = StationDao().list_all()
    noms = [s.name for s in stations]

    assert {"Alpha", "Bravo", "Charlie"} <= set(noms)
    assert noms == sorted(noms)  # list_all trie par nom


def test_create_ok():
    station = Station("NEW_001", 999, "Nouvelle", 48.85, 2.35, 25, "3 rue Neuve")

    assert StationDao().create(station) is True

    relue = StationDao().find_by_id("NEW_001")
    assert relue is not None
    assert relue.name == "Nouvelle"


def test_create_doublon():
    station = Station("TEST_001", 999, "Doublon", 48.85, 2.35, 10)

    with pytest.raises(psycopg2.errors.UniqueViolation):
        StationDao().create(station)


def test_create_reseau_inexistant():
    station = Station("NEW_002", 12345, "Sans réseau", 48.85, 2.35, 10)

    with pytest.raises(psycopg2.errors.ForeignKeyViolation):
        StationDao().create(station)


def test_create_or_update_modification():
    station = Station("TEST_002", 999, "Bravo modifiée", 48.8443, 2.3736, 99)

    assert StationDao().create_or_update(station) is True

    relue = StationDao().find_by_id("TEST_002")
    assert relue.name == "Bravo modifiée"
    assert relue.capacite == 99


def test_create_or_update_insertion():
    station = Station("NEW_003", 998, "Insérée", 48.86, 2.36, 15)

    assert StationDao().create_or_update(station) is True
    assert StationDao().find_by_id("NEW_003") is not None