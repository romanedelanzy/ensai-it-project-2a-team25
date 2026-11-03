from dataclasses import replace
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from business_object.station import Station
from business_object.stationstatus import StationStatus
from service.station_service import PERIODS, StationService


def creer_station(station_id="ST001", name="Place Pey Berland", capacite=20):
    return Station(station_id, 1, name, 44.8378, -0.5792, capacite)


def creer_status(**champs):
    status = StationStatus(
        id_station="ST001",
        horodatage=datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc),
        nb_velos_dispos=5,
        nb_velos_elec_dispos=1,
        nb_places_dispos=15,
        est_installee=True,
        permet_retour=True,
        permet_emprunt=True,
    )
    return replace(status, **champs)


def test_get_station_ok():
    dao = MagicMock()
    station = creer_station()
    dao.find_by_id.return_value = station

    resultat = StationService(station_dao=dao).get_station("ST001")

    assert resultat == station
    dao.find_by_id.assert_called_once_with("ST001")

def test_get_station_inconnue():
    dao = MagicMock()
    dao.find_by_id.return_value = None

    resultat = StationService(station_dao=dao).get_station("INCONNUE")

    assert resultat is None
    dao.find_by_id.assert_called_once_with("INCONNUE")


def test_list_all():
    dao = MagicMock()
    stations = [creer_station("ST001"), creer_station("ST002", name="Quinconces")]
    dao.list_all.return_value = stations

    resultat = StationService(station_dao=dao).list_all()

    assert resultat == stations
    assert len(resultat) == 2
    dao.list_all.assert_called_once_with()

def test_list_all_vide():
    dao = MagicMock()
    dao.list_all.return_value = []

    resultat = StationService(station_dao=dao).list_all()

    assert resultat == []


def test_delete_ok():
    dao = MagicMock()
    dao.delete.return_value = True
    station = creer_station()
 
    resultat = StationService(station_dao=dao).delete(station)
 
    assert resultat is True
    dao.delete.assert_called_once_with(station)
 
def test_delete_echec():
    dao = MagicMock()
    dao.delete.return_value = False
    station = creer_station()
 
    resultat = StationService(station_dao=dao).delete(station)
 
    assert resultat is False
    dao.delete.assert_called_once_with(station)





def test_get_current_status_ok():
    dao = MagicMock()
    status = creer_status()
    dao.find_current_status.return_value = status

    resultat = StationService(station_status_dao=dao).get_current_status("ST001")

    assert resultat == status
    dao.find_current_status.assert_called_once_with("ST001")

def test_get_current_status_inconnu():
    dao = MagicMock()
    dao.find_current_status.return_value = None

    resultat = StationService(station_status_dao=dao).get_current_status("ST001")

    assert resultat is None


def test_get_history():
    dao = MagicMock()
    statuts = [creer_status(), creer_status(nb_velos_dispos=6)]
    dao.find_history.return_value = statuts
    debut = datetime(2026, 10, 1, tzinfo=timezone.utc)
    fin = datetime(2026, 10, 2, tzinfo=timezone.utc)

    resultat = StationService(station_status_dao=dao).get_history("ST001", debut, fin)

    assert resultat == statuts
    dao.find_history.assert_called_once_with("ST001", debut, fin)

def test_get_history_liste_vide():
    dao = MagicMock()
    dao.find_history.return_value = []
    debut = datetime(2026, 10, 1, tzinfo=timezone.utc)
    fin = datetime(2026, 10, 2, tzinfo=timezone.utc)

    resultat = StationService(station_status_dao=dao).get_history("ST001", debut, fin)

    assert resultat == []


def test_search_by_name_trouve_sans_tenir_compte_de_la_casse():
    dao = MagicMock()
    station = creer_station()
    dao.list_all.return_value = [station, creer_station("ST002", name="Quinconces")]

    assert StationService(station_dao=dao).search_by_name("pey") == [station]
    assert StationService(station_dao=dao).search_by_name("BERLAND") == [station]

def test_search_by_name_moins_de_3_caracteres():
    dao = MagicMock()

    resultat = StationService(station_dao=dao).search_by_name("pe")

    assert resultat == []
    dao.list_all.assert_not_called()

def test_search_by_name_aucun_resultat():
    dao = MagicMock()
    dao.list_all.return_value = [creer_station()]

    resultat = StationService(station_dao=dao).search_by_name("quinconces")

    assert resultat == []


def test_is_operational_ok():
    dao = MagicMock()
    dao.find_current_status.return_value = creer_status()

    resultat = StationService(station_status_dao=dao).is_operational("ST001")

    assert resultat is True
    dao.find_current_status.assert_called_once_with("ST001")

@pytest.mark.parametrize("champ", ["est_installee", "permet_emprunt", "permet_retour"])
def test_is_operational_faux_si_un_champ_est_faux(champ):
    dao = MagicMock()
    dao.find_current_status.return_value = creer_status(**{champ: False})

    resultat = StationService(station_status_dao=dao).is_operational("ST001")

    assert resultat is False

def test_is_operational_faux_sans_statut():
    dao = MagicMock()
    dao.find_current_status.return_value = None

    resultat = StationService(station_status_dao=dao).is_operational("ST001")

    assert resultat is False


def test_get_fill_rate_ok():
    station_dao = MagicMock()
    status_dao = MagicMock()
    station_dao.find_by_id.return_value = creer_station(capacite=20)
    status_dao.find_current_status.return_value = creer_status(nb_velos_dispos=5)

    resultat = StationService(station_dao=station_dao, station_status_dao=status_dao).get_fill_rate("ST001")

    assert resultat == 0.25  # 5 vélos / 20 places
    station_dao.find_by_id.assert_called_once_with("ST001")
    status_dao.find_current_status.assert_called_once_with("ST001")

def test_get_fill_rate_station_inconnue():
    station_dao = MagicMock()
    status_dao = MagicMock()
    station_dao.find_by_id.return_value = None
    status_dao.find_current_status.return_value = creer_status()

    resultat = StationService(station_dao=station_dao, station_status_dao=status_dao).get_fill_rate("ST001")

    assert resultat is None

def test_get_fill_rate_sans_statut():
    station_dao = MagicMock()
    status_dao = MagicMock()
    station_dao.find_by_id.return_value = creer_station()
    status_dao.find_current_status.return_value = None

    resultat = StationService(station_dao=station_dao, station_status_dao=status_dao).get_fill_rate("ST001")

    assert resultat is None

def test_get_fill_rate_capacite_nulle():
    station_dao = MagicMock()
    status_dao = MagicMock()
    station_dao.find_by_id.return_value = creer_station(capacite=0)
    status_dao.find_current_status.return_value = creer_status()

    resultat = StationService(station_dao=station_dao, station_status_dao=status_dao).get_fill_rate("ST001")

    assert resultat is None


@pytest.mark.parametrize("period", ["24h", "7j", "30j"])
def test_get_history_by_period(period):
    dao = MagicMock()
    statuts = [creer_status()]
    dao.find_history.return_value = statuts
    avant = datetime.now(timezone.utc)

    resultat = StationService(station_status_dao=dao).get_history_by_period("ST001", period)

    apres = datetime.now(timezone.utc)
    station_id, debut, fin = dao.find_history.call_args.args
    assert resultat == statuts
    assert station_id == "ST001"
    assert avant <= fin <= apres
    assert fin - debut == PERIODS[period]

def test_get_history_by_period_par_defaut_24h():
    dao = MagicMock()
    dao.find_history.return_value = []

    StationService(station_status_dao=dao).get_history_by_period("ST001")

    _, debut, fin = dao.find_history.call_args.args
    assert fin - debut == PERIODS["24h"]

def test_get_history_by_period_invalide():
    dao = MagicMock()

    with pytest.raises(ValueError):
        StationService(station_status_dao=dao).get_history_by_period("ST001", "1h")

    dao.find_history.assert_not_called()