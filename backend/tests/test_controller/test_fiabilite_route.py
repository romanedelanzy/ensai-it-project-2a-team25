from datetime import datetime
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from controller.fiabilite_controller import (
    router,
    get_reliability_service
)


def test_get_station_reliability_http():

    # Arrange : création du faux service
    service = MagicMock()

    date1 = datetime(2026, 1, 1, 8, 0)
    date2 = datetime(2026, 1, 1, 9, 0)

    service.reliability_current_score.return_value = 0.85
    service.reliability_score_evolution.return_value = {
        date1: 0.72,
        date2: 0.85
    }
    service.percent_time_empty_all.return_value = 0.15
    service.percent_saturation_all.return_value = 0.10
    service.average_empty_duration_all.return_value = 1.5
    service.average_saturated_duration_all.return_value = 0.8

    # Création d'une application FastAPI de test
    app = FastAPI()
    app.include_router(router, prefix="/reliability")

    # Remplacement de la dépendance par notre faux service
    app.dependency_overrides[get_reliability_service] = lambda: service

    client = TestClient(app)

    # Act : envoi d'une véritable requête HTTP
    response = client.get("/reliability/station_1")

    # Assert : vérification du statut HTTP
    assert response.status_code == 200

    # Vérification du contenu JSON
    data = response.json()

    assert data["station_id"] == "station_1"
    assert data["current_score"] == 0.85
    assert data["empty_percentage"] == 0.15
    assert data["saturation_percentage"] == 0.10
    assert data["average_empty_duration"] == 1.5
    assert data["average_saturated_duration"] == 0.8

    assert len(data["score_evolution"]) == 2
    assert data["score_evolution"][0]["date"] == "2026-01-01T08:00:00"
    assert data["score_evolution"][0]["score"] == 0.72
    assert data["score_evolution"][1]["date"] == "2026-01-01T09:00:00"
    assert data["score_evolution"][1]["score"] == 0.85