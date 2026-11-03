from unittest.mock import MagicMock
from business_object.compte import Compte
from dao.CompteDAO import CompteDAO
from service.compte_service import CompteService

compte_list = [
    Compte(username="username1", email="username1@mail.fr", password="1234", is_admin=False),
    Compte(username="username2", email="username2@mail.fr", password="0000", is_admin=True),
    Compte(username="username3", email="username2@mail.fr", password="abcd", is_admin=False),
]

def test_create_account_ok():
    """Vérifie la création réussie d'un compte utilisateur."""

    # GIVEN
    username, password, is_admin, email = "username1", "mdp1", False, "username1@gmail.fr"
    CompteDAO().create = MagicMock(return_value=True)

    # WHEN
    compte = CompteService().create_account(username, password, is_admin, email)

    # THEN
    assert compte is not None
    assert compte.username == username
    assert compte.email == email
    assert compte.is_admin == is_admin

def test_create_account_fail():
    """Échec de la création d'un compte car CompteDAO().create renvoie False."""

    # GIVEN
    username, password, is_admin, email = "fanny", "mon_mdp", False, "fanny@mail.fr"
    # On simule le DAO pour qu'il renvoie False (échec de l'insertion en base)
    CompteDAO().create = MagicMock(return_value=False)

    # WHEN
    compte = CompteService().create_account(username, password, is_admin, email)

    # THEN
    assert compte is None

def test_list_account():
    """Récupère la liste de tous les comptes"""

    # GIVEN
    CompteDAO().list_all = MagicMock(return_value=compte_list)

    # WHEN
    res = CompteService().list_account()

    # THEN
    assert len(res) == 3
    assert res == compte_list

def test_username_already_used_yes():
    """Le nom d'utilisateur est déjà utilisé dans compte_list"""

    # GIVEN
    username = "username1"

    # WHEN
    CompteDAO().list_all = MagicMock(return_value=compte_list)
    res = CompteService().username_already_used(username)

    # THEN
    assert res

def test_username_already_used_no():
    """Le nom d'utilisateur n'est pas encore utilisé dans compte_list"""

    # GIVEN
    username = "kitten"

    # WHEN
    CompteDAO().find_all = MagicMock(return_value=compte_list)
    res = CompteService().username_already_used(username)

    # THEN
    assert not res

def test_find_by_id_ok():
    """Trouve un compte avec succès par son ID"""
    # GIVEN
    compte_test = Compte(user_id=1, username="username1", email="mail@mail.fr", password="123", is_admin=False)
    CompteDAO().find_by_id = MagicMock(return_value=compte_test)

    # WHEN
    res = CompteService().find_by_id(1)

    # THEN
    assert res is not None
    assert res.user_id == 1
    assert res.username == "username1"

def test_login_ok():
    """Connexion réussie avec des identifiants valides"""
    # GIVEN
    username = "username1"
    raw_password = "1234"
    compte_test = Compte(user_id=1, username=username, email="mail@mail.fr", password="hash_valide", is_admin=False)
    # On simule le DAO pour login et update
    CompteDAO().login = MagicMock(return_value=compte_test)
    CompteDAO().update = MagicMock(return_value=True)

    # WHEN
    res = CompteService().login(username, raw_password)

    # THEN
    assert res is not None
    assert res.username == username
    assert res.access_token is not None  # Vérifie que le token a bien été généré

def test_login_fail():
    """Échec de la connexion avec de mauvais identifiants"""
    # GIVEN
    CompteDAO().login = MagicMock(return_value=None)

    # WHEN
    res = CompteService().login("inconnu", "mauvais_mdp")

    # THEN
    assert res is None

def test_update_account():
    """Mise à jour réussie d'un compte"""
    # GIVEN
    compte_test = Compte(user_id=1, username="username1", email="nouveau@mail.fr", password="123", is_admin=False)
    CompteDAO().update = MagicMock(return_value=True)

    # WHEN
    res = CompteService().update(compte_test)

    # THEN
    assert res is not None
    assert res.email == "nouveau@mail.fr"

def test_delete_account():
    """Suppression réussie d'un compte"""
    # GIVEN
    compte_test = Compte(user_id=1, username="username1", email="mail@mail.fr", password="123", is_admin=False)
    CompteDAO().delete = MagicMock(return_value=True)

    # WHEN
    res = CompteService().delete(compte_test)

    # THEN
    assert res is True
if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
