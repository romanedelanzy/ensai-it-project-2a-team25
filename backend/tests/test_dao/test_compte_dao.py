import os
from unittest.mock import patch

import psycopg2
import pytest

from business_object.compte import Compte
from dao.CompteDAO import CompteDAO
from utils.reset_database import ResetDatabase
from utils.security import hash_password


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialise la base de données de test une seule fois pour la session."""
    with patch.dict(os.environ, {"SCHEMA": "project_test_dao"}):
        ResetDatabase().run(test_dao=True)
        yield


def test_find_by_id_existing():
    """Trouve un compte par un ID existant"""
    # GIVEN
    user_id = 2  # ID présent dans la base de test initiale

    # WHEN
    compte = CompteDAO().find_by_id(user_id)

    # THEN
    assert compte is not None
    assert compte.user_id == user_id


def test_find_by_id_non_existing():
    """Échoue à trouver un compte avec un ID inexistant"""
    # GIVEN
    user_id = 999999999

    # WHEN
    compte = CompteDAO().find_by_id(user_id)

    # THEN
    assert compte is None


def test_find_by_username_existing():
    """Trouve un compte par son username"""
    # GIVEN
    username = "username2"

    # WHEN
    compte = CompteDAO().find_by_username(username)

    # THEN
    assert compte is not None
    assert compte.username == username


def test_find_all():
    """Vérifie que list_all retourne une liste de comptes"""
    # WHEN
    comptes = CompteDAO().list_all()

    # THEN
    assert isinstance(comptes, list)
    for c in comptes:
        assert isinstance(c, Compte)
    assert len(comptes) >= 2


def test_create_ok():
    """Crée un compte avec succès"""
    # GIVEN
    nouveau_compte = Compte(
        username="test_pytest_user",
        is_admin=False,
        password="password_secure",
        email="pytest@email.fr"
    )

    # WHEN
    id_genere = CompteDAO().create(nouveau_compte)

    # THEN
    assert id_genere is not None
    assert nouveau_compte.user_id is not None


def test_create_ko():
    """Échoue à créer un compte avec des types invalides (ex: is_admin non booléen)"""
    # GIVEN
    with pytest.raises(TypeError):
        Compte(
            username="fail_user",
            is_admin="not_a_bool",
            password="password",
            email="fail@email.fr"
        )


def test_update_ok():
    """Met à jour un compte existant avec succès."""
    # GIVEN
    compte = CompteDAO().find_by_id(3)
    assert compte is not None
    compte.username = "username3_updated"

    # WHEN
    update_ok = CompteDAO().update(compte)

    # THEN
    assert update_ok
    compte_verif = CompteDAO().find_by_id(3)
    assert compte_verif.username == "username3_updated"


def test_update_ko():
    """Échoue à mettre à jour un compte avec un ID inexistant."""
    # GIVEN
    compte = Compte(
        user_id=88888,
        username="ghost",
        is_admin=False,
        password="pwd",
        email="ghost@email.fr"
    )

    # WHEN
    update_ok = CompteDAO().update(compte)

    # THEN
    assert not update_ok


def test_delete_ok():
    """Supprime un compte existant avec succès."""
    # GIVEN - On crée un compte dédié à la suppression
    compte_a_supprimer = Compte(
        username="to_delete",
        is_admin=False,
        password="pwd",
        email="delete@email.fr"
    )
    user_id = CompteDAO().create(compte_a_supprimer)

    # WHEN
    delete_ok = CompteDAO().delete(user_id)

    # THEN
    assert delete_ok
    assert CompteDAO().find_by_id(user_id) is None


def test_delete_ko():
    """Échoue à supprimer un compte avec un ID inexistant."""
    # WHEN
    delete_ok = CompteDAO().delete(999999)

    # THEN
    assert not delete_ok


def test_login_ok():
    """Connecte un utilisateur avec succès."""

    # GIVEN
    username = "username1"
    password = "password1"

    # WHEN
    compte = CompteDAO().login(username, password)

    # THEN
    assert isinstance(compte, Compte)



def test_find_by_token():
    """Recherche un compte via son access_token."""
    # GIVEN
    compte = CompteDAO().find_by_id(2)
    compte.access_token = "token"
    CompteDAO().update(compte)

    # WHEN
    trouve_par_token = CompteDAO().find_by_token("token")

    # THEN
    assert trouve_par_token is not None
    assert trouve_par_token.user_id == compte.user_id


if __name__ == "__main__":
    pytest.main([__file__])