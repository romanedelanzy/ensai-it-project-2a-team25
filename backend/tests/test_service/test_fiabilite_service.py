
from datetime import datetime, timedelta
from unittest.mock import patch

from business_object.stationstatus import StationStatus
from service.fiabilite_service import ReliabilityService


def create_normal_status(date):
    return StationStatus(
        id_station="station_1",
        horodatage=date,
        nb_velos_dispos=5,
        nb_velos_elec_dispos=2,
        nb_places_dispos=5,
        est_installee=True,
        permet_retour=True,
        permet_emprunt=True
    )


def create_empty_status(date):
    return StationStatus(
        id_station="station_1",
        horodatage=date,
        nb_velos_dispos=0,
        nb_velos_elec_dispos=0,
        nb_places_dispos=10,
        est_installee=True,
        permet_retour=True,
        permet_emprunt=False
    )


def create_saturated_status(date):
    return StationStatus(
        id_station="station_1",
        horodatage=date,
        nb_velos_dispos=10,
        nb_velos_elec_dispos=3,
        nb_places_dispos=0,
        est_installee=True,
        permet_retour=False,
        permet_emprunt=True
    )

# Déclaration de la dépendance au DAO pour le mock
@patch("service.fiabilite_service.StationStatusDao")
def test_percent_time_empty_all(mock_dao):

    # Arrange : préparation des données
    start = datetime(2026, 1, 1, 8, 0)
    # Creation d'un historique jouet pour nos tests
    history = [
        create_normal_status(start),
        create_empty_status(start + timedelta(hours=1)),
        create_empty_status(start + timedelta(hours=2)),
        create_normal_status(start + timedelta(hours=3)),
        create_saturated_status(start + timedelta(hours=4)),
        create_saturated_status(start + timedelta(hours=5)),
        create_normal_status(start + timedelta(hours=6))
    ]
    # Quand on appelle la fonction find_all_history de la DAO
    # On remplace la valeur retournée par notre history créé
    mock_dao.return_value.find_all_history.return_value = history

    # Act : exécution de la méthode
    service = ReliabilityService()
    result = service.percent_time_empty_all("station_1")

    # Assert : vérification du résultat
    assert result == 1 / 3


@patch("service.fiabilite_service.StationStatusDao")
def test_percent_time_empty_until(mock_dao):

    # Arrange : préparation des données
    start = datetime(2026, 1, 1, 8, 0)
    end = start + timedelta(hours=4)

    history = [
        create_normal_status(start),
        create_empty_status(start + timedelta(hours=1)),
        create_empty_status(start + timedelta(hours=2)),
        create_normal_status(start + timedelta(hours=3)),
        create_saturated_status(start + timedelta(hours=4))
    ]

    mock_dao.return_value.find_history_until.return_value = history

    # Act : exécution de la méthode
    service = ReliabilityService()
    result = service.percent_time_empty_until("station_1", end)

    # Assert : vérification du résultat
    assert result == 0.5

@patch("service.fiabilite_service.StationStatusDao")
def test_average_empty_duration_all(mock_dao):

    # Arrange
    start = datetime(2026, 1, 1, 8, 0)

    history = [
        create_normal_status(start),
        create_empty_status(start + timedelta(hours=1)),
        create_normal_status(start + timedelta(hours=3)),
        create_empty_status(start + timedelta(hours=4)),
        create_empty_status(start + timedelta(hours=7))
    ]

    mock_dao.return_value.find_all_history.return_value = history

    # Act
    service = ReliabilityService()
    result = service.average_empty_duration_all("station_1")

    # Assert
    assert result == 2.5

@patch("service.fiabilite_service.StationStatusDao")
def test_average_saturated_duration_all(mock_dao):

    # Arrange
    start = datetime(2026, 1, 1, 8, 0)

    history = [
        create_normal_status(start),
        create_saturated_status(start + timedelta(hours=1)),
        create_normal_status(start + timedelta(hours=3)),
        create_saturated_status(start + timedelta(hours=4)),
        create_saturated_status(start + timedelta(hours=7))
    ]

    mock_dao.return_value.find_all_history.return_value = history

    # Act
    service = ReliabilityService()
    result = service.average_saturated_duration_all("station_1")

    # Assert
    assert result == 2.5

@patch("service.fiabilite_service.StationStatusDao")
def test_average_empty_duration_until(mock_dao):

    # Arrange
    start = datetime(2026, 1, 1, 8, 0)
    end = start + timedelta(hours=7)

    history = [
        create_normal_status(start),
        create_empty_status(start + timedelta(hours=1)),
        create_normal_status(start + timedelta(hours=3)),
        create_empty_status(start + timedelta(hours=4)),
        create_empty_status(end)
    ]

    mock_dao.return_value.find_history_until.return_value = history

    # Act
    service = ReliabilityService()
    result = service.average_empty_duration_until("station_1", end)

    # Assert
    assert result == 2.5

@patch("service.fiabilite_service.StationStatusDao")
def test_average_saturated_duration_until(mock_dao):

    # Arrange
    start = datetime(2026, 1, 1, 8, 0)
    end = start + timedelta(hours=7)

    history = [
        create_normal_status(start),
        create_saturated_status(start + timedelta(hours=1)),
        create_normal_status(start + timedelta(hours=3)),
        create_saturated_status(start + timedelta(hours=4)),
        create_saturated_status(end)
    ]

    mock_dao.return_value.find_history_until.return_value = history

    # Act
    service = ReliabilityService()
    result = service.average_saturated_duration_until("station_1", end)

    # Assert
    assert result == 2.5

@patch("service.fiabilite_service.StationStatusDao")
def test_average_empty_duration_all_no_history(mock_dao):

    mock_dao.return_value.find_all_history.return_value = []

    service = ReliabilityService()

    assert service.average_empty_duration_all("station_1") is None


@patch("service.fiabilite_service.StationStatusDao")
def test_average_empty_duration_all_no_episode(mock_dao):

    start = datetime(2026, 1, 1, 8, 0)

    history = [
        create_normal_status(start),
        create_normal_status(start + timedelta(hours=2))
    ]

    mock_dao.return_value.find_all_history.return_value = history

    service = ReliabilityService()

    assert service.average_empty_duration_all("station_1") == 0.0

@patch("service.fiabilite_service.StationStatusDao")
def test_reliability_current_score(mock_dao):

    # Arrange
    start = datetime(2026, 1, 1, 8, 0)

    history = [
        create_normal_status(start),
        create_normal_status(start + timedelta(hours=2))
    ]

    mock_dao.return_value.find_all_history.return_value = history
    mock_dao.return_value.find_current_status.return_value = create_normal_status(
        start + timedelta(hours=2)
    )

    service = ReliabilityService()

    # On remplace les méthodes déjà testées par des résultats connus
    with patch.object(service, "percent_time_empty_all", return_value=0.1), \
         patch.object(service, "percent_saturation_all", return_value=0.2), \
         patch.object(service, "average_empty_duration_all", return_value=0.5), \
         patch.object(service, "average_saturated_duration_all", return_value=1.0):

        # Act
        result = service.reliability_current_score("station_1")

    # Assert
    assert result == 0.79

@patch("service.fiabilite_service.StationStatusDao")
def test_reliability_current_score_no_history(mock_dao):

    mock_dao.return_value.find_all_history.return_value = []

    service = ReliabilityService()

    result = service.reliability_current_score("station_1")

    assert result == 0.0

@patch("service.fiabilite_service.StationStatusDao")
def test_reliability_score_evolution(mock_dao):

    # Arrange
    start = datetime(2026, 1, 1, 8, 0)
    end = start + timedelta(hours=2)

    history = [
        create_normal_status(start),
        create_normal_status(end)
    ]

    mock_dao.return_value.find_all_history.return_value = history

    service = ReliabilityService()

    with patch.object(service, "percent_time_empty_until", return_value=0.25), \
         patch.object(service, "percent_saturation_until", return_value=0.5), \
         patch.object(service, "average_empty_duration_until", return_value=0.5), \
         patch.object(service, "average_saturated_duration_until", return_value=1.0):

        # Act
        result = service.reliability_score_evolution("station_1")

    # Assert
    assert result == {
        start: 0.0,
        end: 0.7
    }

@patch("service.fiabilite_service.StationStatusDao")
def test_reliability_score_evolution_no_history(mock_dao):

    mock_dao.return_value.find_all_history.return_value = []

    service = ReliabilityService()

    result = service.reliability_score_evolution("station_1")

    assert result == {}
