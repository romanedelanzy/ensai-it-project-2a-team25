from datetime import datetime
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from psycopg2 import errors

from business_object.favoris import Favori
from controller.favori_controller import (
    add_favorite,
    add_favorite_by_name,
    get_favori_service,
    get_station_service,
    get_user_favorite,
    remove_favorite,
    router,
)
from schema.favori_model import FavoriReadModel
from utils.security import get_current_user

# Les fonctions du contrôleur sont appelées directement, avec un faux service et un faux
# utilisateur connecté passés en paramètres à la place des Depends : aucune base de données
# n'est utilisée. Le user_id n'est plus dans l'URL : il vient du token (current_user).


def fake_user(user_id: int = 1):
    """Faux utilisateur connecté, comme renvoyé par get_current_user."""
    user = MagicMock()
    user.user_id = user_id
    return user


# ---------- routes ----------


def test_routes_declarees():
    """The router exposes the three expected routes (no user_id in the URL anymore)"""

    # WHEN
    routes = {(route.path, method) for route in router.routes for method in route.methods}

    # THEN
    assert ("/", "GET") in routes
    assert ("/{station_id}", "POST") in routes
    assert ("/{station_id}", "DELETE") in routes
    assert ("/nom/{station_name}", "POST") in routes


# ---------- get_user_favorite ----------


def test_get_user_favorite_ok():
    """List the favorites of the connected user"""

    # GIVEN
    date = datetime(2026, 10, 27, 13, 0)
    service = MagicMock()
    service.recuperer_favoris_par_joueur.return_value = [
        Favori("TEST_001", 1, date),
        Favori("TEST_002", 1, date),
    ]

    # WHEN
    res = get_user_favorite(favori_service=service, current_user=fake_user(1))

    # THEN
    service.recuperer_favoris_par_joueur.assert_called_once_with(1)
    assert len(res) == 2
    assert all(isinstance(f, FavoriReadModel) for f in res)
    assert [f.station_id for f in res] == ["TEST_001", "TEST_002"]
    assert res[0].user_id == 1
    assert res[0].create_at == date


def test_get_user_favorite_empty():
    """A user without favorites gets an empty list"""

    # GIVEN
    service = MagicMock()
    service.recuperer_favoris_par_joueur.return_value = []

    # WHEN
    res = get_user_favorite(favori_service=service, current_user=fake_user(3))

    # THEN
    service.recuperer_favoris_par_joueur.assert_called_once_with(3)
    assert res == []


# ---------- add_favorite ----------


def test_add_favorite_ok():
    """Successfully add a favorite for the connected user"""

    # GIVEN
    service = MagicMock()
    service.ajouter_favori.return_value = True

    # WHEN
    res = add_favorite("TEST_001", favori_service=service, current_user=fake_user(1))

    # THEN
    service.ajouter_favori.assert_called_once_with(1, "TEST_001")
    assert "TEST_001" in res["message"]


def test_add_favorite_doublon():
    """409 when the station is already one of the user's favorites"""

    # GIVEN
    service = MagicMock()
    service.ajouter_favori.side_effect = errors.UniqueViolation("doublon")

    # WHEN / THEN
    with pytest.raises(HTTPException) as exc:
        add_favorite("TEST_001", favori_service=service, current_user=fake_user(1))

    assert exc.value.status_code == 409


def test_add_favorite_station_ou_utilisateur_inexistant():
    """404 when the user or the station does not exist"""

    # GIVEN
    service = MagicMock()
    service.ajouter_favori.side_effect = errors.ForeignKeyViolation("inexistant")

    # WHEN / THEN
    with pytest.raises(HTTPException) as exc:
        add_favorite("N_EXISTE_PAS", favori_service=service, current_user=fake_user(1))

    assert exc.value.status_code == 404


def test_add_favorite_fail():
    """500 when the service reports that nothing was added"""

    # GIVEN
    service = MagicMock()
    service.ajouter_favori.return_value = False

    # WHEN / THEN
    with pytest.raises(HTTPException) as exc:
        add_favorite("TEST_001", favori_service=service, current_user=fake_user(1))

    assert exc.value.status_code == 500


# ---------- add_favorite_by_name ----------


def fake_station(station_id: str, name: str):
    """Fausse station renvoyée par StationService.search_by_name."""
    station = MagicMock()
    station.station_id = station_id
    station.name = name
    return station


def test_add_favorite_by_name_ok():
    """Add a favorite from the exact name of the station"""

    # GIVEN
    favori_service = MagicMock()
    favori_service.ajouter_favori.return_value = True
    station_service = MagicMock()
    station_service.search_by_name.return_value = [fake_station("8", "Patinoire")]

    # WHEN
    res = add_favorite_by_name(
        "Patinoire",
        favori_service=favori_service,
        station_service=station_service,
        current_user=fake_user(3),
    )

    # THEN
    favori_service.ajouter_favori.assert_called_once_with(3, "8")
    assert "8" in res["message"]


def test_add_favorite_by_name_ignore_casse_et_espaces():
    """Case and surrounding spaces are ignored (the real data has 'Grand Lebrun ')"""

    # GIVEN
    favori_service = MagicMock()
    favori_service.ajouter_favori.return_value = True
    station_service = MagicMock()
    station_service.search_by_name.return_value = [
        fake_station("12", "Grand Lebrun "),
        fake_station("13", "Grand Lebrun Nord"),
    ]

    # WHEN
    add_favorite_by_name(
        "  grand lebrun",
        favori_service=favori_service,
        station_service=station_service,
        current_user=fake_user(3),
    )

    # THEN : la correspondance exacte l'emporte sur la correspondance partielle
    favori_service.ajouter_favori.assert_called_once_with(3, "12")


def test_add_favorite_by_name_partiel_unique():
    """A partial name is accepted when it identifies a single station"""

    # GIVEN
    favori_service = MagicMock()
    favori_service.ajouter_favori.return_value = True
    station_service = MagicMock()
    station_service.search_by_name.return_value = [fake_station("8", "Patinoire")]

    # WHEN
    add_favorite_by_name(
        "Patin",
        favori_service=favori_service,
        station_service=station_service,
        current_user=fake_user(3),
    )

    # THEN
    favori_service.ajouter_favori.assert_called_once_with(3, "8")


def test_add_favorite_by_name_introuvable():
    """404 when no station matches the name"""

    # GIVEN
    favori_service = MagicMock()
    station_service = MagicMock()
    station_service.search_by_name.return_value = []

    # WHEN / THEN
    with pytest.raises(HTTPException) as exc:
        add_favorite_by_name(
            "Inconnue",
            favori_service=favori_service,
            station_service=station_service,
            current_user=fake_user(3),
        )

    assert exc.value.status_code == 404
    favori_service.ajouter_favori.assert_not_called()


def test_add_favorite_by_name_ambigu():
    """400 when several stations match and none is an exact match"""

    # GIVEN
    favori_service = MagicMock()
    station_service = MagicMock()
    station_service.search_by_name.return_value = [
        fake_station("1", "Gare Nord"),
        fake_station("2", "Gare Sud"),
    ]

    # WHEN / THEN
    with pytest.raises(HTTPException) as exc:
        add_favorite_by_name(
            "Gare",
            favori_service=favori_service,
            station_service=station_service,
            current_user=fake_user(3),
        )

    assert exc.value.status_code == 400
    assert "Gare Nord" in exc.value.detail and "Gare Sud" in exc.value.detail
    favori_service.ajouter_favori.assert_not_called()


def test_add_favorite_by_name_doublon():
    """409 when the station is already one of the user's favorites"""

    # GIVEN
    favori_service = MagicMock()
    favori_service.ajouter_favori.side_effect = errors.UniqueViolation("doublon")
    station_service = MagicMock()
    station_service.search_by_name.return_value = [fake_station("8", "Patinoire")]

    # WHEN / THEN
    with pytest.raises(HTTPException) as exc:
        add_favorite_by_name(
            "Patinoire",
            favori_service=favori_service,
            station_service=station_service,
            current_user=fake_user(3),
        )

    assert exc.value.status_code == 409


# ---------- remove_favorite ----------


def test_remove_favorite_ok():
    """Successfully remove a favorite of the connected user"""

    # GIVEN
    service = MagicMock()
    service.supprimer_favori.return_value = True

    # WHEN
    res = remove_favorite("TEST_001", favori_service=service, current_user=fake_user(1))

    # THEN
    service.supprimer_favori.assert_called_once_with(1, "TEST_001")
    assert "TEST_001" in res["message"]


def test_remove_favorite_inexistant():
    """404 when the favorite does not exist"""

    # GIVEN
    service = MagicMock()
    service.supprimer_favori.return_value = False

    # WHEN / THEN
    with pytest.raises(HTTPException) as exc:
        remove_favorite("TEST_001", favori_service=service, current_user=fake_user(1))

    assert exc.value.status_code == 404


# ---------- sécurité (appels HTTP complets) ----------


@pytest.fixture
def client_and_service():
    """App FastAPI de test : vrai routeur, faux service, authentification simulée."""
    app = FastAPI()
    app.include_router(router, prefix="/favoris")
    service = MagicMock()
    app.dependency_overrides[get_favori_service] = lambda: service
    return TestClient(app), app, service


@pytest.mark.parametrize(
    "method, url",
    [
        ("get", "/favoris/"),
        ("post", "/favoris/TEST_001"),
        ("post", "/favoris/nom/Patinoire"),
        ("delete", "/favoris/TEST_001"),
    ],
)
def test_routes_exigent_un_token(client_and_service, method, url):
    """Without X-Auth-Token header, every route is refused"""

    # GIVEN
    client, _, service = client_and_service

    # WHEN
    res = getattr(client, method)(url)

    # THEN
    assert res.status_code in (401, 403)
    service.recuperer_favoris_par_joueur.assert_not_called()
    service.ajouter_favori.assert_not_called()
    service.supprimer_favori.assert_not_called()


def test_chacun_agit_uniquement_sur_ses_propres_favoris(client_and_service):
    """The user id used by the service is the one of the token, never one sent by the client"""

    # GIVEN : l'utilisateur 7 est connecté
    client, app, service = client_and_service
    app.dependency_overrides[get_current_user] = lambda: fake_user(7)
    service.ajouter_favori.return_value = True
    service.supprimer_favori.return_value = True

    # WHEN
    client.post("/favoris/TEST_001")
    client.delete("/favoris/TEST_001")

    # THEN : toujours l'id 7
    service.ajouter_favori.assert_called_once_with(7, "TEST_001")
    service.supprimer_favori.assert_called_once_with(7, "TEST_001")


def test_ajout_par_nom_utilise_le_user_du_token(client_and_service):
    """Adding by name goes through the full route and uses the user id of the token"""

    # GIVEN : l'utilisateur 7 est connecté
    client, app, service = client_and_service
    app.dependency_overrides[get_current_user] = lambda: fake_user(7)
    station_service = MagicMock()
    station_service.search_by_name.return_value = [fake_station("8", "Patinoire")]
    app.dependency_overrides[get_station_service] = lambda: station_service
    service.ajouter_favori.return_value = True

    # WHEN
    res = client.post("/favoris/nom/Patinoire")

    # THEN
    assert res.status_code == 201
    service.ajouter_favori.assert_called_once_with(7, "8")


def test_ancienne_route_avec_user_id_n_existe_plus(client_and_service):
    """DELETE /favoris/{user_id}/{station_id} (old, unprotected route) is gone"""

    # GIVEN
    client, app, service = client_and_service
    app.dependency_overrides[get_current_user] = lambda: fake_user(7)

    # WHEN
    res = client.delete("/favoris/42/TEST_001")

    # THEN
    assert res.status_code in (404, 405)
    service.supprimer_favori.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__])