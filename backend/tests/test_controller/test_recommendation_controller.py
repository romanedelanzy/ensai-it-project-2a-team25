from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from business_object.station import Station
from controller import recommendation_controller
from controller.recommendation_controller import get_recommendation_service, router


def test_get_recommendations_http():
    service = MagicMock()
    service.recommander_stations.return_value = [
        {
            "station": Station("39", 1, "Quinconces", 44.84423, -0.57434, 63),
            "distance_km": 0.125,
            "score_fiabilite": 0.9,
            "score_recommandation": 0.85,
        }
    ]

    app = FastAPI()
    app.include_router(router, prefix="/recommendation")
    app.dependency_overrides[get_recommendation_service] = lambda: service
    client = TestClient(app)

    response = client.get(
        "/recommendation/",
        params={"latitude": 44.84, "longitude": -0.58, "limite": 3, "rayon_km": 2},
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "station": {
                "station_id": "39",
                "reseau_id": 1,
                "name": "Quinconces",
                "adresse": None,
                "latitude": 44.84423,
                "longitude": -0.57434,
                "capacite": 63,
            },
            "distance_km": 0.125,
            "score_fiabilite": 0.9,
            "score_recommandation": 0.85,
        }
    ]
    service.recommander_stations.assert_called_once_with(
        latitude=44.84,
        longitude=-0.58,
        limite=3,
        rayon_km=2,
    )


def test_get_recommendations_accepts_bordeaux_address():
    service = MagicMock()
    service.recommander_stations.return_value = []

    app = FastAPI()
    app.include_router(router, prefix="/recommendation")
    app.dependency_overrides[get_recommendation_service] = lambda: service
    client = TestClient(app)

    recommendation_controller.geocode_bordeaux_address = MagicMock(
        return_value=(44.84423, -0.57434)
    )

    response = client.get(
        "/recommendation/",
        params={"address": "Place Quinconces", "limite": 3},
    )

    assert response.status_code == 200
    service.recommander_stations.assert_called_once_with(
        latitude=44.84423,
        longitude=-0.57434,
        limite=3,
        rayon_km=None,
    )


def test_get_recommendations_rejects_invalid_coordinates():
    app = FastAPI()
    app.include_router(router, prefix="/recommendation")
    app.dependency_overrides[get_recommendation_service] = MagicMock
    client = TestClient(app)

    response = client.get(
        "/recommendation/",
        params={"latitude": 91, "longitude": -0.58},
    )

    assert response.status_code == 422
