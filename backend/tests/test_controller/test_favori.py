from datetime import datetime
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from psycopg2 import errors

from business_object.favoris import Favori
from controller.FavoriController import (
    add_favorite,
    get_user_favorite,
    remove_favorite,
    router,
)
from schema.favori_model import FavoriReadModel

# Les fonctions du contrôleur sont appelées directement, avec un faux service passé en
# paramètre à la place de Depends(get_favori_service) : aucune base de données n'est utilisée.


# ---------- routes ----------


def test_routes_declarees():
    """The router exposes the three expected routes"""

    # WHEN
    routes = {(route.path, method) for route in router.routes for method in route.methods}

    # THEN
    assert ("/{user_id}", "GET") in routes
    assert ("/{user_id}/{station_id}", "POST") in routes
    assert ("/{user_id}/{station_id}", "DELETE") in routes


# ---------- get_user_favorite ----------


def test_get_user_favorite_ok():
    """List the favorites of a user"""

    # GIVEN
    date = datetime(2026, 10, 27, 13, 0)
    service = MagicMock()
    service.recuperer_favoris_par_joueur.return_value = [
        Favori("TEST_001", 1, date),
        Favori("TEST_002", 1, date),
    ]

    # WHEN
    res = get_user_favorite(1, favori_service=service)

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
    res = get_user_favorite(3, favori_service=service)

    # THEN
    assert res == []


# ---------- add_favorite ----------


def test_add_favorite_ok():
    """Successfully add a favorite"""

    # GIVEN
    service = MagicMock()
    service.ajouter_favori.return_value = True

    # WHEN
    res = add_favorite(1, "TEST_001", favori_service=service)

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
        add_favorite(1, "TEST_001", favori_service=service)

    assert exc.value.status_code == 409


def test_add_favorite_station_ou_utilisateur_inexistant():
    """404 when the user or the station does not exist"""

    # GIVEN
    service = MagicMock()
    service.ajouter_favori.side_effect = errors.ForeignKeyViolation("inexistant")

    # WHEN / THEN
    with pytest.raises(HTTPException) as exc:
        add_favorite(1, "N_EXISTE_PAS", favori_service=service)

    assert exc.value.status_code == 404


def test_add_favorite_fail():
    """500 when the service reports that nothing was added"""

    # GIVEN
    service = MagicMock()
    service.ajouter_favori.return_value = False

    # WHEN / THEN
    with pytest.raises(HTTPException) as exc:
        add_favorite(1, "TEST_001", favori_service=service)

    assert exc.value.status_code == 500


# ---------- remove_favorite ----------


def test_remove_favorite_ok():
    """Successfully remove a favorite"""

    # GIVEN
    service = MagicMock()
    service.supprimer_favori.return_value = True

    # WHEN
    res = remove_favorite(1, "TEST_001", favori_service=service)

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
        remove_favorite(1, "TEST_001", favori_service=service)

    assert exc.value.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__])