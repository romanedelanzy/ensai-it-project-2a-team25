from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from business_object.station import Station
from business_object.stationstatus import StationStatus
from controller.station_controller import get_station_service, router
from utils.security import verify_token


def creer_station(station_id="ST001", name="Place Pey Berland"):
    return Station(station_id, 1, name, 44.8378, -0.5792, 20, "Place Pey-Berland")


def creer_status(nb_velos_dispos=5):
    return StationStatus(
        id_station="ST001",
        horodatage=datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc),
        nb_velos_dispos=nb_velos_dispos,
        nb_velos_elec_dispos=1,
        nb_places_dispos=15,
        est_installee=True,
        permet_retour=True,
        permet_emprunt=True,
    )


@pytest.fixture
def station_service():
    """Faux StationService : aucune base n'est utilisée."""
    return MagicMock()


@pytest.fixture
def app(station_service):
    """Mini application contenant seulement le router des stations."""
    app = FastAPI()
    app.include_router(router, prefix="/stations")
    app.dependency_overrides[get_station_service] = lambda: station_service
    app.dependency_overrides[verify_token] = lambda: MagicMock()  # utilisateur connecté
    return app


@pytest.fixture
def client(app):
    return TestClient(app)




def test_find_all_stations_ok(client, station_service):
    """List all stations"""

    # GIVEN
    station_service.list_all.return_value = [
        creer_station("ST001", "Pey Berland"),
        creer_station("ST002", "Quinconces"),
    ]

    # WHEN
    res = client.get("/stations/")

    # THEN
    assert res.status_code == 200
    assert [s["name"] for s in res.json()] == ["Pey Berland", "Quinconces"]
    assert res.json()[0]["station_id"] == "ST001"
    station_service.list_all.assert_called_once_with()


def test_find_all_stations_par_nom(client, station_service):
    """Search stations by name"""

    # GIVEN
    station_service.search_by_name.return_value = [creer_station()]

    # WHEN
    res = client.get("/stations/", params={"name": "pey"})

    # THEN
    assert res.status_code == 200
    assert len(res.json()) == 1
    station_service.search_by_name.assert_called_once_with("pey")
    station_service.list_all.assert_not_called()


def test_station_by_id_ok(client, station_service):
    """Find a station by its id"""

    # GIVEN
    station_service.get_station.return_value = creer_station()

    # WHEN
    res = client.get("/stations/ST001")

    # THEN
    assert res.status_code == 200
    assert res.json()["name"] == "Place Pey Berland"
    assert res.json()["capacite"] == 20
    station_service.get_station.assert_called_once_with("ST001")


def test_station_by_id_inexistante(client, station_service):
    """Unknown station returns 404"""

    # GIVEN
    station_service.get_station.return_value = None

    # WHEN
    res = client.get("/stations/N_EXISTE_PAS")

    # THEN
    assert res.status_code == 404



def test_station_current_status_ok(client, station_service):
    """Get the latest status of a station"""

    # GIVEN
    station_service.get_current_status.return_value = creer_status(nb_velos_dispos=5)

    # WHEN
    res = client.get("/stations/ST001/status")

    # THEN
    assert res.status_code == 200
    assert res.json()["nb_velos_dispos"] == 5
    assert res.json()["est_installee"] is True
    station_service.get_current_status.assert_called_once_with("ST001")


def test_station_current_status_absent(client, station_service):
    """No status for the station returns 404"""

    # GIVEN
    station_service.get_current_status.return_value = None

    # WHEN
    res = client.get("/stations/ST001/status")

    # THEN
    assert res.status_code == 404



def test_station_history_par_defaut_24h(client, station_service):
    """History uses the 24h period by default"""

    # GIVEN
    station_service.get_station.return_value = creer_station()
    station_service.get_history_by_period.return_value = [creer_status(), creer_status(6)]

    # WHEN
    res = client.get("/stations/ST001/history")

    # THEN
    assert res.status_code == 200
    assert len(res.json()) == 2
    station_service.get_history_by_period.assert_called_once_with("ST001", "24h")


def test_station_history_periode_7j(client, station_service):
    """History over 7 days"""

    # GIVEN
    station_service.get_station.return_value = creer_station()
    station_service.get_history_by_period.return_value = []

    # WHEN
    res = client.get("/stations/ST001/history", params={"period": "7j"})

    # THEN
    assert res.status_code == 200
    assert res.json() == []
    station_service.get_history_by_period.assert_called_once_with("ST001", "7j")


def test_station_history_periode_invalide(client, station_service):
    """An invalid period returns 422"""

    # WHEN
    res = client.get("/stations/ST001/history", params={"period": "1h"})

    # THEN
    assert res.status_code == 422
    station_service.get_history_by_period.assert_not_called()


def test_station_history_station_inexistante(client, station_service):
    """History of an unknown station returns 404"""

    # GIVEN
    station_service.get_station.return_value = None

    # WHEN
    res = client.get("/stations/N_EXISTE_PAS/history")

    # THEN
    assert res.status_code == 404
    station_service.get_history_by_period.assert_not_called()



def test_delete_station_ok(client, station_service):
    """Successfully delete a station"""

    # GIVEN
    station = creer_station()
    station_service.get_station.return_value = station
    station_service.delete.return_value = True

    # WHEN
    res = client.delete("/stations/ST001")

    # THEN
    assert res.status_code == 200
    assert res.json() == "Station Place Pey Berland deleted"
    station_service.delete.assert_called_once_with(station)


def test_delete_station_inexistante(client, station_service):
    """Deleting an unknown station returns 404"""

    # GIVEN
    station_service.get_station.return_value = None

    # WHEN
    res = client.delete("/stations/N_EXISTE_PAS")

    # THEN
    assert res.status_code == 404
    station_service.delete.assert_not_called()


def test_delete_station_echec(client, station_service):
    """A failed deletion returns 500"""

    # GIVEN
    station_service.get_station.return_value = creer_station()
    station_service.delete.return_value = False

    # WHEN
    res = client.delete("/stations/ST001")

    # THEN
    assert res.status_code == 500


def test_delete_station_non_authentifie(app, client, station_service):
    """Deleting without being authenticated returns 401"""

    # GIVEN
    def refuser():
        raise HTTPException(status_code=401, detail="Not authenticated")

    app.dependency_overrides[verify_token] = refuser

    # WHEN
    res = client.delete("/stations/ST001")

    # THEN
    assert res.status_code == 401
    station_service.delete.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__])