
from unittest.mock import MagicMock

from business_object.favoris import Favori
from service.favori_service import FavoriService


def test_ajouter_favori_ok():
    dao = MagicMock()
    dao.add_favorite.return_value = True
    service = FavoriService(favori_dao=dao)

    resultat = service.ajouter_favori(1, "station_1")

    assert resultat is True
    dao.add_favorite.assert_called_once_with(1, "station_1")


def test_ajouter_favori_echec():
    dao = MagicMock()
    dao.add_favorite.return_value = False
    service = FavoriService(favori_dao=dao)

    resultat = service.ajouter_favori(1, "station_1")

    assert resultat is False
    dao.add_favorite.assert_called_once_with(1, "station_1")


def test_supprimer_favori_ok():
    dao = MagicMock()
    dao.remove_favorite.return_value = True
    service = FavoriService(favori_dao=dao)

    resultat = service.supprimer_favori(1, "station_1")

    assert resultat is True
    dao.remove_favorite.assert_called_once_with(1, "station_1")


def test_supprimer_favori_echec():
    dao = MagicMock()
    dao.remove_favorite.return_value = False
    service = FavoriService(favori_dao=dao)

    resultat = service.supprimer_favori(1, "station_1")

    assert resultat is False
    dao.remove_favorite.assert_called_once_with(1, "station_1")


def test_recuperer_favoris_par_joueur():
    dao = MagicMock()
    favoris_attendus = [
        Favori(
            station_id="station_1",
            utilisateur_id=1,
            cree_a=None,
        ),
        Favori(
            station_id="station_2",
            utilisateur_id=1,
            cree_a=None,
        ),
    ]
    dao.user_favorite.return_value = favoris_attendus
    service = FavoriService(favori_dao=dao)

    resultat = service.recuperer_favoris_par_joueur(1)

    assert resultat == favoris_attendus
    assert len(resultat) == 2
    dao.user_favorite.assert_called_once_with(1)


def test_recuperer_favoris_liste_vide():
    dao = MagicMock()
    dao.user_favorite.return_value = []
    service = FavoriService(favori_dao=dao)

    resultat = service.recuperer_favoris_par_joueur(1)

    assert resultat == []
    dao.user_favorite.assert_called_once_with(1)
