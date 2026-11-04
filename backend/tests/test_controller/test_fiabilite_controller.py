from datetime import datetime
from unittest.mock import MagicMock

from controller.fiabilite_controller import get_station_reliability


def test_get_station_reliability():

    # Arrange
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

    # Act
    result = get_station_reliability("station_1", service)

    # Assert : vérification des résultats
    assert result.station_id == "station_1"
    assert result.current_score == 0.85
    assert result.empty_percentage == 0.15
    assert result.saturation_percentage == 0.10
    assert result.average_empty_duration == 1.5
    assert result.average_saturated_duration == 0.8

    # Vérification de la transformation du dictionnaire en liste
    assert len(result.score_evolution) == 2
    assert result.score_evolution[0].date == date1
    assert result.score_evolution[0].score == 0.72
    assert result.score_evolution[1].date == date2
    assert result.score_evolution[1].score == 0.85

    # Vérification des appels au service
    service.reliability_current_score.assert_called_once_with("station_1")
    service.reliability_score_evolution.assert_called_once_with("station_1")
    service.percent_time_empty_all.assert_called_once_with("station_1")
    service.percent_saturation_all.assert_called_once_with("station_1")
    service.average_empty_duration_all.assert_called_once_with("station_1")
    service.average_saturated_duration_all.assert_called_once_with("station_1")


def test_get_station_reliability_no_history():

    # Arrange
    service = MagicMock()

    service.reliability_current_score.return_value = 0.0
    service.reliability_score_evolution.return_value = {}
    service.percent_time_empty_all.return_value = 0.0
    service.percent_saturation_all.return_value = 0.0
    service.average_empty_duration_all.return_value = None
    service.average_saturated_duration_all.return_value = None

    # Act
    result = get_station_reliability("station_1", service)

    # Assert
    assert result.station_id == "station_1"
    assert result.current_score == 0.0
    assert result.score_evolution == []
    assert result.empty_percentage == 0.0
    assert result.saturation_percentage == 0.0
    assert result.average_empty_duration is None
    assert result.average_saturated_duration is None